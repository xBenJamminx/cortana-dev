#!/usr/bin/env python3
"""
Substack Popular Monitor - Track trending newsletters/posts
Uses RSS feeds from popular Substacks in AI/tech/creator space
"""
import sqlite3
import feedparser
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/substack-monitor.log")
SUMMARY_FILE = Path("/root/clawd/memory/substack_summary.md")

# Popular Substacks to monitor
SUBSTACKS = [
    # AI/Tech
    ("The Neuron", "https://www.theneurondaily.com/feed"),
    ("AI Supremacy", "https://aisupremacy.substack.com/feed"),
    ("The Rundown AI", "https://therundown.ai/feed"),
    ("Ben's Bites", "https://bensbites.beehiiv.com/feed"),  # Actually Beehiiv but RSS works
    ("Superhuman", "https://www.superhuman.ai/feed"),
    # Solopreneur/Creator
    ("The Hustle", "https://thehustle.co/feed"),
    ("Lenny's Newsletter", "https://www.lennysnewsletter.com/feed"),
    ("The Profile", "https://theprofile.substack.com/feed"),
    # Indie/Startup
    ("Indie Hackers", "https://www.indiehackers.com/feed.xml"),
    ("Starter Story", "https://www.starterstory.com/feed"),
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
        CREATE TABLE IF NOT EXISTS substack_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE,
            title TEXT,
            newsletter TEXT,
            url TEXT,
            summary TEXT,
            published TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_substacks():
    """Fetch latest posts from Substack RSS feeds"""
    results = []

    for name, feed_url in SUBSTACKS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:  # Last 3 posts per newsletter
                post_id = entry.get("id", entry.get("link", ""))
                results.append({
                    "post_id": f"substack_{hash(post_id)}",
                    "title": entry.get("title", ""),
                    "newsletter": name,
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:300],
                    "published": entry.get("published", "")
                })
            log(f"  {name}: {min(3, len(feed.entries))} posts")
        except Exception as e:
            log(f"  {name} error: {e}")

    return results

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0

    for r in results:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO substack_posts
                (post_id, title, newsletter, url, summary, published, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (r["post_id"], r["title"], r["newsletter"], r["url"],
                  r["summary"], r["published"], datetime.now().isoformat()))
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
        SELECT title, newsletter, url FROM substack_posts
        WHERE created_at > datetime('now', '-48 hours')
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    posts = cursor.fetchall()
    conn.close()

    summary = "📬 Newsletter Highlights\n\n"
    for title, newsletter, url in posts:
        summary += f"• [{title}]({url})\n  _{newsletter}_\n\n"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary)
    return summary

def main():
    log("Substack monitor starting...")
    ensure_tables()

    log("Fetching newsletter feeds...")
    results = fetch_substacks()
    log(f"Found {len(results)} posts")

    saved = save_results(results)
    log(f"Saved {saved} new posts")

    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])

    log("Done")

if __name__ == "__main__":
    main()
