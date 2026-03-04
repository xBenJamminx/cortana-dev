#!/usr/bin/env python3
"""
Competitor Monitor — Track what creators in our niche are posting about.

Monitors Twitter accounts + YouTube channels, stores in SQLite, generates
reports. Enhanced with keyword alerting and engagement spike detection.

Usage:
  python3 competitor-monitor.py                    # Full run
  python3 competitor-monitor.py --alert-keywords "openclaw,cortana"
  python3 competitor-monitor.py --alert-velocity 100

Cron: existing schedule (every 6h)
"""

import sqlite3
import json
import sys
import time
import argparse
import feedparser
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.bird import (
    bird_user_tweets, normalize_tweet, send_telegram, log as bird_log,
    BirdError, BirdRateLimited,
)

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = "/root/.openclaw/workspace/logs/competitor-monitor.log"

def log(msg):
    bird_log(msg, LOG_FILE)

# Twitter accounts to monitor
TWITTER_COMPETITORS = [
    # === AI LABS & OFFICIAL ===
    "OpenAI", "AnthropicAI", "GoogleDeepMind", "xai", "NVIDIAAI",
    # === RESEARCHERS & THOUGHT LEADERS ===
    "karpathy", "sama", "ylecun", "drfeifei", "fchollet",
    "demishassabis", "lexfridman", "DrJimFan",
    # === CURATED AI NEWS & NEWSLETTERS ===
    "rowancheung", "TheRundownAI", "kimmonismus", "_akhaliq",
    "bensbites", "theneuron", "superhumanai", "tldrai",
    "theresanaiforthat", "AravSrinivas",
    # === BUILDERS & CREATORS ===
    "LinusEkenstam", "mattshumer_", "LiamOttley", "levelsio",
    "marclou", "dannypostma", "thisguyknowsai", "nonmayorpete",
    "venturetwins", "mckaywrigley", "hwchase17", "bentossell",
    "swyx", "ai_for_success", "bindureddy", "skirank",
]

# YouTube channels
YOUTUBE_COMPETITORS = [
    ("Fireship", "UCsBjURrPoezykLs9EqgamOA"),
    ("Matt Wolfe", "UCJIfeSCssxSC_Dhc5s7woww"),
    ("AI Explained", "UCNJ1Ymd5yFuUPtn21xtRbbw"),
    ("The AI Advantage", "UCHhYXsLBEVVnbvsq57n1MTQ"),
    ("Liam Ottley", "UCui4jxDaMb53Gdh-AZUTPAg"),
    ("Greg Isenberg", "UCGwuxdEeCf0TIA2RbPOj-8g"),
    ("My First Million", "UCyaN6mg5u8Cjy2ZI4ikWaug"),
    ("Two Minute Papers", "UCbfYPyITQ-7l4upoX8nvctg"),
    ("Yannic Kilcher", "UCZHmQk67mSJgfCCTn7xBfew"),
    ("AI Jason", "UCrXSVX9a1mj8l0CMLwKgMVw"),
    ("David Ondrej", "UCPGrgwfbkjTIgPoOh2q1BAg"),
    ("WorldofAI", "UC2WmuBuFq6gL08QYG-JjXKw"),
    ("Wes Roth", "UCqcbQf6yw5KzRoDDcZ_wBSw"),
    ("TheAIGRID", "UCbY9xX3_jW5c2fjlZVBI4cg"),
]

# Keywords that trigger immediate alerts
DEFAULT_ALERT_KEYWORDS = [
    "openclaw", "cortana", "bird cli", "claude code", "everydayai",
]


