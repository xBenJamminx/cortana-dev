#!/usr/bin/env python3
"""
Thread Analyzer — Finds viral threads and dissects their structure.

Searches for high-engagement threads, pulls full content via bird thread,
analyzes hook patterns, length, engagement drop-off, and structure.

Usage:
  python3 thread-analyzer.py                           # Scan for threads
  python3 thread-analyzer.py --query "ai agent"        # Custom search
  python3 thread-analyzer.py --min-likes 100 --send
  python3 thread-analyzer.py --analyze-top 5

Cron: 0 13 * * * (daily 8AM ET)
"""

import sys, time, argparse, re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.bird import (
    bird_search, bird_thread, normalize_tweet, send_telegram, log,
    BirdError, retry_on_rate_limit,
)

LOG_FILE = "/root/.openclaw/workspace/logs/thread-analyzer.log"
ANALYSIS_DIR = Path("/root/.openclaw/workspace/memory/thread-analyses")

# Thread search queries
THREAD_QUERIES = [
    '"🧵" AI OR agent OR code OR build -is:retweet lang:en',
    '"thread" AI tool OR framework OR agent -is:retweet lang:en',
    '"1/" AI OR coding OR automation -is:retweet lang:en',
    '"here\'s how" AI OR build OR ship -is:retweet lang:en',
    '"step by step" AI OR automation -is:retweet lang:en',
]

# Hook pattern classifications
HOOK_PATTERNS = {
    "Curiosity Gap": [
        r"here'?s (what|how|why)", r"most people don'?t",
        r"nobody talks about", r"secret", r"hidden",
    ],
    "Bold Claim": [
        r"will (change|replace|kill|destroy|transform)",
        r"the (best|worst|biggest|most)",
        r"stop (using|doing|building)",
    ],
    "Story": [
        r"^I (just|recently|finally)", r"last (week|month|year)",
        r"story time", r"true story",
    ],
    "List/How-To": [
        r"^\d+ (ways|tips|tools|steps|things|mistakes)",
        r"how (to|I)", r"step by step", r"guide",
    ],
    "Contrarian": [
        r"unpopular opinion", r"hot take", r"controversial",
        r"overrated", r"wrong about",
    ],
}


def classify_hook(text: str) -> str:
    """Classify the hook pattern of a thread's first tweet."""
    text_lower = text.lower()
    for pattern_name, regexes in HOOK_PATTERNS.items():
        for regex in regexes:
            if re.search(regex, text_lower):
                return pattern_name
    return "Direct Statement"


def analyze_thread(tweets: list) -> dict:
    """Analyze a thread's structure and engagement."""
    if not tweets:
        return {}

    first = tweets[0]
    hook_pattern = classify_hook(first["text"])

    # Engagement per tweet
    engagements = [t["likes"] + t["retweets"] for t in tweets]
    total_engagement = sum(t["likes"] for t in tweets)

    # Drop-off rate (engagement of last tweet vs first)
    if len(tweets) > 1 and engagements[0] > 0:
        dropoff = round((1 - engagements[-1] / engagements[0]) * 100)
    else:
        dropoff = 0

    # Detect structure
    structure_parts = []
    if len(tweets) >= 1:
        structure_parts.append("Hook")
    if len(tweets) >= 2:
        # Check if tweet 2 sets up a problem
        t2_lower = tweets[1]["text"].lower() if len(tweets) > 1 else ""
        if any(w in t2_lower for w in ["problem", "issue", "challenge", "but", "however"]):
            structure_parts.append("Problem")
        else:
            structure_parts.append("Context")
    if len(tweets) >= 3:
        # Middle is the meat
        middle_count = len(tweets) - 2
        structure_parts.append(f"{middle_count} Steps/Points")
    if len(tweets) >= 2:
        # Check last tweet for CTA
        last_lower = tweets[-1]["text"].lower()
        if any(w in last_lower for w in ["follow", "retweet", "like", "share", "dm", "link", "subscribe"]):
            structure_parts.append("CTA")
        else:
            structure_parts.append("Conclusion")

    return {
        "hook_text": first["text"][:120],
        "hook_pattern": hook_pattern,
        "thread_length": len(tweets),
        "total_likes": total_engagement,
        "dropoff_pct": dropoff,
        "structure": " → ".join(structure_parts),
        "username": first["username"],
        "url": first["url"],
        "tweets": tweets,
    }


