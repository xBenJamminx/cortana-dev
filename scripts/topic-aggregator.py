#!/usr/bin/env python3
"""
Topic Aggregator - Identify HOT TOPICS by finding what's mentioned across multiple sources

The goal: If "Claude Code" is mentioned on HN, Twitter, AND a newsletter, that's a hot topic.
Not just "here's articles from IndieHackers" but "here's what EVERYONE is talking about"
"""
import sqlite3
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/topic-aggregator.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def extract_keywords(text):
    """Extract meaningful keywords/phrases from text"""
    if not text:
        return []

    text_lower = text.lower()
    keywords = []

    # Known hot topics to look for (products, companies, concepts)
    known_topics = [
        'claude', 'claude code', 'chatgpt', 'gpt-4', 'gpt-5', 'openai', 'anthropic',
        'gemini', 'deepseek', 'mistral', 'llama', 'qwen', 'cursor', 'copilot',
        'mcp', 'model context protocol', 'ai agent', 'ai agents', 'agentic',
        'vibe coding', 'vibe-coding', 'coding agent', 'xcode', 'windsurf',
        'n8n', 'make.com', 'zapier', 'automation', 'workflow',
        'saas', 'micro-saas', 'indie hacker', 'solopreneur', 'bootstrapped',
        'no-code', 'nocode', 'low-code', 'api', 'sdk',
        'midjourney', 'sora', 'runway', 'flux', 'stable diffusion',
        'rag', 'vector', 'embedding', 'fine-tuning', 'fine tuning',
        'open source', 'self-hosted', 'local llm', 'ollama',
        'retell', 'vapi', 'voice ai', 'speech to text', 'tts',
        'composio', 'langchain', 'langgraph', 'crewai', 'autogen',
        'twitter', 'x algorithm', 'youtube algorithm', 'content creation',
        'deno', 'bun', 'typescript', 'rust', 'golang',
    ]

    for topic in known_topics:
        if topic in text_lower:
            # Normalize variations
            normalized = topic.replace('-', ' ').replace('.', ' ').strip()
            keywords.append(normalized)

    # Extract capitalized product/company names (2+ chars)
    caps = re.findall(r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)?)\b', text)
    for cap in caps:
        if len(cap) > 2 and cap.lower() not in ['the', 'and', 'for', 'with', 'this', 'that', 'from']:
            keywords.append(cap.lower())

    return list(set(keywords))

