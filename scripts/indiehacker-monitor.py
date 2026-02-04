#!/usr/bin/env python3
"""
Indie Hacker Monitor - Track trending topics from indie hacker communities
Runs every 4 hours via cron
Sources: Hacker News, IndieHackers, Product Hunt, DuckDuckGo News
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
LOG_FILE = Path("/root/clawd/logs/indiehacker-monitor.log")

# Keywords to track
KEYWORDS = [
    "indie hacker", "indiehacker", "side project", "saas", "micro-saas",
    "solopreneur", "bootstrapped", "mrr", "passive income", "solo founder",
    "maker", "build in public", "ship it", "launch", "product hunt",
    "no-code", "low-code", "automation", "ai tools", "revenue"
]

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
        CREATE TABLE IF NOT EXISTS indiehacker_posts (
            id TEXT PRIMARY KEY,
            title TEXT,
            source TEXT,
            score INTEGER,
            url TEXT,
            author TEXT,
            created_at TEXT,
            keywords_matched TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_hackernews_top() -> List[Dict]:
    """Fetch top stories from Hacker News"""
    try:
        # Get top story IDs
        r = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = r.json()[:50]  # Top 50

        posts = []
        for story_id in story_ids[:30]:  # Check first 30
            try:
                story_r = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
                story = story_r.json()
                if story and story.get("type") == "story":
                    posts.append({
                        "id": f"hn_{story.get('id')}",
                        "title": story.get("title", ""),
                        "source": "Hacker News",
                        "score": story.get("score", 0),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story.get('id')}"),
                        "author": story.get("by", ""),
                    })
            except:
                continue

        return posts
    except Exception as e:
        log(f"Error fetching HN: {e}")
        return []

def fetch_producthunt_trending() -> List[Dict]:
    """Fetch trending from Product Hunt (public page scrape fallback)"""
    try:
        # Try the public API endpoint
        headers = {"User-Agent": "CortanaMonitor/1.0"}
        r = requests.get("https://www.producthunt.com/frontend/graphql",
                        headers=headers, timeout=10)
        # This usually needs auth, so fall back to DuckDuckGo
        return []
    except:
        return []

def fetch_duckduckgo_news(query: str, max_results: int = 10) -> List[Dict]:
    """Search DuckDuckGo news for indie hacker topics"""
    try:
        from duckduckgo_search import DDGS
        posts = []
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))
            for r in results:
                posts.append({
                    "id": f"ddg_{hash(r.get('url', ''))}",
                    "title": r.get("title", ""),
                    "source": r.get("source", "News"),
                    "score": 0,
                    "url": r.get("url", ""),
                    "author": "",
                })
        return posts
    except Exception as e:
        log(f"DDG news error for '{query}': {e}")
        return []

def match_keywords(text: str) -> List[str]:
    """Find matching keywords in text"""
    text_lower = text.lower()
    return [kw for kw in KEYWORDS if kw.lower() in text_lower]

def save_post(post: Dict, keywords: List[str]) -> bool:
    """Save a post to the database"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO indiehacker_posts
            (id, title, source, score, url, author, created_at, keywords_matched)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post["id"],
            post["title"],
            post["source"],
            post["score"],
            post["url"],
            post["author"],
            datetime.now().isoformat(),
            ",".join(keywords)
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log(f"Error saving post: {e}")
        return False

def get_daily_summary() -> str:
    """Generate a summary of indie hacker trends"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()

        # Top posts from last 24 hours
        cursor.execute("""
            SELECT title, source, score, url, keywords_matched
            FROM indiehacker_posts
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY score DESC
            LIMIT 10
        """)
        top_posts = cursor.fetchall()

        # Keyword frequency
        cursor.execute("""
            SELECT keywords_matched FROM indiehacker_posts
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

        summary = f"🚀 Indie Hacker Monitor ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"

        if top_keywords:
            summary += "🔥 Hot Topics:\n"
            for kw, count in top_keywords:
                summary += f"  • {kw}: {count} mentions\n"
            summary += "\n"

        if top_posts:
            summary += "📈 Top Stories:\n"
            for title, source, score, url, _ in top_posts[:5]:
                score_str = f" ({score}⬆)" if score > 0 else ""
                summary += f"  • [{source}]{score_str}: {title}\n"
                summary += f"    {url}\n"

        return summary
    except Exception as e:
        return f"Error generating summary: {e}"

def main():
    log("Indie Hacker monitor starting...")
    ensure_tables()

    total_saved = 0

    # 1. Fetch Hacker News
    log("Fetching Hacker News...")
    hn_posts = fetch_hackernews_top()
    log(f"  Got {len(hn_posts)} HN stories")

    for post in hn_posts:
        keywords = match_keywords(post["title"])
        # Save if it matches indie hacker keywords OR has high score
        if keywords or post["score"] >= 100:
            if save_post(post, keywords):
                total_saved += 1
                if keywords:
                    log(f"  Saved: {post['title'][:60]}... (keywords: {keywords})")

    # 2. Search DuckDuckGo for indie hacker news
    search_queries = [
        "indie hacker news 2025",
        "micro saas launch",
        "solopreneur success story",
        "bootstrapped startup",
        "side project revenue",
        "build in public",
    ]

    for query in search_queries:
        log(f"Searching: {query}")
        posts = fetch_duckduckgo_news(query, max_results=5)
        for post in posts:
            keywords = match_keywords(post["title"])
            if keywords or True:  # Save all search results
                if save_post(post, keywords):
                    total_saved += 1

    log(f"Total saved: {total_saved} posts")

    # Generate and save summary
    summary = get_daily_summary()
    log(summary)

    summary_file = Path("/root/clawd/memory/indiehacker_daily_summary.txt")
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(summary)

    log("Indie Hacker monitor complete")

if __name__ == "__main__":
    main()
