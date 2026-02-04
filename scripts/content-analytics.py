#!/usr/bin/env python3
"""
Content Analytics Engine - Topic-first intelligence
Detects trending topics, then finds related content across sources
"""
import sqlite3
import requests
import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/content-analytics.log")
SUMMARY_FILE = Path("/root/clawd/memory/content_analytics_summary.txt")

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
        CREATE TABLE IF NOT EXISTS trending_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            sources TEXT,
            score INTEGER,
            related_content TEXT,
            created_at TEXT,
            UNIQUE(topic, created_at)
        )
    ''')
    conn.commit()
    conn.close()

def get_google_trends_topics():
    """Get topics from Google Trends"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT term, traffic FROM google_trends
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        results = cursor.fetchall()
        conn.close()
        return [(r[0], r[1] or "trending") for r in results]
    except:
        return []

def get_twitter_topics():
    """Extract topics from trending tweets"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT text, likes FROM twitter_trends
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        results = cursor.fetchall()
        conn.close()

        # Extract keywords/hashtags from tweets
        topics = []
        # AI/tech keywords to look for
        hot_keywords = [
            'chatgpt', 'claude', 'gemini', 'deepseek', 'openai', 'anthropic',
            'gpt-4', 'gpt4', 'gpt-5', 'gpt5', 'llm', 'ai agent', 'ai agents',
            'automation', 'no-code', 'nocode', 'low-code', 'cursor', 'copilot',
            'midjourney', 'sora', 'dalle', 'stable diffusion', 'flux',
            'n8n', 'make.com', 'zapier', 'airtable', 'notion',
            'saas', 'indie hacker', 'solopreneur', 'creator economy',
            'viral', 'trending', 'launch', 'shipped', 'building in public',
            'vibe coding', 'vibe-coding', 'vibecoding'
        ]

        for text, likes in results:
            text_lower = text.lower()
            # Find hashtags
            hashtags = re.findall(r'#(\w+)', text)
            for tag in hashtags:
                topics.append((tag, max(likes or 0, 10)))
            # Find known keywords
            for kw in hot_keywords:
                if kw in text_lower:
                    topics.append((kw, max(likes or 0, 20)))
            # Find product names (capitalized words that could be products)
            products = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', text)  # CamelCase
            for p in products:
                if len(p) > 4:
                    topics.append((p.lower(), max(likes or 0, 15)))
        return topics
    except:
        return []

def get_exploding_topics():
    """Get topics from Exploding Topics"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT topic, growth FROM exploding_topics
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        results = cursor.fetchall()
        conn.close()
        return [(r[0], r[1] or "growing") for r in results]
    except:
        return []

def get_producthunt_topics():
    """Get product names from Product Hunt"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, votes FROM producthunt_posts
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        results = cursor.fetchall()
        conn.close()
        return [(r[0], r[1] or 0) for r in results]
    except:
        return []

def normalize_topic(topic):
    """Normalize topic for matching"""
    return re.sub(r'[^a-z0-9]', '', topic.lower())

def aggregate_topics():
    """Combine topics from all sources, score by frequency/engagement"""
    all_topics = {}
    
    # Google Trends (high signal)
    for topic, traffic in get_google_trends_topics():
        key = normalize_topic(topic)
        if key and len(key) > 2:
            if key not in all_topics:
                all_topics[key] = {"name": topic, "sources": [], "score": 0}
            all_topics[key]["sources"].append("google_trends")
            all_topics[key]["score"] += 100  # High weight for Google Trends
    
    # Twitter (engagement-based)
    for topic, likes in get_twitter_topics():
        key = normalize_topic(topic)
        if key and len(key) > 2:
            if key not in all_topics:
                all_topics[key] = {"name": topic, "sources": [], "score": 0}
            all_topics[key]["sources"].append("twitter")
            all_topics[key]["score"] += min(likes, 50)  # Cap at 50
    
    # Exploding Topics (emerging signal)
    for topic, growth in get_exploding_topics():
        key = normalize_topic(topic)
        if key and len(key) > 2:
            if key not in all_topics:
                all_topics[key] = {"name": topic, "sources": [], "score": 0}
            all_topics[key]["sources"].append("exploding_topics")
            all_topics[key]["score"] += 75  # Medium-high weight
    
    # Product Hunt (product launches)
    for topic, votes in get_producthunt_topics():
        key = normalize_topic(topic)
        if key and len(key) > 2:
            if key not in all_topics:
                all_topics[key] = {"name": topic, "sources": [], "score": 0}
            all_topics[key]["sources"].append("producthunt")
            all_topics[key]["score"] += min(votes, 30)  # Cap at 30
    
    # Sort by score
    ranked = sorted(all_topics.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:20]  # Top 20 topics

def find_related_content(topic_name):
    """Find content across sources related to a topic"""
    related = []
    topic_lower = topic_name.lower()
    topic_normalized = normalize_topic(topic_name)
    
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    
    # Search Twitter
    try:
        cursor.execute('''
            SELECT author, text, url FROM twitter_trends
            WHERE lower(text) LIKE ?
            AND created_at > datetime('now', '-48 hours')
            LIMIT 3
        ''', (f'%{topic_lower}%',))
        for row in cursor.fetchall():
            related.append({"type": "tweet", "author": row[0], "text": row[1][:100], "url": row[2]})
    except:
        pass
    
    # Search Dev.to/Hashnode
    try:
        cursor.execute('''
            SELECT title, url, source FROM devto_posts
            WHERE lower(title) LIKE ?
            AND created_at > datetime('now', '-48 hours')
            LIMIT 2
        ''', (f'%{topic_lower}%',))
        for row in cursor.fetchall():
            related.append({"type": "article", "title": row[0], "url": row[1], "source": row[2]})
    except:
        pass
    
    # Search YouTube
    try:
        cursor.execute('''
            SELECT title, channel, url FROM youtube_videos
            WHERE lower(title) LIKE ?
            AND created_at > datetime('now', '-48 hours')
            LIMIT 2
        ''', (f'%{topic_lower}%',))
        for row in cursor.fetchall():
            related.append({"type": "video", "title": row[0], "channel": row[1], "url": row[2]})
    except:
        pass
    
    # Search newsletters
    try:
        cursor.execute('''
            SELECT title, newsletter, url FROM substack_posts
            WHERE lower(title) LIKE ?
            AND created_at > datetime('now', '-48 hours')
            LIMIT 2
        ''', (f'%{topic_lower}%',))
        for row in cursor.fetchall():
            related.append({"type": "newsletter", "title": row[0], "source": row[1], "url": row[2]})
    except:
        pass
    
    # Search trending news
    try:
        cursor.execute('''
            SELECT title, source, url FROM trending_news
            WHERE lower(title) LIKE ?
            AND created_at > datetime('now', '-48 hours')
            LIMIT 2
        ''', (f'%{topic_lower}%',))
        for row in cursor.fetchall():
            related.append({"type": "news", "title": row[0], "source": row[1], "url": row[2]})
    except:
        pass
    
    conn.close()
    return related

def generate_analytics():
    """Generate the topic-first analytics"""
    topics = aggregate_topics()
    
    output = []
    output.append("🔥 TRENDING TOPICS — Content Opportunities\n")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    output.append("=" * 50 + "\n")
    
    for i, topic in enumerate(topics[:10], 1):
        name = topic["name"]
        sources = list(set(topic["sources"]))
        score = topic["score"]
        
        output.append(f"\n{i}. {name.upper()}")
        output.append(f"   Score: {score} | Sources: {', '.join(sources)}")
        
        # Find related content
        related = find_related_content(name)
        if related:
            output.append("   Related content:")
            for item in related[:3]:
                if item["type"] == "tweet":
                    output.append(f"   🐦 @{item['author']}: {item['text'][:60]}...")
                elif item["type"] == "video":
                    output.append(f"   📺 {item['title'][:50]} ({item['channel']})")
                elif item["type"] == "article":
                    output.append(f"   📝 {item['title'][:50]} [{item['source']}]")
                elif item["type"] == "newsletter":
                    output.append(f"   📬 {item['title'][:50]} ({item['source']})")
                elif item["type"] == "news":
                    output.append(f"   📰 {item['title'][:50]}")
        else:
            output.append("   ⚡ Fresh topic - no indexed content yet (opportunity!)")
    
    result = "\n".join(output)
    
    # Save summary
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_FILE.write_text(result)
    
    return result

def main():
    log("Content Analytics starting...")
    ensure_tables()
    
    result = generate_analytics()
    print(result)
    
    log("Done")

if __name__ == "__main__":
    main()
