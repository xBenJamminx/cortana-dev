#!/usr/bin/env python3
"""
YouTube Trending Monitor - Track viral content in AI/tech/creator space
Uses YouTube RSS feeds for trending in categories
"""
import sqlite3
import requests
import feedparser
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/youtube-trending-monitor.log")
SUMMARY_FILE = Path("/root/clawd/memory/youtube_trends_summary.md")

# YouTube RSS feeds for channels/topics we care about
# Format: (name, feed_url)
YOUTUBE_FEEDS = [
    # Tech/AI channels
    ("Fireship", "https://www.youtube.com/feeds/videos.xml?channel_id=UCsBjURrPoezykLs9EqgamOA"),
    ("Two Minute Papers", "https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7l4upoX8nvctg"),
    ("Matt Wolfe", "https://www.youtube.com/feeds/videos.xml?channel_id=UCJIfeSCssxSC_Dhc5s7woww"),
    ("AI Explained", "https://www.youtube.com/feeds/videos.xml?channel_id=UCNJ1Ymd5yFuUPtn21xtRbbw"),
    ("The AI Advantage", "https://www.youtube.com/feeds/videos.xml?channel_id=UCLZGCe59kwxd9DlmEMVCPuw"),
    # Solopreneur/Creator
    ("Ali Abdaal", "https://www.youtube.com/feeds/videos.xml?channel_id=UCoOae5nYA7VqaXzerajD0lg"),
    ("Pat Flynn", "https://www.youtube.com/feeds/videos.xml?channel_id=UCGk1LCv1E3SvrumNKOJSLzA"),
    ("Dan Koe", "https://www.youtube.com/feeds/videos.xml?channel_id=UCohg4K5NlYXNFPBCiEcOxZw"),
    # No-code/Automation
    ("Liam Ottley", "https://www.youtube.com/feeds/videos.xml?channel_id=UCWRBqP4RG1m_G96Hrg0DT-w"),
    ("Brett from AI Automation Agency", "https://www.youtube.com/feeds/videos.xml?channel_id=UCc6QrPJQb5wWTqOmN1p3m3Q"),
]

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def ensure_tables():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS youtube_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT UNIQUE,
            title TEXT,
            channel TEXT,
            url TEXT,
            published TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_youtube_feeds():
    """Fetch latest videos from YouTube RSS feeds"""
    results = []

    for channel_name, feed_url in YOUTUBE_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:  # Last 3 videos per channel
                video_id = entry.get("yt_videoid", "")
                results.append({
                    "video_id": video_id,
                    "title": entry.get("title", ""),
                    "channel": channel_name,
                    "url": entry.get("link", f"https://youtube.com/watch?v={video_id}"),
                    "published": entry.get("published", "")
                })
            log(f"  {channel_name}: {len(feed.entries)} videos")
        except Exception as e:
            log(f"  {channel_name} error: {e}")

    return results

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0

    for r in results:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO youtube_videos (video_id, title, channel, url, published, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (r["video_id"], r["title"], r["channel"], r["url"], r["published"], datetime.now().isoformat()))
            if cursor.rowcount > 0:
                saved += 1
        except Exception as e:
            log(f"Save error: {e}")

    conn.commit()
    conn.close()
    return saved

def generate_summary():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, channel, url FROM youtube_videos
        WHERE created_at > datetime('now', '-48 hours')
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    videos = cursor.fetchall()
    conn.close()

    summary = "📺 YouTube - Latest from AI/Creator Channels\n\n"
    for title, channel, url in videos:
        summary += f"• [{title}]({url})\n  _{channel}_\n\n"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary)
    return summary

def main():
    log("YouTube trends monitor starting...")
    ensure_tables()

    log("Fetching YouTube feeds...")
    results = fetch_youtube_feeds()
    log(f"Found {len(results)} videos")

    saved = save_results(results)
    log(f"Saved {saved} new videos")

    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])

    log("Done")

if __name__ == "__main__":
    main()
