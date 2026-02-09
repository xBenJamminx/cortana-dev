#!/usr/bin/env python3
"""
Twitter Topic Extractor - Extract WHAT people are talking about on Twitter
Not raw tweet text, but actual topics with post counts.

Approach:
1. Search high-engagement tweets on tech keywords
2. Extract topics from tweets (entities, keywords, linked content)
3. Cluster similar topics and count mentions
4. Output: "Topic X - 500 posts" style like X's Today's News
"""
import sqlite3
import subprocess
import json
import re
import requests
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/twitter-topic-extractor.log")

# Tech-focused search queries
SEARCHES = [
    "Claude AI min_faves:50",
    "ChatGPT min_faves:100",
    "OpenAI min_faves:100",
    "Anthropic min_faves:50",
    "AI agent min_faves:50",
    "Cursor AI min_faves:50",
    "MCP server min_faves:30",
    "Xcode agent min_faves:30",
    "LLM min_faves:100",
    "GPT-5 min_faves:50",
    "indie hacker min_faves:50",
    "side project launched min_faves:30",
    "open source AI min_faves:50",
    "vibe coding min_faves:30",
    "n8n automation min_faves:30",
]

# Known entities to detect
ENTITIES = {
    # AI Companies
    'anthropic': 'Anthropic',
    'openai': 'OpenAI',
    'google ai': 'Google AI',
    'meta ai': 'Meta AI',
    'mistral': 'Mistral AI',
    'deepseek': 'DeepSeek',

    # AI Products
    'claude': 'Claude',
    'claude code': 'Claude Code',
    'chatgpt': 'ChatGPT',
    'gpt-4': 'GPT-4',
    'gpt-5': 'GPT-5',
    'gemini': 'Gemini',
    'grok': 'Grok',
    'copilot': 'GitHub Copilot',
    'cursor': 'Cursor',
    'windsurf': 'Windsurf',

    # Tech
    'mcp': 'MCP (Model Context Protocol)',
    'xcode': 'Xcode',
    'vscode': 'VS Code',
    'ollama': 'Ollama',
    'hugging face': 'Hugging Face',
    'huggingface': 'Hugging Face',

    # Concepts
    'ai agent': 'AI Agents',
    'coding agent': 'Coding Agents',
    'vibe coding': 'Vibe Coding',
    'no code': 'No-Code',
    'low code': 'Low-Code',
}

