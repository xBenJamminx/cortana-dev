#!/usr/bin/env python3
"""
Dev.to and Hashnode Monitor - Track trending dev content
"""
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/devto-hashnode-monitor.log")
SUMMARY_FILE = Path("/root/clawd/memory/devto_hashnode_summary.md")

# Tags to monitor
TAGS = ["ai", "automation", "nocode", "productivity", "webdev", "programming"]

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
        CREATE TABLE IF NOT EXISTS devto_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT UNIQUE,
            title TEXT,
            author TEXT,
            url TEXT,
            reactions INTEGER,
            source TEXT,
            tags TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_devto():
    """Fetch trending posts from Dev.to API"""
    results = []

    try:
        # Top articles from past week
        r = requests.get(
            "https://dev.to/api/articles",
            params={"top": 7, "per_page": 20},
            headers={"User-Agent": "CortanaBot/1.0"},
            timeout=30
        )

        if r.status_code == 200:
            for article in r.json():
                results.append({
                    "post_id": f"devto_{article.get('id', '')}",
                    "title": article.get("title", ""),
                    "author": article.get("user", {}).get("username", ""),
                    "url": article.get("url", ""),
                    "reactions": article.get("public_reactions_count", 0),
                    "source": "dev.to",
                    "tags": ",".join(article.get("tag_list", []))
                })

        log(f"Dev.to: Found {len(results)} articles")
    except Exception as e:
        log(f"Dev.to error: {e}")

    # Also fetch by tags
    for tag in TAGS[:3]:  # Limit to avoid rate limits
        try:
            r = requests.get(
                "https://dev.to/api/articles",
                params={"tag": tag, "top": 1, "per_page": 5},
                headers={"User-Agent": "CortanaBot/1.0"},
                timeout=30
            )

            if r.status_code == 200:
                for article in r.json():
                    results.append({
                        "post_id": f"devto_{article.get('id', '')}",
                        "title": article.get("title", ""),
                        "author": article.get("user", {}).get("username", ""),
                        "url": article.get("url", ""),
                        "reactions": article.get("public_reactions_count", 0),
                        "source": "dev.to",
                        "tags": ",".join(article.get("tag_list", []))
                    })
        except:
            pass

    return results

def fetch_hashnode():
    """Fetch trending posts from Hashnode GraphQL API"""
    results = []

    try:
        query = """
        query {
            feed(first: 15, filter: {type: BEST}) {
                edges {
                    node {
                        id
                        title
                        url
                        reactionCount
                        author {
                            username
                        }
                        tags {
                            name
                        }
                    }
                }
            }
        }
        """

        r = requests.post(
            "https://gql.hashnode.com",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if r.status_code == 200:
            data = r.json()
            edges = data.get("data", {}).get("feed", {}).get("edges", [])

            for edge in edges:
                node = edge.get("node", {})
                tags = [t.get("name", "") for t in node.get("tags", [])]
                results.append({
                    "post_id": f"hashnode_{node.get('id', '')}",
                    "title": node.get("title", ""),
                    "author": node.get("author", {}).get("username", ""),
                    "url": node.get("url", ""),
                    "reactions": node.get("reactionCount", 0),
                    "source": "hashnode",
                    "tags": ",".join(tags)
                })

            log(f"Hashnode: Found {len(results)} articles")
    except Exception as e:
        log(f"Hashnode error: {e}")

    return results

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0

    for r in results:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO devto_posts
                (post_id, title, author, url, reactions, source, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (r["post_id"], r["title"], r["author"], r["url"],
                  r["reactions"], r["source"], r["tags"], datetime.now().isoformat()))
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
        SELECT title, author, url, reactions, source FROM devto_posts
        WHERE created_at > datetime('now', '-48 hours')
        ORDER BY reactions DESC
        LIMIT 10
    ''')
    posts = cursor.fetchall()
    conn.close()

    summary = "💻 Dev.to / Hashnode Trending\n\n"
    for title, author, url, reactions, source in posts:
        emoji = "🔷" if source == "dev.to" else "🔶"
        summary += f"{emoji} [{title}]({url})\n  _@{author}_ ({reactions}❤️)\n\n"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary)
    return summary

def main():
    log("Dev.to / Hashnode monitor starting...")
    ensure_tables()

    devto = fetch_devto()
    hashnode = fetch_hashnode()

    all_results = devto + hashnode
    log(f"Total: {len(all_results)} articles")

    saved = save_results(all_results)
    log(f"Saved {saved} new articles")

    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])

    log("Done")

if __name__ == "__main__":
    main()
