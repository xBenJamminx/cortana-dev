#!/usr/bin/env python3
"""
Exploding Topics Monitor - Track early trend signals
Uses their public trending page (no API key needed)
"""
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/exploding-topics-monitor.log")
SUMMARY_FILE = Path("/root/clawd/memory/exploding_topics_summary.md")

# Categories to check
CATEGORIES = [
    ("tech", "https://explodingtopics.com/blog/tech-trends"),
    ("ai", "https://explodingtopics.com/blog/ai-trends"),
    ("business", "https://explodingtopics.com/blog/business-trends"),
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
        CREATE TABLE IF NOT EXISTS exploding_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE,
            category TEXT,
            growth TEXT,
            description TEXT,
            url TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_exploding_topics():
    """Scrape trending topics from Exploding Topics"""
    results = []

    # Try to get data from their trending endpoint
    try:
        r = requests.get(
            "https://explodingtopics.com/api/trends",
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; CortanaBot/1.0)",
                "Accept": "application/json"
            },
            timeout=30
        )

        if r.status_code == 200:
            data = r.json()
            for trend in data.get("trends", [])[:20]:
                results.append({
                    "topic": trend.get("name", ""),
                    "category": trend.get("category", "general"),
                    "growth": trend.get("growth", ""),
                    "description": trend.get("description", ""),
                    "url": f"https://explodingtopics.com/topic/{trend.get('slug', '')}"
                })
            log(f"API: Found {len(results)} topics")
            return results
    except Exception as e:
        log(f"API failed: {e}, trying scrape...")

    # Fallback: scrape the homepage
    try:
        r = requests.get(
            "https://explodingtopics.com",
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
            timeout=30
        )

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")

            # Look for trend cards/items
            for item in soup.select(".trend-card, .topic-item, [class*='trend']")[:15]:
                title = item.select_one("h2, h3, .title, .name")
                growth = item.select_one(".growth, .percentage, [class*='growth']")
                link = item.select_one("a")

                if title:
                    results.append({
                        "topic": title.get_text(strip=True),
                        "category": "general",
                        "growth": growth.get_text(strip=True) if growth else "",
                        "description": "",
                        "url": link.get("href", "") if link else ""
                    })

            log(f"Scrape: Found {len(results)} topics")
    except Exception as e:
        log(f"Scrape error: {e}")

    # If still nothing, use DuckDuckGo to find trending topics
    if not results:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for result in ddgs.news("exploding topics AI trends 2026", max_results=10):
                    results.append({
                        "topic": result.get("title", ""),
                        "category": "ai",
                        "growth": "",
                        "description": result.get("body", ""),
                        "url": result.get("url", "")
                    })
            log(f"DDG fallback: Found {len(results)} topics")
        except Exception as e:
            log(f"DDG error: {e}")

    return results

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0

    for r in results:
        if not r.get("topic"):
            continue
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO exploding_topics
                (topic, category, growth, description, url, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (r["topic"], r["category"], r["growth"],
                  r["description"], r["url"], datetime.now().isoformat()))
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
        SELECT topic, category, growth, url FROM exploding_topics
        WHERE created_at > datetime('now', '-48 hours')
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    topics = cursor.fetchall()
    conn.close()

    summary = "🚀 Exploding Topics\n\n"
    for topic, category, growth, url in topics:
        growth_str = f" ({growth})" if growth else ""
        if url and url.startswith("http"):
            summary += f"• [{topic}]({url}){growth_str}\n"
        else:
            summary += f"• {topic}{growth_str}\n"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary)
    return summary

def main():
    log("Exploding Topics monitor starting...")
    ensure_tables()

    results = fetch_exploding_topics()
    log(f"Found {len(results)} topics")

    saved = save_results(results)
    log(f"Saved {saved} new topics")

    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])

    log("Done")

if __name__ == "__main__":
    main()