def ensure_tables():
    conn = sqlite3.connect(MEMORY_DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS competitor_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator TEXT,
            platform TEXT,
            content TEXT,
            url TEXT,
            engagement TEXT,
            created_at TEXT,
            UNIQUE(creator, url)
        )
    ''')
    conn.commit()
    conn.close()


def fetch_twitter_competitors(alert_keywords: list = None, alert_velocity: float = 100):
    """Fetch recent tweets from competitor accounts using Bird CLI."""
    # DISABLED: Bird CLI removed while account suspended
    log("  [DISABLED] Twitter competitor fetch skipped — Bird CLI suspended")
    return [], []

    results = []
    alerts = []

    for username in TWITTER_COMPETITORS:
        try:
            raw = bird_user_tweets(username, n=3)
            tweets = [normalize_tweet(t) for t in raw]
            count = 0

            for t in tweets:
                results.append({
                    'creator': username,
                    'platform': 'twitter',
                    'content': t['text'][:280],
                    'url': t['url'],
                    'engagement': f"{t['likes']} likes, {t['retweets']} RTs",
                })
                count += 1

                # Keyword alerting
                if alert_keywords:
                    text_lower = t['text'].lower()
                    matched = [kw for kw in alert_keywords if kw.lower() in text_lower]
                    if matched:
                        alerts.append({
                            'type': 'keyword',
                            'username': username,
                            'keywords': matched,
                            'tweet': t,
                        })

                # Engagement spike detection
                if t['velocity'] >= alert_velocity and t['age_hours'] <= 6:
                    alerts.append({
                        'type': 'spike',
                        'username': username,
                        'velocity': t['velocity'],
                        'tweet': t,
                    })

            log(f"  @{username}: {count} tweets")
            time.sleep(2)  # Rate limit protection
        except BirdRateLimited:
            log("  Rate limited, stopping Twitter fetch")
            break
        except BirdError as e:
            log(f"  @{username} error: {e}")

    return results, alerts


def fetch_youtube_competitors():
    """Fetch recent videos from competitor channels."""
    results = []
    for name, channel_id in YOUTUBE_COMPETITORS:
        try:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                results.append({
                    'creator': name,
                    'platform': 'youtube',
                    'content': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'engagement': entry.get('published', '')[:10]
                })
            log(f"  {name}: {min(2, len(feed.entries))} videos")
        except Exception as e:
            log(f"  {name} error: {e}")
    return results


def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    saved = 0
    for r in results:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO competitor_content "
                "(creator, platform, content, url, engagement, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (r['creator'], r['platform'], r['content'],
                 r['url'], r['engagement'], datetime.now().isoformat())
            )
            if conn.total_changes:
                saved += 1
        except:
            pass
    conn.commit()
    conn.close()
    return saved


def generate_report():
    """Generate competitor activity report."""
    conn = sqlite3.connect(MEMORY_DB)
    content = conn.execute(
        "SELECT creator, platform, content, engagement, url "
        "FROM competitor_content "
        "WHERE created_at > datetime('now', '-24 hours') ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    report = ["👀 *COMPETITOR WATCH*\n"]
    report.append(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    twitter = [c for c in content if c[1] == 'twitter']
    youtube = [c for c in content if c[1] == 'youtube']

    if twitter:
        report.append("\n🐦 TWITTER:")
        for creator, _, text, engagement, url in twitter[:10]:
            text_short = text[:80].replace('\n', ' ') + "..."
            report.append(f"  @{creator}: {text_short}")
            report.append(f"    {engagement}")

    if youtube:
        report.append("\n📺 YOUTUBE:")
        for creator, _, title, date, url in youtube[:10]:
            report.append(f"  {creator}: {title[:60]}")
            report.append(f"    Published: {date}")

    return "\n".join(report)


def format_alerts(alerts: list) -> str:
    """Format keyword/spike alerts for Telegram."""
    if not alerts:
        return ""

    lines = ["🚨 *COMPETITOR ALERTS*\n"]

    keyword_alerts = [a for a in alerts if a['type'] == 'keyword']
    spike_alerts = [a for a in alerts if a['type'] == 'spike']

    if keyword_alerts:
        lines.append("🔑 *Keyword Mentions:*")
        for a in keyword_alerts:
            t = a['tweet']
            text_preview = t['text'][:100].replace('\n', ' ')
            lines.append(
                f"  @{a['username']} mentioned: {', '.join(a['keywords'])}\n"
                f"    \"{text_preview}...\"\n"
                f"    {t['url']}"
            )

    if spike_alerts:
        lines.append("\n📈 *Engagement Spikes:*")
        for a in spike_alerts:
            t = a['tweet']
            text_preview = t['text'][:100].replace('\n', ' ')
            lines.append(
                f"  @{a['username']} — {t['velocity']:.0f} likes/hr\n"
                f"    \"{text_preview}...\"\n"
                f"    ❤️ {t['likes']} in {t['age_hours']}h | {t['url']}"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Competitor Monitor")
    parser.add_argument("--send", action="store_true", help="Send alerts to Telegram")
    parser.add_argument("--alert-keywords", type=str, default=None,
                        help="Comma-separated keywords to alert on (default: openclaw,cortana,...)")
    parser.add_argument("--alert-velocity", type=float, default=100,
                        help="Min likes/hr for spike alert (default: 100)")
    parser.add_argument("--account", type=str, default="ben", help="Bird CLI account")
    args = parser.parse_args()

    # Parse alert keywords
    if args.alert_keywords:
        alert_keywords = [k.strip() for k in args.alert_keywords.split(",")]
    else:
        alert_keywords = DEFAULT_ALERT_KEYWORDS

    log("Competitor Monitor starting...")
    ensure_tables()

    all_results = []
    all_alerts = []

    log("Fetching Twitter competitors...")
    twitter_results, twitter_alerts = fetch_twitter_competitors(
        alert_keywords=alert_keywords,
        alert_velocity=args.alert_velocity,
    )
    all_results.extend(twitter_results)
    all_alerts.extend(twitter_alerts)

    log("Fetching YouTube competitors...")
    all_results.extend(fetch_youtube_competitors())

    log(f"Total: {len(all_results)} items | Alerts: {len(all_alerts)}")

    saved = save_results(all_results)
    log(f"Saved: {saved} new items")

    report = generate_report()
    print(report)
    Path("/root/.openclaw/workspace/memory/competitor_report.txt").write_text(report)

    # Send alerts if any
    if all_alerts:
        alert_text = format_alerts(all_alerts)
        print(f"\n{alert_text}")
        if args.send:
            send_telegram(alert_text)

    log("Done")


if __name__ == "__main__":
    main()
