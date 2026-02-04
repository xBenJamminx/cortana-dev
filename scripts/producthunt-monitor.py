#!/usr/bin/env python3
"""
Product Hunt Daily Monitor - Track trending products/launches
"""
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/producthunt-monitor.log")
SUMMARY_FILE = Path("/root/clawd/memory/producthunt_summary.md")

# Product Hunt doesn't require auth for basic RSS/frontpage scraping
PH_API = "https://www.producthunt.com/frontend/graphql"

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
        CREATE TABLE IF NOT EXISTS producthunt_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            tagline TEXT,
            url TEXT UNIQUE,
            votes INTEGER,
            topics TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_producthunt():
    """Fetch top products using their GraphQL API"""
    try:
        # GraphQL query for today's top products
        query = """
        query {
            posts(first: 15, order: VOTES) {
                edges {
                    node {
                        id
                        name
                        tagline
                        url
                        votesCount
                        topics {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; CortanaBot/1.0)",
        }

        r = requests.post(PH_API, json={"query": query}, headers=headers, timeout=30)

        if r.status_code != 200:
            log(f"API returned {r.status_code}, trying RSS fallback")
            return fetch_producthunt_rss()

        data = r.json()
        results = []

        for edge in data.get("data", {}).get("posts", {}).get("edges", []):
            node = edge.get("node", {})
            topics = [t["node"]["name"] for t in node.get("topics", {}).get("edges", [])]
            results.append({
                "title": node.get("name", ""),
                "tagline": node.get("tagline", ""),
                "url": node.get("url", ""),
                "votes": node.get("votesCount", 0),
                "topics": ", ".join(topics[:3])
            })

        return results
    except Exception as e:
        log(f"GraphQL error: {e}, trying RSS")
        return fetch_producthunt_rss()

def fetch_producthunt_rss():
    """Fallback to RSS feed"""
    try:
        import feedparser
        feed = feedparser.parse("https://www.producthunt.com/feed")
        results = []

        for entry in feed.entries[:15]:
            results.append({
                "title": entry.get("title", ""),
                "tagline": entry.get("summary", "")[:200],
                "url": entry.get("link", ""),
                "votes": 0,
                "topics": ""
            })

        return results
    except Exception as e:
        log(f"RSS error: {e}")
        return []

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0

    for r in results:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO producthunt_posts (title, tagline, url, votes, topics, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (r["title"], r["tagline"], r["url"], r["votes"], r["topics"], datetime.now().isoformat()))
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
        SELECT title, tagline, url, votes FROM producthunt_posts
        WHERE created_at > datetime('now', '-24 hours')
        ORDER BY votes DESC
        LIMIT 10
    ''')
    posts = cursor.fetchall()
    conn.close()

    summary = "🚀 Product Hunt Top Launches (last 24h)\n\n"
    for title, tagline, url, votes in posts:
        vote_str = f" ({votes}⬆)" if votes > 0 else ""
        summary += f"• [{title}]({url}){vote_str}\n  _{tagline[:100]}_\n\n"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary)
    return summary

def main():
    log("Product Hunt monitor starting...")
    ensure_tables()

    results = fetch_producthunt()
    log(f"Found {len(results)} products")

    saved = save_results(results)
    log(f"Saved {saved} products")

    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])

    log("Done")

if __name__ == "__main__":
    main()
