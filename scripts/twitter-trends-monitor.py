#!/usr/bin/env python3
"""
Twitter/X Trends Monitor - Track what's hot in AI/automation/creator space
Uses bird CLI for searching
"""
import sqlite3
import subprocess
import json
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/twitter-trends-monitor.log")
SUMMARY_FILE = Path("/root/clawd/memory/twitter_trends_summary.md")

# Searches to run
SEARCHES = [
    "AI tools viral min_faves:100",
    "automation workflow min_faves:50",
    "solopreneur revenue min_faves:100",
    "content creation tips min_faves:100",
    "no code app min_faves:50",
    "indie hacker launched min_faves:50",
    "ChatGPT hack min_faves:100",
    "Claude AI min_faves:50",
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
        CREATE TABLE IF NOT EXISTS twitter_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE,
            author TEXT,
            text TEXT,
            likes INTEGER,
            retweets INTEGER,
            url TEXT,
            search_query TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def search_twitter(query):
    """Use bird CLI to search Twitter"""
    import os
    auth_token = os.environ.get("AUTH_TOKEN", "REDACTED_TWITTER_AUTH_TOKEN")
    ct0 = os.environ.get("CT0", "1feded6ef927dcaaa873bf8000f6fa59aaee85ace1e5c1060b2cc8ad35e6f6a3b15eb5c982af43e3e12860266c4a8ecda849908e5751675f155de353e24e868035ccaa0a3080b301b40cb09964e5e90b")

    try:
        result = subprocess.run(
            ["bird", "search", query, "--json", "-n", "10",
             "--auth-token", auth_token, "--ct0", ct0],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            log(f"bird search failed: {result.stderr}")
            return []

        # Parse JSON output from bird
        tweets = []
        try:
            data = json.loads(result.stdout)
            for tweet in data if isinstance(data, list) else data.get("tweets", []):
                author = tweet.get("author", {}).get("username", "") or tweet.get("user", {}).get("screen_name", "")
                tweet_id = tweet.get("id", "") or tweet.get("id_str", "")
                text = tweet.get("text", "") or tweet.get("full_text", "")
                likes = tweet.get("favorite_count", 0) or tweet.get("public_metrics", {}).get("like_count", 0)
                retweets = tweet.get("retweet_count", 0) or tweet.get("public_metrics", {}).get("retweet_count", 0)

                tweets.append({
                    "tweet_id": str(tweet_id),
                    "author": f"@{author}" if author else "",
                    "text": text,
                    "likes": likes,
                    "retweets": retweets,
                    "url": f"https://twitter.com/{author}/status/{tweet_id}" if author and tweet_id else ""
                })
        except json.JSONDecodeError as e:
            log(f"JSON parse error: {e}")

        return tweets

    except subprocess.TimeoutExpired:
        log(f"Search timed out for: {query}")
        return []
    except Exception as e:
        log(f"Search error: {e}")
        return []

def fetch_all_searches():
    """Run all searches and collect results"""
    all_results = []

    for query in SEARCHES:
        log(f"Searching: {query}")
        tweets = search_twitter(query)
        log(f"  Found {len(tweets)} tweets")

        for tweet in tweets:
            tweet["search_query"] = query
            all_results.append(tweet)

    return all_results

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0

    for r in results:
        if not r.get("tweet_id"):
            continue
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO twitter_trends
                (tweet_id, author, text, likes, retweets, url, search_query, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                r.get("tweet_id", ""),
                r.get("author", ""),
                r.get("text", "")[:500],
                r.get("likes", 0),
                r.get("retweets", 0),
                r.get("url", ""),
                r.get("search_query", ""),
                datetime.now().isoformat()
            ))
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
        SELECT author, text, likes, url FROM twitter_trends
        WHERE created_at > datetime('now', '-24 hours')
        ORDER BY likes DESC
        LIMIT 10
    ''')
    tweets = cursor.fetchall()
    conn.close()

    summary = "🐦 Twitter/X Trending (last 24h)\n\n"
    for author, text, likes, url in tweets:
        text_preview = text[:100].replace("\n", " ").strip()
        if len(text) > 100:
            text_preview += "..."
        likes_str = f" ({likes}❤️)" if likes else ""
        summary += f"• {author}: _{text_preview}_{likes_str}\n  [{url}]({url})\n\n"

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(summary)
    return summary

def main():
    log("Twitter trends monitor starting...")
    ensure_tables()

    results = fetch_all_searches()
    log(f"Found {len(results)} total tweets")

    saved = save_results(results)
    log(f"Saved {saved} tweets")

    summary = generate_summary()
    log("Summary generated")
    print(summary[:500])

    log("Done")

if __name__ == "__main__":
    main()
