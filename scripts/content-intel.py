#!/usr/bin/env python3
"""
Content Intelligence - Topic-first trending analysis
Detects what's blowing up across platforms, groups by topic, shows multi-platform signals.

Sources: Hacker News, Product Hunt, Dev.to, Google Trends, DuckDuckGo News
"""
import os
import json
import sqlite3
import requests
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/content-intel.log")

# Topic keywords to track and normalize
TOPIC_ALIASES = {
    "claude": ["claude", "anthropic", "claude 3", "claude code", "opus", "sonnet", "claude ai"],
    "gpt": ["gpt", "chatgpt", "openai", "gpt-4", "gpt-5", "gpt4", "gpt5", "codex"],
    "ai agents": ["ai agent", "agent", "agentic", "autonomous agent", "mcp", "agent sdk"],
    "cursor": ["cursor", "cursor ai", "cursor ide"],
    "windsurf": ["windsurf", "codeium"],
    "vibe coding": ["vibe coding", "vibecoding", "vibe-coding", "vibe code"],
    "no-code": ["no-code", "nocode", "no code", "low-code", "lowcode"],
    "indie hacker": ["indie hacker", "indiehacker", "indie hackers", "bootstrapped", "solopreneur", "solo founder"],
    "side project": ["side project", "sideproject", "weekend project", "shipping"],
    "saas": ["saas", "micro-saas", "microsaas", "mrr", "arr"],
    "product launch": ["product hunt", "producthunt", "ph launch", "launch", "launched", "launching"],
    "llm": ["llm", "large language model", "language model", "gemini", "llama", "mistral", "qwen"],
    "open source": ["open source", "opensource", "oss", "foss", "github"],
    "startup": ["startup", "startups", "founder", "founders", "yc", "y combinator"],
    "automation": ["automation", "automate", "automated", "workflow", "n8n", "make.com", "zapier"],
    "ai tools": ["ai tool", "ai tools", "ai app", "ai-powered"],
    "dev tools": ["developer tool", "dev tool", "devtool", "ide", "code editor"],
    "react": ["react", "reactjs", "next.js", "nextjs", "vercel"],
    "python": ["python", "fastapi", "django", "flask"],
    "rust": ["rust", "rustlang"],
    "typescript": ["typescript", "ts", "deno", "bun", "node"],
    "xcode": ["xcode", "swift", "ios", "apple developer"],
}

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def ensure_tables():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_intel (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            source TEXT,
            score INTEGER DEFAULT 0,
            topics TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            source TEXT,
            content_id TEXT,
            signal_strength INTEGER,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def extract_topics(text: str) -> List[str]:
    """Extract normalized topics from text"""
    text_lower = text.lower()
    found_topics = []
    for topic, aliases in TOPIC_ALIASES.items():
        for alias in aliases:
            if alias in text_lower:
                found_topics.append(topic)
                break
    return list(set(found_topics))

def fetch_hackernews() -> List[Dict]:
    """Fetch from Hacker News"""
    try:
        r = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = r.json()[:30]
        items = []
        for sid in story_ids:
            try:
                sr = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5)
                s = sr.json()
                if s and s.get("type") == "story":
                    items.append({
                        "id": f"hn_{s.get('id')}",
                        "title": s.get("title", ""),
                        "url": s.get("url", f"https://news.ycombinator.com/item?id={s.get('id')}"),
                        "source": "hn",
                        "score": s.get("score", 0)
                    })
            except:
                continue
        return items
    except Exception as e:
        log(f"HN error: {e}")
        return []

def fetch_producthunt() -> List[Dict]:
    """Fetch from Product Hunt via Atom feed"""
    try:
        r = requests.get("https://www.producthunt.com/feed",
                        headers={"User-Agent": "CortanaIntel/1.0"}, timeout=10)
        items = []
        # Parse Atom feed entries
        entries = re.findall(r'<entry>(.*?)</entry>', r.text, re.DOTALL)
        for i, entry in enumerate(entries[:15]):
            title_match = re.search(r'<title>([^<]+)</title>', entry)
            link_match = re.search(r'<link[^>]*href="([^"]+)"', entry)
            if title_match and link_match:
                title = title_match.group(1).strip()
                link = link_match.group(1)
                items.append({
                    "id": f"ph_{hash(link)}",
                    "title": title,
                    "url": link,
                    "source": "ph",
                    "score": 15 - i  # Rough ranking by position
                })
        return items
    except Exception as e:
        log(f"PH error: {e}")
        return []

def fetch_devto() -> List[Dict]:
    """Fetch from Dev.to API"""
    try:
        r = requests.get("https://dev.to/api/articles?per_page=20&top=1",
                        headers={"User-Agent": "CortanaIntel/1.0"}, timeout=10)
        items = []
        for article in r.json():
            items.append({
                "id": f"dev_{article.get('id')}",
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "source": "dev",
                "score": article.get("positive_reactions_count", 0)
            })
        return items
    except Exception as e:
        log(f"Dev.to error: {e}")
        return []

