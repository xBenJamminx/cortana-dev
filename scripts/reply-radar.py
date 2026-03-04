#!/usr/bin/env python3
"""
Reply Radar — Aggregated multi-query search for reply-guy targets.

Runs a curated list of queries across content pillars via Bird CLI,
deduplicates, scores by engagement velocity, and surfaces the best
opportunities in one feed.

Usage:
  python3 reply-radar.py                  # Run with defaults
  python3 reply-radar.py --send           # Run + send results to Telegram
  python3 reply-radar.py --pillars ai,build  # Filter to specific pillars
  python3 reply-radar.py --since 3h       # Override time window (default: 6h)
  python3 reply-radar.py --min-followers 5000
  python3 reply-radar.py --min-likes 10
  python3 reply-radar.py --top 15         # Show top N results
"""

import sys, time, argparse, math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.bird import (
    bird_search, normalize_tweet, send_telegram, log,
    BirdRateLimited, BirdError, retry_on_rate_limit,
)

LOG_FILE = "/root/.openclaw/workspace/logs/reply-radar.log"

# ── Search Queries by Content Pillar ─────────────────────────────────────

SEARCH_QUERIES = {
    "ai_tools": [
        '"claude code" OR "cursor ai" OR "windsurf" -is:retweet lang:en',
        '"ai agent" OR "ai agents" build OR built OR shipping -is:retweet lang:en',
        '"mcp server" OR "model context protocol" -is:retweet lang:en',
        '"vibe coding" OR "vibe code" -is:retweet lang:en',
    ],
    "build_in_public": [
        '"building in public" shipped OR launched OR update -is:retweet lang:en',
        '"just shipped" OR "just launched" OR "just deployed" AI OR app OR tool -is:retweet lang:en',
        '"indie hacker" revenue OR MRR OR launched -is:retweet lang:en',
    ],
    "solopreneur": [
        'solopreneur OR "one person business" AI OR automation -is:retweet lang:en',
        '"quit my job" build OR startup OR AI -is:retweet lang:en',
        '"side project" OR "weekend project" AI OR shipped OR live -is:retweet lang:en',
    ],
    "ai_workflow": [
        '"ai automation" OR "ai workflow" no-code OR zapier OR make -is:retweet lang:en',
        '"prompt engineering" OR "system prompt" tip OR trick -is:retweet lang:en',
    ],
    "hot_takes": [
        '"unpopular opinion" OR "hot take" AI OR coding OR developer -is:retweet lang:en',
        '"overrated" OR "underrated" AI OR tool OR framework -is:retweet lang:en',
    ],
}


def dedupe(tweets: list) -> list:
    """Deduplicate by tweet ID."""
    seen = set()
    out = []
    for t in tweets:
        if t["id"] not in seen:
            seen.add(t["id"])
            out.append(t)
    return out


def score_and_rank(tweets: list, min_followers: int = 5000,
                   min_likes: int = 10, max_age_hours: int = 3) -> list:
    """Filter and score tweets for reply-guy potential.

    Key insight: we want FRESH posts that are ACTIVELY gaining steam.
    A 9-hour-old post with 200 likes is stale — a 30-min-old post with
    20 likes from a 50K account is a reply-guy goldmine.
    """
    filtered = [
        t for t in tweets
        if t["followers"] >= min_followers
        and t["likes"] >= min_likes
        and t["age_hours"] <= max_age_hours
    ]

    for t in filtered:
        follower_boost = math.log10(max(t["followers"], 10))
        freshness_bonus = 2.0 if t["age_hours"] <= 1.0 else 1.0
        t["score"] = round(t["velocity"] * follower_boost * freshness_bonus, 2)

    return sorted(filtered, key=lambda t: t["score"], reverse=True)


