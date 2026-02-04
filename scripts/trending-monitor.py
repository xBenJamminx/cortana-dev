#!/usr/bin/env python3
"""
Trending Topics Monitor - Track AI/tech/creator trends
Uses DuckDuckGo for news and web searches
"""
import sqlite3
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/trending-monitor.log")

SEARCH_QUERIES = [
    "AI tools 2025",
    "Claude AI news",
    "GPT news",
    "indie hacker trending",
    "no-code tools",
    "vibe coding",
    "AI automation",
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
        CREATE TABLE IF NOT EXISTS trending_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            url TEXT UNIQUE,
            body TEXT,
            query TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_news():
    try:
        from duckduckgo_search import DDGS
        all_results = []
        
        with DDGS() as ddgs:
            for query in SEARCH_QUERIES:
                log(f"Searching: {query}")
                try:
                    news = list(ddgs.news(query, max_results=5))
                    for item in news:
                        all_results.append({
                            "title": item.get("title", ""),
                            "source": item.get("source", ""),
                            "url": item.get("url", ""),
                            "body": item.get("body", ""),
                            "query": query
                        })
                except Exception as e:
                    log(f"  Error: {e}")
        
        return all_results
    except Exception as e:
        log(f"Fatal error: {e}")
        return []

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0
    
    for r in results:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO trending_news (title, source, url, body, query, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (r["title"], r["source"], r["url"], r["body"], r["query"], datetime.now().isoformat()))
            if cursor.rowcount > 0:
                saved += 1
        except:
            pass
    
    conn.commit()
    conn.close()
    return saved

def generate_summary():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, source, url FROM trending_news
        WHERE created_at > datetime('now', '-24 hours')
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    news = cursor.fetchall()
    conn.close()
    
    summary = "📰 Trending Topics (last 24h)\n\n"
    for title, source, url in news:
        summary += f"• {title}\n  _{source}_\n\n"
    
    Path("/root/clawd/memory/trending_summary.md").write_text(summary)
    return summary

def main():
    log("Trending monitor starting...")
    ensure_tables()
    
    results = fetch_news()
    log(f"Found {len(results)} articles")
    
    saved = save_results(results)
    log(f"Saved {saved} new articles")
    
    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])
    
    log("Done")

if __name__ == "__main__":
    main()