def fetch_duckduckgo_news() -> List[Dict]:
    """Fetch AI/tech news via DuckDuckGo"""
    try:
        from duckduckgo_search import DDGS
        items = []
        queries = ["AI tools trending", "Claude AI", "GPT news", "indie hacker", "tech startup launch"]
        with DDGS() as ddgs:
            for query in queries:
                try:
                    results = list(ddgs.news(query, max_results=5))
                    for r in results:
                        items.append({
                            "id": f"news_{hash(r.get('url', ''))}",
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "source": "news",
                            "score": 0
                        })
                except:
                    continue
        return items
    except Exception as e:
        log(f"DDG error: {e}")
        return []

def save_content(items: List[Dict]):
    """Save content to database"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    for item in items:
        topics = extract_topics(item["title"])
        cursor.execute("""
            INSERT OR REPLACE INTO content_intel
            (id, title, url, source, score, topics, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (item["id"], item["title"], item["url"], item["source"],
              item["score"], ",".join(topics), now))

        # Record topic signals
        for topic in topics:
            cursor.execute("""
                INSERT INTO topic_signals (topic, source, content_id, signal_strength, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (topic, item["source"], item["id"], item["score"], now))

    conn.commit()
    conn.close()

def get_trending_topics() -> Dict[str, Dict]:
    """Analyze topics by multi-platform signal strength"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    # Get recent topic signals
    cursor.execute("""
        SELECT topic, source, content_id, signal_strength
        FROM topic_signals
        WHERE created_at > datetime('now', '-24 hours')
    """)
    signals = cursor.fetchall()

    # Aggregate by topic
    topics = defaultdict(lambda: {"sources": set(), "content_ids": set(), "total_score": 0, "count": 0})
    for topic, source, content_id, strength in signals:
        topics[topic]["sources"].add(source)
        topics[topic]["content_ids"].add(content_id)
        topics[topic]["total_score"] += strength or 0
        topics[topic]["count"] += 1

    # Rank by multi-platform presence + engagement
    ranked = {}
    for topic, data in topics.items():
        platform_multiplier = len(data["sources"]) * 2  # Multi-platform = stronger signal
        ranked[topic] = {
            "sources": list(data["sources"]),
            "platform_count": len(data["sources"]),
            "content_count": len(data["content_ids"]),
            "total_score": data["total_score"],
            "rank_score": platform_multiplier * data["count"] + data["total_score"]
        }

    conn.close()
    return dict(sorted(ranked.items(), key=lambda x: x[1]["rank_score"], reverse=True))

def get_content_for_topic(topic: str, limit: int = 5) -> List[Dict]:
    """Get content items for a specific topic"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, url, source, score FROM content_intel
        WHERE topics LIKE ? AND created_at > datetime('now', '-24 hours')
        ORDER BY score DESC LIMIT ?
    """, (f"%{topic}%", limit))
    results = cursor.fetchall()
    conn.close()
    return [{"title": r[0], "url": r[1], "source": r[2], "score": r[3]} for r in results]

def get_fresh_launches() -> List[Dict]:
    """Get fresh Product Hunt launches"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, url, score FROM content_intel
        WHERE source = 'ph' AND created_at > datetime('now', '-24 hours')
        ORDER BY created_at DESC LIMIT 5
    """)
    results = cursor.fetchall()
    conn.close()
    return [{"title": r[0], "url": r[1], "score": r[2]} for r in results]

def format_intel_report() -> str:
    """Format the intelligence report - topic first"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    sections = [f"🎯 *Content Intel* ({now})\n"]

    # Trending Topics (multi-platform signals)
    topics = get_trending_topics()
    if topics:
        sections.append("*🔥 TRENDING TOPICS*")
        for topic, data in list(topics.items())[:6]:
            sources_str = ", ".join(sorted(data["sources"]))
            platform_indicator = "🔴" if data["platform_count"] >= 3 else "🟡" if data["platform_count"] >= 2 else "⚪"
            sections.append(f"{platform_indicator} *{topic.upper()}* `[{sources_str}]`")

            # Show top content for this topic
            content = get_content_for_topic(topic, limit=3)
            for item in content:
                score_str = f" ({item['score']}⬆)" if item['score'] > 0 else ""
                sections.append(f"   • [{item['title'][:60]}]({item['url']}){score_str}")
            sections.append("")

    # Fresh Launches
    launches = get_fresh_launches()
    if launches:
        sections.append("*🚀 FRESH LAUNCHES*")
        for launch in launches:
            sections.append(f"• [{launch['title']}]({launch['url']})")
        sections.append("")

    # Signal Legend
    sections.append("_🔴 3+ platforms | 🟡 2 platforms | ⚪ 1 platform_")

    return "\n".join(sections)

def main():
    import sys
    log("Content intel starting...")
    ensure_tables()

    skip_refresh = "--no-refresh" in sys.argv

    if not skip_refresh:
        # Gather from all sources
        all_content = []

        log("Fetching Hacker News...")
        all_content.extend(fetch_hackernews())

        log("Fetching Product Hunt...")
        all_content.extend(fetch_producthunt())

        log("Fetching Dev.to...")
        all_content.extend(fetch_devto())

        log("Fetching news...")
        all_content.extend(fetch_duckduckgo_news())

        log(f"Total items: {len(all_content)}")
        save_content(all_content)

    # Output report
    report = format_intel_report()
    print(report)

    # Save to file for morning briefing
    report_file = Path("/root/clawd/memory/content_intel_report.txt")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(report)

    log("Content intel complete")

if __name__ == "__main__":
    main()
