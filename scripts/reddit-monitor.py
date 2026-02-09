#!/usr/bin/env python3
"""
Reddit Monitor - Track trending posts in relevant subreddits
Runs every 4 hours via cron
"""
import os
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Config
MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/reddit-monitor.log")

# Subreddits to monitor
SUBREDDITS = [
    "artificial",
    "ChatGPT",
    "LocalLLaMA",
    "ClaudeAI",
    "OpenAI",
    "vibecoding",
    "startups",
    "SideProject",
    "indiehackers",
    "Entrepreneur",
    "nocode",
    "AutomateYourself",
]

# Keywords to track (case insensitive)
KEYWORDS = [
    "claude", "anthropic", "gpt", "ai tools", "ai agent",
    "no-code", "nocode", "indie hacker", "side project",
    "automation", "vibe coding", "vibecoding", "cursor",
    "bolt", "lovable", "replit", "v0", "windsurf",
    "saas", "micro-saas", "passive income", "solopreneur"
]

MIN_SCORE = 50  # Minimum upvotes to track

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def ensure_tables():
    """Create tables if they don't exist"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id TEXT PRIMARY KEY,
            title TEXT,
            subreddit TEXT,
            score INTEGER,
            num_comments INTEGER,
            url TEXT,
            permalink TEXT,
            author TEXT,
            created_utc REAL,
            created_at TEXT,
            keywords_matched TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            subreddit TEXT,
            top_keywords TEXT,
            avg_score REAL,
            post_count INTEGER
        )
    """)
    conn.commit()
    conn.close()

def fetch_subreddit_hot(subreddit: str, limit: int = 25) -> List[Dict]:
    """Fetch hot posts from a subreddit using Reddit's JSON API (no auth needed)"""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        headers = {"User-Agent": "CortanaMonitor/1.0"}
        r = requests.get(url, headers=headers, params={"limit": limit}, timeout=15)

        if r.status_code != 200:
            log(f"Error fetching r/{subreddit}: HTTP {r.status_code}")
            return []

        data = r.json()
        posts = []

        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            posts.append({
                "id": post.get("id"),
                "title": post.get("title", ""),
                "subreddit": post.get("subreddit", subreddit),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "url": post.get("url", ""),
                "permalink": f"https://reddit.com{post.get('permalink', '')}",
                "author": post.get("author", ""),
                "created_utc": post.get("created_utc", 0),
            })

        return posts
    except Exception as e:
        log(f"Error fetching r/{subreddit}: {e}")
        return []

def match_keywords(text: str) -> List[str]:
    """Find matching keywords in text"""
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw.lower() in text_lower]

def save_post(post: Dict, keywords: List[str]):
    """Save a post to the database"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO reddit_posts
            (id, title, subreddit, score, num_comments, url, permalink, author, created_utc, created_at, keywords_matched)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post["id"],
            post["title"],
            post["subreddit"],
            post["score"],
            post["num_comments"],
            post["url"],
            post["permalink"],
            post["author"],
            post["created_utc"],
            datetime.now().isoformat(),
            ",".join(keywords)
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log(f"Error saving post: {e}")
        return False

def get_trending_summary() -> str:
    """Generate a summary of trending topics"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()

        # Top posts from last 24 hours
        cursor.execute("""
            SELECT title, subreddit, score, keywords_matched
            FROM reddit_posts
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY score DESC
            LIMIT 10
        """)
        top_posts = cursor.fetchall()

        # Keyword frequency
        cursor.execute("""
            SELECT keywords_matched FROM reddit_posts
            WHERE created_at > datetime('now', '-24 hours')
        """)
        all_keywords = []
        for row in cursor.fetchall():
            if row[0]:
                all_keywords.extend(row[0].split(","))

        conn.close()

        # Count keywords
        keyword_counts = {}
        for kw in all_keywords:
            if kw:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        summary = f"📊 Reddit Monitor Summary ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"

        if top_keywords:
            summary += "🔥 Hot Keywords:\n"
            for kw, count in top_keywords:
                summary += f"  • {kw}: {count} mentions\n"
            summary += "\n"

        if top_posts:
            summary += "📈 Top Posts:\n"
            for title, sub, score, _ in top_posts[:5]:
                summary += f"  • r/{sub} ({score}⬆): {title[:60]}...\n"

        return summary
    except Exception as e:
        return f"Error generating summary: {e}"

def main():
    log("Reddit monitor starting...")
    ensure_tables()

    total_saved = 0

    for subreddit in SUBREDDITS:
        log(f"Fetching r/{subreddit}...")
        posts = fetch_subreddit_hot(subreddit)

        for post in posts:
            # Skip low-score posts
            if post["score"] < MIN_SCORE:
                continue

            # Check for keyword matches
            keywords = match_keywords(post["title"])

            # Save if it has keywords or high score
            if keywords or post["score"] >= 100:
                if save_post(post, keywords):
                    total_saved += 1
                    if keywords:
                        log(f"  Saved: {post['title'][:50]}... (keywords: {keywords})")

    log(f"Saved {total_saved} posts")

    # Generate and log summary
    summary = get_trending_summary()
    log(summary)

    # Save summary to file for morning briefing
    summary_file = Path("/root/clawd/memory/reddit_daily_summary.txt")
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(summary)

    log("Reddit monitor complete")

if __name__ == "__main__":
    main()