def save_analysis(analysis: dict):
    """Save thread analysis as markdown."""
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r'[^a-z0-9]+', '-', analysis["hook_text"][:40].lower()).strip('-')
    date = datetime.now().strftime("%Y%m%d")
    filename = f"{analysis['username']}-{date}-{slug}.md"

    content = [
        f"# Thread by @{analysis['username']}",
        f"URL: {analysis['url']}",
        f"Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Hook Pattern: {analysis['hook_pattern']}",
        f"Length: {analysis['thread_length']} tweets",
        f"Total Likes: {analysis['total_likes']:,}",
        f"Drop-off: {analysis['dropoff_pct']}%",
        f"Structure: {analysis['structure']}",
        "---",
        "",
    ]

    for i, t in enumerate(analysis["tweets"], 1):
        content.append(f"{i}/ {t['text']}")
        content.append(f"   ❤️ {t['likes']} | 🔁 {t['retweets']}")
        content.append("")

    (ANALYSIS_DIR / filename).write_text("\n".join(content))
    log(f"  Saved: {filename}", LOG_FILE)


def format_analyses(analyses: list) -> str:
    """Format thread analyses for Telegram."""
    if not analyses:
        return "No viral threads found matching criteria."

    lines = [f"🧵 *THREAD ANALYZER* — {len(analyses)} viral threads dissected\n"]

    for i, a in enumerate(analyses, 1):
        hook_preview = a["hook_text"][:80]
        if len(a["hook_text"]) > 80:
            hook_preview += "..."

        lines.append(
            f"*{i}. @{a['username']}* — \"{hook_preview}\"\n"
            f"   📊 {a['thread_length']} tweets | ❤️ {a['total_likes']:,} total | Hook: {a['hook_pattern']}\n"
            f"   📉 Drop-off: -{a['dropoff_pct']}% by end\n"
            f"   🔑 Structure: {a['structure']}\n"
            f"   {a['url']}\n"
        )

    return "\n".join(lines)


def main():
    # DISABLED: Bird CLI removed while account suspended
    # All functionality in this script depends on Bird CLI (bird_search, bird_thread).
    # Re-enable when @xBenJamminx suspension is resolved.
    print("[DISABLED] Thread Analyzer disabled — Bird CLI suspended")
    return

    parser = argparse.ArgumentParser(description="Thread Analyzer")
    parser.add_argument("--send", action="store_true", help="Send to Telegram")
    parser.add_argument("--query", type=str, default=None, help="Custom search query")
    parser.add_argument("--min-likes", type=int, default=100, help="Min likes for thread (default: 100)")
    parser.add_argument("--analyze-top", type=int, default=5, help="Analyze top N threads (default: 5)")
    parser.add_argument("--account", type=str, default="ben", help="Bird CLI account")
    args = parser.parse_args()

    # Build queries
    queries = [args.query] if args.query else THREAD_QUERIES

    all_tweets = []
    for i, q in enumerate(queries, 1):
        log(f"[{i}/{len(queries)}] Searching: {q[:60]}...", LOG_FILE)
        try:
            raw = retry_on_rate_limit(
                lambda q=q: bird_search(q, n=30, account=args.account)
            )
            tweets = [normalize_tweet(t) for t in raw]
            log(f"  → {len(tweets)} results", LOG_FILE)
            all_tweets.extend(tweets)
        except BirdError as e:
            log(f"  ⚠️ Failed: {e}", LOG_FILE)
        time.sleep(1.5)

    # Dedupe and filter high-engagement
    seen = set()
    candidates = []
    for t in all_tweets:
        if t["id"] not in seen and t["likes"] >= args.min_likes:
            seen.add(t["id"])
            candidates.append(t)

    candidates.sort(key=lambda t: t["likes"], reverse=True)
    log(f"📊 {len(candidates)} thread candidates with ≥{args.min_likes} likes", LOG_FILE)

    # Pull and analyze full threads
    analyses = []
    for t in candidates[:args.analyze_top]:
        log(f"Analyzing thread by @{t['username']} ({t['likes']} likes)...", LOG_FILE)
        try:
            raw_thread = retry_on_rate_limit(
                lambda tid=t["id"]: bird_thread(tid, account=args.account)
            )
            thread_tweets = [normalize_tweet(tt) for tt in raw_thread]

            if len(thread_tweets) < 2:
                log(f"  Skipping — only {len(thread_tweets)} tweet(s)", LOG_FILE)
                continue

            analysis = analyze_thread(thread_tweets)
            if analysis:
                analyses.append(analysis)
                save_analysis(analysis)

            time.sleep(2)
        except BirdError as e:
            log(f"  ⚠️ Failed to fetch thread: {e}", LOG_FILE)

    output = format_analyses(analyses)
    print(f"\n{output}")

    if args.send and analyses:
        send_telegram(output)


if __name__ == "__main__":
    main()