def format_results(tweets: list, top_n: int = 10) -> str:
    """Format results for display / Telegram."""
    if not tweets:
        return "No results found matching the criteria."

    lines = ["🎯 *REPLY RADAR* — Top targets right now\n"]

    for i, t in enumerate(tweets[:top_n], 1):
        text_preview = t["text"][:120].replace("\n", " ")
        if len(t["text"]) > 120:
            text_preview += "..."

        lines.append(
            f"*{i}. @{t['username']}* ({t['followers']:,} followers)\n"
            f"   {text_preview}\n"
            f"   ❤️ {t['likes']} | 🔁 {t['retweets']} | 💬 {t['replies']} | "
            f"⏱️ {t['age_hours']}h ago | 🔥 velocity: {t['velocity']}/hr\n"
            f"   {t['url']}\n"
        )

    lines.append(f"\n📊 Scanned {len(tweets)} tweets total | Showing top {min(top_n, len(tweets))}")
    return "\n".join(lines)


def main():
    # DISABLED: Bird CLI removed while account suspended
    # All functionality depends on Bird CLI (bird_search).
    # Re-enable when @xBenJamminx suspension is resolved.
    print("[DISABLED] Reply Radar disabled — Bird CLI suspended")
    return

    parser = argparse.ArgumentParser(description="Reply Radar — aggregated reply-guy target finder")
    parser.add_argument("--send", action="store_true", help="Send results to Telegram")
    parser.add_argument("--pillars", type=str, default="all", help="Comma-separated pillar names (default: all)")
    parser.add_argument("--since", type=int, default=6, help="Hours to look back (default: 6)")
    parser.add_argument("--max-age", type=int, default=3, help="Max post age in hours (default: 3)")
    parser.add_argument("--min-followers", type=int, default=5000, help="Min follower count (default: 5000)")
    parser.add_argument("--min-likes", type=int, default=10, help="Min likes (default: 10)")
    parser.add_argument("--top", type=int, default=10, help="Show top N results (default: 10)")
    parser.add_argument("--account", type=str, default="ben", help="Bird CLI account (default: ben)")
    args = parser.parse_args()

    # Select pillars
    if args.pillars == "all":
        pillars = SEARCH_QUERIES
    else:
        selected = [p.strip() for p in args.pillars.split(",")]
        pillars = {k: v for k, v in SEARCH_QUERIES.items() if k in selected}
        if not pillars:
            print(f"❌ No matching pillars. Available: {', '.join(SEARCH_QUERIES.keys())}")
            sys.exit(1)

    # Run all searches
    all_tweets = []
    total_queries = sum(len(v) for v in pillars.values())
    query_num = 0

    for pillar, queries in pillars.items():
        log(f"📡 Pillar: {pillar}", LOG_FILE)
        for q in queries:
            query_num += 1
            log(f"  [{query_num}/{total_queries}] Searching: {q[:60]}...", LOG_FILE)

            try:
                raw_results = retry_on_rate_limit(
                    lambda q=q: bird_search(q, n=50, account=args.account)
                )
                tweets = [normalize_tweet(t) for t in raw_results]
                log(f"    → {len(tweets)} results", LOG_FILE)
                all_tweets.extend(tweets)
            except BirdError as e:
                log(f"    ⚠️ Search failed: {e}", LOG_FILE)

            time.sleep(1.5)  # Rate limit spacing

    # Dedupe
    unique = dedupe(all_tweets)
    log(f"📊 Total: {len(all_tweets)} raw → {len(unique)} unique tweets", LOG_FILE)

    # Score and rank
    ranked = score_and_rank(
        unique,
        min_followers=args.min_followers,
        min_likes=args.min_likes,
        max_age_hours=args.max_age,
    )
    log(f"🎯 {len(ranked)} tweets pass filters (≥{args.min_followers} followers, "
        f"≥{args.min_likes} likes, ≤{args.max_age}h old)", LOG_FILE)

    # Format
    output = format_results(ranked, top_n=args.top)
    print(f"\n{output}")

    # Send to Telegram if requested
    if args.send:
        send_telegram(output)


if __name__ == "__main__":
    main()
