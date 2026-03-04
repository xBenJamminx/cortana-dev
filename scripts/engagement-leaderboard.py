#!/usr/bin/env python3
"""
Engagement Leaderboard — Weekly performance report for your tweets.

Pulls recent tweets, ranks by engagement, compares with last week,
identifies best performing content types and posting times.

Usage:
  python3 engagement-leaderboard.py                    # Dry run
  python3 engagement-leaderboard.py --send             # Send to Telegram
  python3 engagement-leaderboard.py --username xBenJamminx --period 7

Cron: 0 1 * * 1 (weekly Sunday 8PM ET)
"""

import sys, argparse, sqlite3
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.bird import (
    bird_user_tweets, normalize_tweet, send_telegram, log,
    BirdError,
)

LOG_FILE = "/root/.openclaw/workspace/logs/engagement-leaderboard.log"
DB_PATH = "/root/.openclaw/memory/main.sqlite"


def ensure_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS engagement_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            tweet_id TEXT,
            text TEXT,
            likes INTEGER,
            retweets INTEGER,
            replies INTEGER,
            bookmarks INTEGER,
            impressions INTEGER,
            engagement_score INTEGER,
            created_at TEXT,
            snapshot_date TEXT,
            UNIQUE(username, tweet_id, snapshot_date)
        )
    """)
    conn.commit()
    conn.close()


def save_snapshot(tweets: list, username: str):
    """Save tweet engagement data for historical comparison."""
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime("%Y-%m-%d")
    for t in tweets:
        score = t["likes"] + t["retweets"] * 2 + t["replies"] + t["bookmarks"] * 3
        conn.execute(
            "INSERT OR REPLACE INTO engagement_snapshots "
            "(username, tweet_id, text, likes, retweets, replies, bookmarks, impressions, "
            "engagement_score, created_at, snapshot_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (username, t["id"], t["text"][:280], t["likes"], t["retweets"],
             t["replies"], t["bookmarks"], t["impressions"], score,
             t["created_at"], today)
        )
    conn.commit()
    conn.close()


def get_last_week_stats(username: str) -> dict:
    """Get last week's snapshot for comparison."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT AVG(likes), AVG(retweets), AVG(replies), AVG(bookmarks), COUNT(*) "
        "FROM engagement_snapshots "
        "WHERE username = ? AND snapshot_date BETWEEN date('now', '-14 days') AND date('now', '-7 days')",
        (username,)
    ).fetchone()
    conn.close()

    if rows and rows[4] > 0:
        return {
            "avg_likes": round(rows[0], 1),
            "avg_retweets": round(rows[1], 1),
            "avg_replies": round(rows[2], 1),
            "avg_bookmarks": round(rows[3], 1),
            "count": rows[4],
        }
    return None


def pct_change(old: float, new: float) -> str:
    """Format percentage change."""
    if old == 0:
        return "N/A"
    change = ((new - old) / old) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.0f}%"


