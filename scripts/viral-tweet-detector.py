#!/usr/bin/env python3
"""
Viral Tweet Detector — Catches tweets gaining traction before they blow up.

Searches niche queries, computes engagement velocity (likes/hour), and flags
tweets that are accelerating but haven't peaked yet. Sends alerts to Telegram.

Usage:
  python3 viral-tweet-detector.py              # Dry run
  python3 viral-tweet-detector.py --send       # Send to Telegram
  python3 viral-tweet-detector.py --since 3    # Look back 3 hours
  python3 viral-tweet-detector.py --min-velocity 30 --top 5

Cron: 0 */2 * * * (every 2 hours)
"""

import sys, time, argparse, sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.bird import (
    bird_search, normalize_tweet, send_telegram, log,
    BirdRateLimited, BirdError, retry_on_rate_limit,
)

LOG_FILE = "/root/.openclaw/workspace/logs/viral-detector.log"
DB_PATH = "/root/.openclaw/memory/main.sqlite"

# Broader than reply-radar — we want to catch anything going viral in the niche
VIRAL_QUERIES = [
    '"claude code" -is:retweet lang:en',
    '"ai agent" build OR ship OR launch -is:retweet lang:en',
    '"vibe coding" -is:retweet lang:en',
    '"mcp server" OR "model context protocol" -is:retweet lang:en',
    '"cursor ai" OR windsurf ship OR build -is:retweet lang:en',
    '"building in public" AI OR tool -is:retweet lang:en',
    '"just shipped" AI OR app -is:retweet lang:en',
    'solopreneur AI automation -is:retweet lang:en',
    '"ai automation" workflow -is:retweet lang:en',
    '"open source" AI tool launch -is:retweet lang:en',
    'indie hacker AI revenue -is:retweet lang:en',
    '"no code" AI tool shipped -is:retweet lang:en',
]


def ensure_table():
    """Create seen_viral_tweets table if not exists."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_viral_tweets (
            tweet_id TEXT PRIMARY KEY,
            username TEXT,
            velocity REAL,
            likes INTEGER,
            first_seen TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_seen_ids() -> set:
    """Load already-alerted tweet IDs."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT tweet_id FROM seen_viral_tweets").fetchall()
    conn.close()
    return {r[0] for r in rows}


def mark_seen(tweets: list):
    """Store tweet IDs so we don't re-alert."""
    conn = sqlite3.connect(DB_PATH)
    for t in tweets:
        conn.execute(
            "INSERT OR IGNORE INTO seen_viral_tweets (tweet_id, username, velocity, likes, first_seen) "
            "VALUES (?, ?, ?, ?, ?)",
            (t["id"], t["username"], t["velocity"], t["likes"], datetime.now().isoformat())
        )
    conn.commit()
    conn.close()


def format_viral(tweets: list, top_n: int = 10) -> str:
    """Format viral tweet alert for Telegram."""
    if not tweets:
        return "No viral tweets detected this cycle."

    lines = [f"🔥 *VIRAL DETECTOR* — {len(tweets[:top_n])} tweets gaining traction\n"]

    for i, t in enumerate(tweets[:top_n], 1):
        text_preview = t["text"][:140].replace("\n", " ")
        if len(t["text"]) > 140:
            text_preview += "..."

        lines.append(
            f"*{i}. @{t['username']}* ({t['followers']:,} followers)\n"
            f"   \"{text_preview}\"\n"
            f"   ❤️ {t['likes']} in {t['age_hours']}h ({t['velocity']}/hr velocity) | 🔁 {t['retweets']}\n"
            f"   {t['url']}\n"
        )

    return "\n".join(lines)


def main():
    # DISABLED: Bird CLI removed while account suspended
    # All functionality depends on Bird CLI (bird_search).
    # Re-enable when @xBenJamminx suspension is resolved.
    print("[DISABLED] Viral Tweet Detector disabled — Bird CLI suspended")
    return

    parser = argparse.ArgumentParser(description="Viral Tweet Detector")
    parser.add_argument("--send", action="store_true", help="Send to Telegram")
    parser.add_argument("--since", type=int, default=6, help="Hours to look back (default: 6)")
    parser.add_argument("--min-velocity", type=float, default=20, help="Min likes/hr to flag (default: 20)")
    parser.add_argument("--max-likes", type=int, default=500, help="Max likes (catching early, default: 500)")
    parser.add_argument("--top", type=int, default=10, help="Show top N (default: 10)")
    parser.add_argument("--account", type=str, default="ben", help="Bird CLI account")
    args = parser.parse_args()

    ensure_table()
    seen_ids = get_seen_ids()

    all_tweets = []

    for i, query in enumerate(VIRAL_QUERIES, 1):
        log(f"[{i}/{len(VIRAL_QUERIES)}] Searching: {query[:60]}...", LOG_FILE)

        try:
            raw = retry_on_rate_limit(
                lambda q=query: bird_search(q, n=30, account=args.account)
            )
            tweets = [normalize_tweet(t) for t in raw]
            log(f"  → {len(tweets)} results", LOG_FILE)
            all_tweets.extend(tweets)
        except BirdError as e:
            log(f"  ⚠️ Failed: {e}", LOG_FILE)

        time.sleep(1.5)

    # Dedupe
    seen = set()
    unique = []
    for t in all_tweets:
        if t["id"] not in seen:
            seen.add(t["id"])
            unique.append(t)

    log(f"📊 {len(all_tweets)} raw → {len(unique)} unique", LOG_FILE)

    # Filter for viral criteria
    viral = [
        t for t in unique
        if t["velocity"] >= args.min_velocity
        and t["likes"] <= args.max_likes
        and t["age_hours"] <= args.since
        and t["id"] not in seen_ids
    ]

    viral.sort(key=lambda t: t["velocity"], reverse=True)
    log(f"🔥 {len(viral)} viral tweets (velocity ≥{args.min_velocity}/hr, likes ≤{args.max_likes})", LOG_FILE)

    output = format_viral(viral, top_n=args.top)
    print(f"\n{output}")

    if args.send and viral:
        send_telegram(output)

    # Mark all flagged tweets as seen
    if viral:
        mark_seen(viral[:args.top])


if __name__ == "__main__":
    main()
