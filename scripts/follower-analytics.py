#!/usr/bin/env python3
"""
Follower Analytics — Daily follower count tracking with trend analysis.

Takes a daily snapshot of follower/following counts, calculates deltas,
and optionally diffs follower lists to identify new follows/unfollows.

Usage:
  python3 follower-analytics.py                    # Dry run
  python3 follower-analytics.py --send             # Send to Telegram
  python3 follower-analytics.py --detailed         # Include follower list diff

Cron: 0 2 * * * (daily 9PM ET)
"""

import sys, argparse, sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.bird import (
    bird_about, bird_followers, normalize_tweet, send_telegram, log,
    BirdError,
)

LOG_FILE = "/root/.openclaw/workspace/logs/follower-analytics.log"
DB_PATH = "/root/.openclaw/memory/main.sqlite"


def ensure_tables():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS follower_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            username TEXT,
            followers INTEGER,
            following INTEGER,
            UNIQUE(date, username)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS follower_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            username TEXT,
            follower_username TEXT,
            follower_name TEXT,
            follower_count INTEGER,
            follower_bio TEXT,
            UNIQUE(date, username, follower_username)
        )
    """)
    conn.commit()
    conn.close()


def save_snapshot(username: str, followers: int, following: int):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO follower_snapshots (date, username, followers, following) VALUES (?, ?, ?, ?)",
        (today, username, followers, following)
    )
    conn.commit()
    conn.close()


def get_trend(username: str, days: int) -> dict:
    """Get follower count from N days ago for trend calculation."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT followers, following FROM follower_snapshots "
        "WHERE username = ? AND date <= date('now', ? || ' days') ORDER BY date DESC LIMIT 1",
        (username, f"-{days}")
    ).fetchone()
    conn.close()
    if row:
        return {"followers": row[0], "following": row[1]}
    return None


def get_yesterday_followers(username: str) -> set:
    """Get yesterday's follower list for diff."""
    yesterday = (datetime.now().replace(hour=0, minute=0) - __import__('datetime').timedelta(days=1)).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT follower_username FROM follower_list WHERE username = ? AND date = ?",
        (username, yesterday)
    ).fetchall()
    conn.close()
    return {r[0] for r in rows}


def save_follower_list(username: str, followers: list):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    for f in followers:
        conn.execute(
            "INSERT OR IGNORE INTO follower_list "
            "(date, username, follower_username, follower_name, follower_count, follower_bio) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (today, username, f.get("username", "?"), f.get("name", "?"),
             f.get("followers", 0), f.get("bio", "")[:200])
        )
    conn.commit()
    conn.close()


def parse_about(raw: list) -> dict:
    """Parse bird about output into a clean dict."""
    if not raw:
        return {}
    # bird about returns a single object (might be in a list)
    data = raw[0] if isinstance(raw, list) else raw
    return {
        "followers": data.get("followers_count", data.get("followers", 0)) or 0,
        "following": data.get("friends_count", data.get("following", 0)) or 0,
        "name": data.get("name", "?"),
        "username": data.get("screen_name", data.get("username", "?")),
        "bio": data.get("description", data.get("bio", "")),
    }


def parse_follower_list(raw: list) -> list:
    """Parse bird followers output into clean dicts."""
    followers = []
    for item in raw:
        followers.append({
            "username": item.get("screen_name", item.get("username", "?")),
            "name": item.get("name", "?"),
            "followers": item.get("followers_count", item.get("followers", 0)) or 0,
            "bio": item.get("description", item.get("bio", "")),
        })
    return followers