def format_leaderboard(tweets: list, username: str, last_week: dict, top_n: int = 5) -> str:
    """Format the weekly leaderboard for Telegram."""
    if not tweets:
        return "No tweets found for the period."

    now = datetime.now()
    week_start = (now - timedelta(days=7)).strftime("%b %d")
    week_end = now.strftime("%b %d")

    # This week's stats
    avg_likes = sum(t["likes"] for t in tweets) / len(tweets) if tweets else 0
    avg_rts = sum(t["retweets"] for t in tweets) / len(tweets) if tweets else 0
    avg_replies = sum(t["replies"] for t in tweets) / len(tweets) if tweets else 0

    lines = [f"🏆 *ENGAGEMENT LEADERBOARD* — Week of {week_start}–{week_end}\n"]

    # Summary stats
    lines.append(f"📈 This Week: {len(tweets)} tweets | Avg ❤️ {avg_likes:.1f} | Avg 🔁 {avg_rts:.1f}")

    if last_week:
        lines.append(
            f"📉 Last Week: {last_week['count']} tweets | "
            f"Avg ❤️ {last_week['avg_likes']:.1f} | Avg 🔁 {last_week['avg_retweets']:.1f}"
        )
        lines.append(
            f"🔥 {pct_change(last_week['avg_likes'], avg_likes)} likes, "
            f"{pct_change(last_week['avg_retweets'], avg_rts)} retweets week-over-week"
        )
    else:
        lines.append("📉 Last Week: No data (first snapshot)")

    # Top posts
    lines.append(f"\n*Top {min(top_n, len(tweets))} Posts:*")
    sorted_tweets = sorted(tweets, key=lambda t: t["likes"] + t["retweets"] * 2 + t["bookmarks"] * 3, reverse=True)

    for i, t in enumerate(sorted_tweets[:top_n], 1):
        text_preview = t["text"][:80].replace("\n", " ")
        if len(t["text"]) > 80:
            text_preview += "..."
        lines.append(
            f"{i}. \"{text_preview}\"\n"
            f"   ❤️ {t['likes']}, 🔁 {t['retweets']}, 💬 {t['replies']}, 🔖 {t['bookmarks']}"
        )

    # Best posting time (simple hour analysis)
    hour_engagement = {}
    for t in tweets:
        if t["created_at"]:
            try:
                from lib.bird import _parse_iso, _parse_twitter_format
                dt = _parse_iso(t["created_at"]) or _parse_twitter_format(t["created_at"])
                if dt:
                    hour = dt.hour
                    score = t["likes"] + t["retweets"] * 2
                    hour_engagement.setdefault(hour, []).append(score)
            except:
                pass

    if hour_engagement:
        avg_by_hour = {h: sum(s)/len(s) for h, s in hour_engagement.items()}
        best_hour = max(avg_by_hour, key=avg_by_hour.get)
        # Convert UTC hour to ET (approximate)
        et_hour = (best_hour - 5) % 24
        period = "AM" if et_hour < 12 else "PM"
        display_hour = et_hour if et_hour <= 12 else et_hour - 12
        if display_hour == 0:
            display_hour = 12
        lines.append(f"\n⏰ Best time: ~{display_hour}{period} ET ({avg_by_hour[best_hour]:.0f} avg engagement)")

    return "\n".join(lines)


def main():
    # DISABLED: Bird CLI removed while account suspended
    # All functionality depends on Bird CLI (bird_user_tweets).
    # Re-enable when @xBenJamminx suspension is resolved.
    print("[DISABLED] Engagement Leaderboard disabled — Bird CLI suspended")
    return

    parser = argparse.ArgumentParser(description="Engagement Leaderboard")
    parser.add_argument("--send", action="store_true", help="Send to Telegram")
    parser.add_argument("--username", type=str, default="xBenJamminx", help="Twitter username")
    parser.add_argument("--period", type=int, default=7, help="Days to analyze (default: 7)")
    parser.add_argument("--top", type=int, default=5, help="Top N posts (default: 5)")
    parser.add_argument("--account", type=str, default="ben", help="Bird CLI account")
    args = parser.parse_args()

    ensure_table()

    log(f"Fetching tweets for @{args.username}...", LOG_FILE)
    try:
        raw = bird_user_tweets(args.username, n=50, account=args.account)
        tweets = [normalize_tweet(t) for t in raw]
        log(f"Got {len(tweets)} tweets", LOG_FILE)
    except BirdError as e:
        log(f"❌ Failed: {e}", LOG_FILE)
        return

    # Filter to recent period
    cutoff_hours = args.period * 24
    recent = [t for t in tweets if t["age_hours"] <= cutoff_hours]
    log(f"📊 {len(recent)} tweets in last {args.period} days", LOG_FILE)

    # Get last week for comparison
    last_week = get_last_week_stats(args.username)

    # Save this week's snapshot
    save_snapshot(recent, args.username)

    output = format_leaderboard(recent, args.username, last_week, top_n=args.top)
    print(f"\n{output}")

    if args.send:
        send_telegram(output)


if __name__ == "__main__":
    main()
