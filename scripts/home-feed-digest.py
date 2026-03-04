#!/usr/bin/env python3
"""
Home Feed Digest — Curated digest of top tweets from your home timeline.

Pulls home feed, scores by engagement, categorizes by topic, filters noise,
and sends a clean digest to Telegram.

Usage:
  python3 home-feed-digest.py              # Dry run
  python3 home-feed-digest.py --send       # Send to Telegram
  python3 home-feed-digest.py --top 15     # More results
  python3 home-feed-digest.py --min-engagement 100

Cron: 0 14,18,23 * * * (3x daily — 9AM, 1PM, 6PM ET)
"""

import sys, re, argparse, sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.bird import (
    bird_home, normalize_tweet, send_telegram, log,
    BirdError,
)

LOG_FILE = "/root/.openclaw/workspace/logs/home-feed-digest.log"
DB_PATH = "/root/.openclaw/memory/main.sqlite"

# Topic categories with keyword patterns
CATEGORIES = {
    "🤖 Tech/AI": [
        "ai", "gpt", "claude", "gemini", "llm", "machine learning", "deep learning",
        "neural", "transformer", "openai", "anthropic", "cursor", "copilot",
        "agent", "mcp", "model context", "vibe coding", "prompt",
    ],
    "🏗️ Build in Public": [
        "shipped", "launched", "deployed", "building in public", "indie hacker",
        "saas", "mrr", "revenue", "startup", "side project", "maker",
    ],
    "🔥 Hot Takes": [
        "unpopular opinion", "hot take", "overrated", "underrated", "controversial",
        "disagree", "rant", "thread", "🧵",
    ],
    "💰 Business": [
        "revenue", "funding", "raised", "valuation", "profit", "growth",
        "customer", "pricing", "monetize", "freelance", "client",
    ],
}


def ensure_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feed_digest_seen (
            tweet_id TEXT PRIMARY KEY,
            seen_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_seen_ids() -> set:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT tweet_id FROM feed_digest_seen").fetchall()
    conn.close()
    return {r[0] for r in rows}


def mark_seen(tweet_ids: list):
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now().isoformat()
    for tid in tweet_ids:
        conn.execute("INSERT OR IGNORE INTO feed_digest_seen (tweet_id, seen_at) VALUES (?, ?)", (tid, now))
    conn.commit()
    conn.close()

    # Cleanup old entries (keep last 7 days)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM feed_digest_seen WHERE seen_at < datetime('now', '-7 days')")
    conn.commit()
    conn.close()


def categorize(tweet: dict) -> str:
    """Assign a category based on tweet text."""
    text_lower = tweet["text"].lower()
    for category, keywords in CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return "📌 Other"


def is_noise(tweet: dict) -> bool:
    """Filter out low-quality content."""
    text = tweet["text"]
    # Skip retweets
    if text.startswith("RT @"):
        return True
    # Skip super short tweets (likely ads or low effort)
    if len(text) < 30:
        return True
    # Skip tweets that are mostly hashtags/mentions
    words = text.split()
    special = sum(1 for w in words if w.startswith(("#", "@", "http")))
    if len(words) > 0 and special / len(words) > 0.6:
        return True
    return False


def format_digest(categorized: dict, total_scanned: int, top_n: int = 10) -> str:
    """Format the digest for Telegram."""
    now = datetime.now().strftime("%I:%M %p ET")
    lines = [f"📰 *HOME FEED DIGEST* — Top posts right now ({now})\n"]

    count = 0
    for category, tweets in categorized.items():
        if not tweets or count >= top_n:
            break
        lines.append(f"\n{category}")
        for t in tweets:
            if count >= top_n:
                break
            text_preview = t["text"][:100].replace("\n", " ")
            if len(t["text"]) > 100:
                text_preview += "..."
            engagement = t["likes"] + t["retweets"] * 2 + t["bookmarks"] * 3

            age = f"{t['age_hours']}h ago" if t['age_hours'] < 24 else f"{int(t['age_hours']/24)}d ago"

            lines.append(
                f"  {count+1}. @{t['username']}: \"{text_preview}\"\n"
                f"     ❤️ {t['likes']:,} | 🔁 {t['retweets']} | 🔖 {t['bookmarks']} | {age}\n"
            )
            count += 1

    lines.append(f"\n📊 Scanned {total_scanned} tweets from home feed")
    return "\n".join(lines)


def main():
    # DISABLED: Bird CLI removed while account suspended
    # All functionality depends on Bird CLI (bird_home).
    # Re-enable when @xBenJamminx suspension is resolved.
    print("[DISABLED] Home Feed Digest disabled — Bird CLI suspended")
    return

    parser = argparse.ArgumentParser(description="Home Feed Digest")
    parser.add_argument("--send", action="store_true", help="Send to Telegram")
    parser.add_argument("--top", type=int, default=10, help="Show top N (default: 10)")
    parser.add_argument("--min-engagement", type=int, default=50, help="Min engagement score (default: 50)")
    parser.add_argument("--account", type=str, default="ben", help="Bird CLI account")
    args = parser.parse_args()

    ensure_table()
    seen_ids = get_seen_ids()

    log("Fetching home feed...", LOG_FILE)
    try:
        raw = bird_home(n=100, account=args.account)
        tweets = [normalize_tweet(t) for t in raw]
        log(f"Got {len(tweets)} tweets from home feed", LOG_FILE)
    except BirdError as e:
        log(f"❌ Failed to fetch home feed: {e}", LOG_FILE)
        return

    # Filter
    filtered = [
        t for t in tweets
        if not is_noise(t)
        and t["id"] not in seen_ids
    ]

    # Score by weighted engagement
    for t in filtered:
        t["engagement_score"] = t["likes"] + t["retweets"] * 2 + t["bookmarks"] * 3

    # Filter by min engagement
    filtered = [t for t in filtered if t["engagement_score"] >= args.min_engagement]
    filtered.sort(key=lambda t: t["engagement_score"], reverse=True)

    log(f"📊 {len(filtered)} tweets pass filters (engagement ≥{args.min_engagement})", LOG_FILE)

    # Categorize
    categorized = {}
    for t in filtered:
        cat = categorize(t)
        categorized.setdefault(cat, []).append(t)

    # Sort categories by total engagement
    categorized = dict(
        sorted(categorized.items(), key=lambda kv: sum(t["engagement_score"] for t in kv[1]), reverse=True)
    )

    output = format_digest(categorized, total_scanned=len(tweets), top_n=args.top)
    print(f"\n{output}")

    if args.send and filtered:
        send_telegram(output)

    # Mark top tweets as seen
    if filtered:
        mark_seen([t["id"] for t in filtered[:args.top]])


if __name__ == "__main__":
    main()