import os
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "REDACTED_TWITTER_AUTH_TOKEN")
CT0 = os.environ.get("CT0", "1feded6ef927dcaaa873bf8000f6fa59aaee85ace1e5c1060b2cc8ad35e6f6a3b15eb5c982af43e3e12860266c4a8ecda849908e5751675f155de353e24e868035ccaa0a3080b301b40cb09964e5e90b")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def search_twitter(query):
    """Search Twitter using bird CLI"""
    try:
        result = subprocess.run(
            ["bird", "search", query, "--json", "-n", "20",
             "--auth-token", AUTH_TOKEN, "--ct0", CT0],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []

        tweets = []
        try:
            data = json.loads(result.stdout)
            for tweet in data if isinstance(data, list) else data.get("tweets", []):
                author = tweet.get("author", {}).get("username", "") or tweet.get("user", {}).get("screen_name", "")
                tweets.append({
                    "text": tweet.get("text", "") or tweet.get("full_text", ""),
                    "author": author,
                    "likes": tweet.get("favorite_count", 0) or tweet.get("public_metrics", {}).get("like_count", 0),
                    "urls": extract_urls(tweet)
                })
        except json.JSONDecodeError:
            pass
        return tweets
    except:
        return []

def extract_urls(tweet):
    """Extract URLs from tweet"""
    urls = []
    # From entities
    entities = tweet.get("entities", {})
    for url_obj in entities.get("urls", []):
        expanded = url_obj.get("expanded_url", "") or url_obj.get("url", "")
        if expanded and "twitter.com" not in expanded and "t.co" not in expanded:
            urls.append(expanded)
    # Fallback: regex
    if not urls:
        text = tweet.get("text", "") or tweet.get("full_text", "")
        found = re.findall(r'https?://[^\s]+', text)
        urls = [u for u in found if "twitter.com" not in u and "t.co" not in u]
    return urls

def fetch_page_title(url):
    """Fetch the title of a linked page"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; TrendBot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        if resp.status_code == 200:
            # Extract title
            match = re.search(r'<title[^>]*>([^<]+)</title>', resp.text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up common suffixes
                for suffix in [' | Hacker News', ' - YouTube', ' | LinkedIn', ' — Medium']:
                    title = title.replace(suffix, '')
                return title[:150]
    except:
        pass
    return None

def extract_topics_from_tweet(tweet):
    """Extract topic signals from a tweet"""
    text = tweet.get("text", "").lower()
    topics = []

    # 1. Detect known entities
    for keyword, entity_name in ENTITIES.items():
        if keyword in text:
            topics.append({
                'name': entity_name,
                'type': 'entity',
                'confidence': 'high'
            })

    # 2. If tweet has URLs, fetch the actual content title
    for url in tweet.get("urls", [])[:2]:  # Max 2 URLs
        title = fetch_page_title(url)
        if title and len(title) > 15:
            topics.append({
                'name': title,
                'type': 'linked_content',
                'url': url,
                'confidence': 'high'
            })

    return topics

def aggregate_topics(all_tweets):
    """Aggregate topics across all tweets and count mentions"""
    topic_counts = defaultdict(lambda: {
        'count': 0,
        'total_likes': 0,
        'examples': [],
        'type': 'entity',
        'urls': set()
    })

    for tweet in all_tweets:
        topics = extract_topics_from_tweet(tweet)
        for topic in topics:
            name = topic['name']
            topic_counts[name]['count'] += 1
            topic_counts[name]['total_likes'] += tweet.get('likes', 0)
            topic_counts[name]['type'] = topic['type']
            if topic.get('url'):
                topic_counts[name]['urls'].add(topic['url'])
            if len(topic_counts[name]['examples']) < 3:
                topic_counts[name]['examples'].append({
                    'author': tweet.get('author', ''),
                    'text': tweet.get('text', '')[:100],
                    'likes': tweet.get('likes', 0)
                })

    # Convert to list and sort by engagement
    results = []
    for name, data in topic_counts.items():
        results.append({
            'topic': name,
            'post_count': data['count'],
            'total_engagement': data['total_likes'],
            'type': data['type'],
            'urls': list(data['urls'])[:3],
            'examples': data['examples']
        })

    # Sort by post count * engagement weight
    results.sort(key=lambda x: x['post_count'] * (1 + x['total_engagement']/100), reverse=True)
    return results

def cluster_similar_topics(topics):
    """Merge similar topics (e.g., 'Claude' and 'Claude Code')"""
    # Simple clustering: if one topic name contains another, merge
    merged = {}

    for topic in topics:
        name = topic['topic']
        name_lower = name.lower()

        # Check if this is a subset of existing topic
        merged_into = None
        for existing_name in list(merged.keys()):
            existing_lower = existing_name.lower()
            if name_lower in existing_lower or existing_lower in name_lower:
                # Merge into the longer/more specific one
                if len(name) > len(existing_name):
                    # This topic is more specific, use it
                    merged[name] = merged.pop(existing_name)
                    merged[name]['post_count'] += topic['post_count']
                    merged[name]['total_engagement'] += topic['total_engagement']
                    merged_into = name
                else:
                    # Existing is more specific, merge into it
                    merged[existing_name]['post_count'] += topic['post_count']
                    merged[existing_name]['total_engagement'] += topic['total_engagement']
                    merged_into = existing_name
                break

        if not merged_into:
            merged[name] = topic

    return sorted(merged.values(), key=lambda x: x['post_count'], reverse=True)

def save_topics(topics):
    """Save extracted topics to database"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS twitter_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            post_count INTEGER,
            total_engagement INTEGER,
            topic_type TEXT,
            urls TEXT,
            created_at TEXT,
            UNIQUE(topic, created_at)
        )
    ''')

    now = datetime.now().strftime("%Y-%m-%d %H:00")
    saved = 0

    for t in topics[:30]:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO twitter_topics
                (topic, post_count, total_engagement, topic_type, urls, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                t['topic'], t['post_count'], t['total_engagement'],
                t['type'], json.dumps(t.get('urls', [])), now
            ))
            saved += 1
        except:
            pass

    conn.commit()
    conn.close()
    return saved

def format_todays_news(topics):
    """Format output like X's Today's News"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"📰 *Today's Tech News* ({now})\n"]

    for t in topics[:15]:
        post_str = f"{t['post_count']} posts" if t['post_count'] > 1 else "1 post"
        engagement = t['total_engagement']
        eng_str = f" · {engagement:,}+ likes" if engagement > 100 else ""

        # Determine category
        if t['type'] == 'linked_content':
            category = "Article"
        elif any(x in t['topic'].lower() for x in ['openai', 'anthropic', 'google', 'meta', 'microsoft']):
            category = "Company"
        elif any(x in t['topic'].lower() for x in ['agent', 'coding', 'vibe']):
            category = "Trend"
        else:
            category = "Tech"

        lines.append(f"**{t['topic']}**")
        lines.append(f"  {category} · {post_str}{eng_str}")

        # Show one example tweet
        if t['examples']:
            ex = t['examples'][0]
            lines.append(f"  └ @{ex['author']}: \"{ex['text'][:60]}...\"")

        lines.append("")

    return "\n".join(lines)

def main():
    log("Twitter Topic Extractor starting...")

    # Gather tweets from all searches
    all_tweets = []
    for query in SEARCHES:
        log(f"Searching: {query}")
        tweets = search_twitter(query)
        all_tweets.extend(tweets)
        log(f"  Found {len(tweets)} tweets")

    log(f"Total tweets: {len(all_tweets)}")

    # Extract and aggregate topics
    topics = aggregate_topics(all_tweets)
    log(f"Extracted {len(topics)} raw topics")

    # Cluster similar topics
    topics = cluster_similar_topics(topics)
    log(f"After clustering: {len(topics)} topics")

    # Save to database
    saved = save_topics(topics)
    log(f"Saved {saved} topics")

    # Output formatted
    output = format_todays_news(topics)
    print(output)

    # Save to file
    output_file = Path("/root/clawd/memory/twitter_topics.md")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(output)

    log("Done")

if __name__ == "__main__":
    main()
