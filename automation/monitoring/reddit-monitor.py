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

# Load env
def _load_env():
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key = key.replace("export ", "").strip()
                    if key and not os.environ.get(key):
                        os.environ[key] = val
_load_env()

# Config
MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/.openclaw/workspace/logs/reddit-monitor.log")

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

# Subreddits dominated by memes/rants need higher thresholds
HIGH_NOISE_SUBS = {"ChatGPT", "OpenAI"}
HIGH_NOISE_MIN_SCORE = 200

# Quality filters — reject low-effort posts
LOW_EFFORT_PATTERNS = [
    # Too short to be substantive
    lambda t: len(t.strip()) < 20,
    # Pure reactions / memes
    lambda t: t.strip().lower().startswith(("haha", "lol", "lmao", "bruh", "omg", "wtf")),
    # Pure emoji posts
    lambda t: len(t.replace(" ", "")) > 0 and sum(1 for c in t if c.isalpha()) < len(t) * 0.3,
    # Rage / rant posts (low signal for content intel)
    lambda t: any(p in t.lower() for p in ["i hate ", "i actually hate ", "is trash", "is garbage", "worst update"]),
    # Just "Good job" / reaction posts
    lambda t: len(t.strip()) < 40 and any(p in t.lower() for p in ["good job", "well done", "nice one", "👏"]),
]

def is_low_effort(title: str) -> bool:
    """Check if a post title indicates low-effort/meme content"""
    return any(check(title) for check in LOW_EFFORT_PATTERNS)

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

REDDIT_CONN_ID = "522f0562-b211-42dc-acc2-830d0518b3e9"

def _get_reddit_token():
    """Get Reddit OAuth token from Composio"""
    try:
        api_key = os.environ.get("COMPOSIO_API_KEY", "")
        resp = requests.get(
            f"https://backend.composio.dev/api/v1/connectedAccounts/{REDDIT_CONN_ID}",
            headers={"x-api-key": api_key},
            timeout=10
        )
        return resp.json().get("connectionParams", {}).get("access_token", "")
    except:
        return ""

_reddit_token = None

def get_reddit_token(force_refresh=False):
    """Get cached Reddit token, refreshing if needed"""
    global _reddit_token
    if _reddit_token is None or force_refresh:
        _reddit_token = _get_reddit_token()
    return _reddit_token

def fetch_subreddit_hot(subreddit: str, limit: int = 25) -> List[Dict]:
    """Fetch hot posts from a subreddit using Reddit OAuth API via Composio"""
    token = get_reddit_token()
    try:
        url = f"https://oauth.reddit.com/r/{subreddit}/hot"
        headers = {
            "User-Agent": "CortanaMonitor/1.0",
            "Authorization": f"Bearer {token}"
        }
        r = requests.get(url, headers=headers, params={"limit": limit}, timeout=15)

        # Token expired - refresh and retry once
        if r.status_code in (401, 403):
            log(f"  Token expired for r/{subreddit}, refreshing...")
            token = get_reddit_token(force_refresh=True)
            headers["Authorization"] = f"Bearer {token}"
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
    """Generate a summary of trending topics, diverse across subreddits"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()

        # Get all posts from last 24 hours
        cursor.execute("""
            SELECT title, subreddit, score, keywords_matched
            FROM reddit_posts
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY score DESC
        """)
        all_posts = cursor.fetchall()

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

        # Diverse post selection: max 1 per sub for the summary
        summary_posts = []
        seen_subs = set()
        for title, sub, score, kw in all_posts:
            if sub not in seen_subs:
                seen_subs.add(sub)
                summary_posts.append((title, sub, score, kw))
            if len(summary_posts) >= 8:
                break

        summary = f"📊 Reddit Monitor Summary ({datetime.now().strftime('%Y-%m-%d %H:%M')})\n\n"

        if top_keywords:
            summary += "🔥 Hot Keywords:\n"
            for kw, count in top_keywords:
                summary += f"  • {kw}: {count} mentions\n"
            summary += "\n"

        if summary_posts:
            summary += "📈 Top Posts (1 per sub):\n"
            for title, sub, score, _ in summary_posts:
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
            sub = post.get("subreddit", subreddit)

            # Higher bar for noisy subreddits
            min_score = HIGH_NOISE_MIN_SCORE if sub in HIGH_NOISE_SUBS else MIN_SCORE
            if post["score"] < min_score:
                continue

            # Skip memes, rants, and low-effort posts
            if is_low_effort(post["title"]):
                log(f"  Skipped (low-effort): {post['title'][:50]}...")
                continue

            # Check for keyword matches
            keywords = match_keywords(post["title"])

            # Save if it has keywords or genuinely high score
            save_threshold = 500 if sub in HIGH_NOISE_SUBS else 100
            if keywords or post["score"] >= save_threshold:
                if save_post(post, keywords):
                    total_saved += 1
                    if keywords:
                        log(f"  Saved: {post['title'][:50]}... (keywords: {keywords})")

    log(f"Saved {total_saved} posts")

    # Generate and log summary
    summary = get_trending_summary()
    log(summary)

    # Save summary to file for morning briefing
    summary_file = Path("/root/.openclaw/workspace/memory/reddit_daily_summary.txt")
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(summary)

    log("Reddit monitor complete")

if __name__ == "__main__":
    main()