def gather_all_content():
    """Gather content from all sources with extracted keywords"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    all_content = []

    # 1. HN / Real trends
    try:
        cursor.execute('''
            SELECT topic, source, url, traffic FROM real_trends
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for topic, source, url, traffic in cursor.fetchall():
            keywords = extract_keywords(topic)
            if keywords:
                all_content.append({
                    'text': topic, 'source': source, 'url': url,
                    'keywords': keywords, 'engagement': traffic
                })
    except: pass

    # 2. IndieHackers
    try:
        cursor.execute('''
            SELECT title, url, score FROM indiehacker_posts
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for title, url, score in cursor.fetchall():
            keywords = extract_keywords(title)
            if keywords:
                all_content.append({
                    'text': title, 'source': 'indiehackers', 'url': url,
                    'keywords': keywords, 'engagement': f"{score}⬆"
                })
    except: pass

    # 3. YouTube
    try:
        cursor.execute('''
            SELECT title, channel, url FROM youtube_videos
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for title, channel, url in cursor.fetchall():
            keywords = extract_keywords(title)
            if keywords:
                all_content.append({
                    'text': title, 'source': f'youtube/{channel}', 'url': url,
                    'keywords': keywords, 'engagement': 'video'
                })
    except: pass

    # 4. Twitter
    try:
        cursor.execute('''
            SELECT text, author, url, likes FROM twitter_trends
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for text, author, url, likes in cursor.fetchall():
            keywords = extract_keywords(text)
            if keywords:
                all_content.append({
                    'text': text[:100], 'source': f'twitter/@{author}', 'url': url,
                    'keywords': keywords, 'engagement': f"{likes} likes"
                })
    except: pass

    # 5. Dev.to / Hashnode
    try:
        cursor.execute('''
            SELECT title, source, url, reactions FROM devto_posts
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for title, source, url, reactions in cursor.fetchall():
            keywords = extract_keywords(title)
            if keywords:
                all_content.append({
                    'text': title, 'source': source, 'url': url,
                    'keywords': keywords, 'engagement': f"{reactions} reactions"
                })
    except: pass

    # 6. Newsletters (Substack)
    try:
        cursor.execute('''
            SELECT title, newsletter, url FROM substack_posts
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for title, newsletter, url in cursor.fetchall():
            keywords = extract_keywords(title)
            if keywords:
                all_content.append({
                    'text': title, 'source': f'newsletter/{newsletter}', 'url': url,
                    'keywords': keywords, 'engagement': 'newsletter'
                })
    except: pass

    # 7. Email newsletters
    try:
        cursor.execute('''
            SELECT subject, sender, snippet FROM email_newsletters
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for subject, sender, snippet in cursor.fetchall():
            # Extract from both subject and snippet
            keywords = extract_keywords(f"{subject} {snippet}")
            if keywords:
                sender_name = sender.split('<')[0].strip() if '<' in sender else sender[:20]
                all_content.append({
                    'text': subject, 'source': f'email/{sender_name}', 'url': '',
                    'keywords': keywords, 'engagement': 'inbox'
                })
    except: pass

    # 8. Product Hunt
    try:
        cursor.execute('''
            SELECT title, tagline, url, votes FROM producthunt_posts
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for title, tagline, url, votes in cursor.fetchall():
            keywords = extract_keywords(f"{title} {tagline}")
            if keywords:
                all_content.append({
                    'text': f"{title}: {tagline}" if tagline else title,
                    'source': 'producthunt', 'url': url,
                    'keywords': keywords, 'engagement': f"{votes}⬆"
                })
    except: pass

    conn.close()
    return all_content

def aggregate_topics(all_content):
    """Find topics that appear across multiple sources"""

    # Map: keyword -> list of sources/content mentioning it
    topic_mentions = defaultdict(list)

    for item in all_content:
        # Get the base source type (strip specific channel/author)
        source_type = item['source'].split('/')[0].split('@')[0]

        for keyword in item['keywords']:
            topic_mentions[keyword].append({
                'source_type': source_type,
                'source_full': item['source'],
                'text': item['text'],
                'url': item['url'],
                'engagement': item['engagement']
            })

    # Score topics by how many DIFFERENT source types mention them
    hot_topics = []
    for keyword, mentions in topic_mentions.items():
        # Get unique source types
        source_types = set(m['source_type'] for m in mentions)

        # Only interested if mentioned in 2+ different source types
        if len(source_types) >= 2:
            hot_topics.append({
                'topic': keyword,
                'source_count': len(source_types),
                'sources': list(source_types),
                'mentions': mentions[:5],  # Keep top 5 examples
                'total_mentions': len(mentions)
            })

    # Sort by number of different sources, then by total mentions
    hot_topics.sort(key=lambda x: (x['source_count'], x['total_mentions']), reverse=True)

    return hot_topics

def save_hot_topics(hot_topics):
    """Save aggregated hot topics to database"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hot_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            source_count INTEGER,
            sources TEXT,
            mentions TEXT,
            created_at TEXT,
            UNIQUE(topic, created_at)
        )
    ''')

    now = datetime.now().strftime("%Y-%m-%d %H:00")  # Round to hour
    saved = 0

    for ht in hot_topics[:20]:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO hot_topics
                (topic, source_count, sources, mentions, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                ht['topic'], ht['source_count'],
                json.dumps(ht['sources']), json.dumps(ht['mentions']), now
            ))
            saved += 1
        except: pass

    conn.commit()
    conn.close()
    return saved

def get_hot_topics_for_briefing():
    """Get hot topics formatted for the morning briefing"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT topic, source_count, sources, mentions
        FROM hot_topics
        WHERE created_at > datetime('now', '-12 hours')
        ORDER BY source_count DESC, created_at DESC
        LIMIT 10
    ''')

    results = []
    for topic, source_count, sources_json, mentions_json in cursor.fetchall():
        sources = json.loads(sources_json)
        mentions = json.loads(mentions_json)
        results.append({
            'topic': topic,
            'source_count': source_count,
            'sources': sources,
            'mentions': mentions
        })

    conn.close()
    return results

def main():
    log("Topic Aggregator starting...")

    # Gather all content
    all_content = gather_all_content()
    log(f"Gathered {len(all_content)} items from all sources")

    # Find cross-source topics
    hot_topics = aggregate_topics(all_content)
    log(f"Found {len(hot_topics)} topics mentioned across multiple sources")

    # Save to database
    saved = save_hot_topics(hot_topics)
    log(f"Saved {saved} hot topics")

    # Print report
    print("\n🔥 HOT TOPICS (mentioned across multiple sources):\n")
    for ht in hot_topics[:15]:
        print(f"*{ht['topic'].upper()}* - {ht['source_count']} sources ({', '.join(ht['sources'])})")
        for m in ht['mentions'][:2]:
            print(f"  • {m['text'][:60]}... [{m['source_full']}]")
        print()

    log("Done")

if __name__ == "__main__":
    main()
