#!/usr/bin/env python3
"""
Google Trends Monitor - Track breakout searches in AI/automation/creator space
"""
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/google-trends-monitor.log")
SUMMARY_FILE = Path("/root/clawd/memory/google_trends_summary.md")

# Categories of interest
CATEGORIES = [
    "AI tools",
    "automation software",
    "content creation",
    "solopreneur",
    "no code",
    "viral marketing",
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
        CREATE TABLE IF NOT EXISTS google_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            category TEXT,
            traffic TEXT,
            related_queries TEXT,
            url TEXT UNIQUE,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_daily_trends():
    """Fetch Google Trends daily trending searches"""
    try:
        # Use the RSS feed for daily trends
        import feedparser
        feed = feedparser.parse("https://trends.google.com/trending/rss?geo=US")

        results = []
        for entry in feed.entries[:20]:
            results.append({
                "term": entry.get("title", ""),
                "category": "daily_trend",
                "traffic": entry.get("ht_approx_traffic", ""),
                "related_queries": "",
                "url": entry.get("link", "")
            })

        return results
    except Exception as e:
        log(f"RSS error: {e}")
        return []

def fetch_related_trends():
    """Use pytrends to get related queries for our categories"""
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz=300)

        results = []
        for category in CATEGORIES:
            try:
                pytrends.build_payload([category], timeframe='now 7-d', geo='US')
                related = pytrends.related_queries()

                if category in related and related[category].get('rising') is not None:
                    rising = related[category]['rising']
                    for _, row in rising.head(5).iterrows():
                        results.append({
                            "term": row['query'],
                            "category": category,
                            "traffic": f"{row['value']}% growth",
                            "related_queries": category,
                            "url": f"https://trends.google.com/trends/explore?q={row['query'].replace(' ', '%20')}&geo=US"
                        })
            except Exception as e:
                log(f"Category {category} error: {e}")

        return results
    except ImportError:
        log("pytrends not installed, using RSS only")
        return []
    except Exception as e:
        log(f"pytrends error: {e}")
        return []

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0

    for r in results:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO google_trends (term, category, traffic, related_queries, url, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (r["term"], r["category"], r["traffic"], r["related_queries"], r["url"], datetime.now().isoformat()))
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

    # Get daily trends
    cursor.execute('''
        SELECT term, traffic, url FROM google_trends
        WHERE category = 'daily_trend' AND created_at > datetime('now', '-24 hours')
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    daily = cursor.fetchall()

    # Get rising queries in our categories
    cursor.execute('''
        SELECT term, category, traffic, url FROM google_trends
        WHERE category != 'daily_trend' AND created_at > datetime('now', '-24 hours')
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    rising = cursor.fetchall()

    conn.close()

    summary = "📈 Google Trends (last 24h)\n\n"

    if daily:
        summary += "*Daily Trending:*\n"
        for term, traffic, url in daily[:5]:
            traffic_str = f" ({traffic})" if traffic else ""
            summary += f"• [{term}]({url}){traffic_str}\n"
        summary += "\n"

    if rising:
        summary += "*Rising in Your Categories:*\n"
        for item in rising[:5]:
            term, category, traffic, url = item
            summary += f"• [{term}]({url}) - _{category}_ {traffic}\n"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary)
    return summary

def main():
    log("Google Trends monitor starting...")
    ensure_tables()

    # Fetch daily trends
    daily = fetch_daily_trends()
    log(f"Found {len(daily)} daily trends")

    # Fetch related trends for our categories
    related = fetch_related_trends()
    log(f"Found {len(related)} related trends")

    all_results = daily + related
    saved = save_results(all_results)
    log(f"Saved {saved} trends")

    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])

    log("Done")

if __name__ == "__main__":
    main()
