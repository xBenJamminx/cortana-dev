#!/usr/bin/env python3
"""
Content Sweep - On-demand trending content check
Uses the same topic-aggregator as morning briefing to stay in sync.
"""
import subprocess
import sqlite3
import json
import sys
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
MONITORS = [
    ("/root/clawd/scripts/real-trends-monitor.py", "Trends"),
    ("/root/clawd/scripts/indiehacker-monitor.py", "IndieHacker/HN"),
    ("/root/clawd/scripts/producthunt-monitor.py", "Product Hunt"),
    ("/root/clawd/scripts/devto-hashnode-monitor.py", "Dev.to"),
]
TOPIC_AGGREGATOR = "/root/clawd/scripts/topic-aggregator.py"

def refresh_data():
    """Run monitors to gather fresh data"""
    for script, name in MONITORS:
        if Path(script).exists():
            try:
                print(f"Refreshing {name}...", file=sys.stderr)
                subprocess.run(["python3", script], timeout=90, capture_output=True)
            except Exception as e:
                print(f"  {name} failed: {e}", file=sys.stderr)

    # Run topic aggregator last
    if Path(TOPIC_AGGREGATOR).exists():
        try:
            print("Running topic aggregator...", file=sys.stderr)
            subprocess.run(["python3", TOPIC_AGGREGATOR], timeout=90, capture_output=True)
        except Exception as e:
            print(f"  Aggregator failed: {e}", file=sys.stderr)

def get_hot_topics():
    """Get hot topics from database (same as morning briefing uses), deduplicated"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        # Get most recent entry for each unique topic (deduped)
        cursor.execute("""
            SELECT topic, MAX(source_count) as source_count, sources, mentions
            FROM hot_topics
            WHERE created_at > datetime('now', '-12 hours')
            GROUP BY topic
            ORDER BY source_count DESC
            LIMIT 15
        """)
        results = []
        seen_topics = set()
        for topic, source_count, sources_json, mentions_json in cursor.fetchall():
            # Additional dedup by normalized topic name
            topic_key = topic.lower().strip()[:50]
            if topic_key in seen_topics:
                continue
            seen_topics.add(topic_key)
            results.append({
                "topic": topic,
                "source_count": source_count,
                "sources": json.loads(sources_json),
                "mentions": json.loads(mentions_json)
            })
        conn.close()
        return results[:10]
    except:
        return []

def get_fresh_launches():
    """Get fresh Product Hunt launches"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, url FROM producthunt_posts
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY created_at DESC LIMIT 5
        """)
        results = cursor.fetchall()
        conn.close()
        return results
    except:
        return []

def is_junk_topic(topic):
    """Filter out topics that aren't really actionable content topics"""
    topic_lower = topic.lower()
    junk_patterns = [
        # Tweet-style content that slipped through
        "people asking", "dms to send", "here are a bunch",
        "woke up to", "just posted", "thread", "retweet",
        "follow me", "check out my", "dm me", "link in bio",
        "who else", "anyone else", "hot take", "unpopular opinion",
        "i'm ", "i am ", "my favorite", "my top", "here's my",
        # Generic/vague
        "misc tech", "misc", "various", "multiple",
    ]
    return any(p in topic_lower for p in junk_patterns)

def format_report():
    """Format the content intel report"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"🎯 *Content Intel* ({now})", ""]

    # Hot Topics
    topics = [t for t in get_hot_topics() if not is_junk_topic(t["topic"])]
    if topics:
        lines.append("*🔥 HOT TOPICS*")
        for t in topics[:8]:
            indicator = "🔴" if t["source_count"] >= 3 else "🟡" if t["source_count"] >= 2 else "⚪"
            sources_str = ", ".join(t["sources"])
            lines.append(f"{indicator} *{t['topic'].upper()}* [{sources_str}]")

            # Dedupe mentions by URL
            seen_urls = set()
            unique_mentions = []
            for m in t["mentions"]:
                url = m.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_mentions.append(m)

            # Show top unique mentions
            for m in unique_mentions[:2]:
                url = m.get("url", "")
                text = m.get("text", "")[:60]
                if url:
                    lines.append(f"   • [{text}]({url})")
                else:
                    lines.append(f"   • {text}")
            lines.append("")

    # Fresh Launches
    launches = get_fresh_launches()
    if launches:
        lines.append("*🚀 FRESH LAUNCHES*")
        for title, url in launches:
            lines.append(f"• [{title}]({url})")
        lines.append("")

    lines.append("_🔴 3+ sources | 🟡 2 sources | ⚪ 1 source_")
    return "\n".join(lines)

def main():
    skip_refresh = "--no-refresh" in sys.argv

    if not skip_refresh:
        refresh_data()

    print(format_report())

if __name__ == "__main__":
    main()