def format_analytics(username: str, current: dict, today_delta: int,
                     week_trend: dict, month_trend: dict,
                     new_followers: list = None, lost_followers: list = None) -> str:
    """Format analytics for Telegram."""
    today = datetime.now().strftime("%b %d")
    lines = [f"👥 *FOLLOWER ANALYTICS* — {today}\n"]

    delta_str = f"+{today_delta}" if today_delta >= 0 else str(today_delta)
    lines.append(f"@{username}")
    lines.append(f"📊 Followers: {current['followers']:,} ({delta_str} today)")

    if week_trend:
        week_delta = current['followers'] - week_trend['followers']
        sign = "+" if week_delta >= 0 else ""
        lines.append(f"📈 7-day: {sign}{week_delta}")

    if month_trend:
        month_delta = current['followers'] - month_trend['followers']
        sign = "+" if month_delta >= 0 else ""
        lines.append(f"📈 30-day: {sign}{month_delta}")

    lines.append(f"👀 Following: {current['following']:,}")

    if new_followers:
        lines.append(f"\n✨ New followers today ({len(new_followers)}):")
        for f in new_followers[:10]:  # Cap at 10
            follower_info = f"• @{f['username']} ({f['followers']:,} followers)"
            if f.get("bio"):
                follower_info += f" — {f['bio'][:60]}"
            lines.append(follower_info)
        if len(new_followers) > 10:
            lines.append(f"  ...and {len(new_followers) - 10} more")

    if lost_followers:
        lines.append(f"\n👋 Unfollowed ({len(lost_followers)}):")
        for username in lost_followers[:5]:
            lines.append(f"  • @{username}")

    return "\n".join(lines)


def main():
    # DISABLED: Bird CLI removed while account suspended
    # All functionality depends on Bird CLI (bird_about, bird_followers).
    # Re-enable when @xBenJamminx suspension is resolved.
    print("[DISABLED] Follower Analytics disabled — Bird CLI suspended")
    return

    parser = argparse.ArgumentParser(description="Follower Analytics")
    parser.add_argument("--send", action="store_true", help="Send to Telegram")
    parser.add_argument("--username", type=str, default="xBenJamminx", help="Twitter username")
    parser.add_argument("--detailed", action="store_true", help="Include follower list diff")
    parser.add_argument("--account", type=str, default="ben", help="Bird CLI account")
    args = parser.parse_args()

    ensure_tables()

    # Get current stats
    log(f"Fetching profile for @{args.username}...", LOG_FILE)
    try:
        raw_about = bird_about(args.username, account=args.account)
        current = parse_about(raw_about)
        log(f"Followers: {current['followers']:,} | Following: {current['following']:,}", LOG_FILE)
    except BirdError as e:
        log(f"❌ Failed to fetch profile: {e}", LOG_FILE)
        return

    # Save today's snapshot
    save_snapshot(args.username, current["followers"], current["following"])

    # Get trends
    yesterday = get_trend(args.username, 1)
    today_delta = (current["followers"] - yesterday["followers"]) if yesterday else 0

    week_trend = get_trend(args.username, 7)
    month_trend = get_trend(args.username, 30)

    # Detailed follower diff
    new_followers = None
    lost_followers = None

    if args.detailed:
        log("Fetching follower list for diff...", LOG_FILE)
        try:
            raw_followers = bird_followers(args.username, n=200, account=args.account)
            today_list = parse_follower_list(raw_followers)

            # Save today's list
            save_follower_list(args.username, today_list)

            # Compare with yesterday
            yesterday_set = get_yesterday_followers(args.username)
            today_set = {f["username"] for f in today_list}

            new_usernames = today_set - yesterday_set
            lost_usernames = yesterday_set - today_set

            new_followers = [f for f in today_list if f["username"] in new_usernames]
            new_followers.sort(key=lambda f: f["followers"], reverse=True)
            lost_followers = list(lost_usernames)

            log(f"New: {len(new_followers)} | Lost: {len(lost_followers)}", LOG_FILE)
        except BirdError as e:
            log(f"⚠️ Follower list fetch failed: {e}", LOG_FILE)

    output = format_analytics(
        args.username, current, today_delta,
        week_trend, month_trend,
        new_followers, lost_followers
    )
    print(f"\n{output}")

    if args.send:
        send_telegram(output)


if __name__ == "__main__":
    main()
