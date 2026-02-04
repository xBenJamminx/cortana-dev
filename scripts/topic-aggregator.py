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

def normalize_title(text):
    """Clean up a title to be a proper topic name"""
    if not text:
        return ""
    # Remove common prefixes
    text = re.sub(r'^(Show HN:|Ask HN:|Launch HN:|Tell HN:)\s*', '', text)
    # Remove newlines (tweets often have them)
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Trim to reasonable length but keep it meaningful
    if len(text) > 100:
        # Try to cut at a natural break
        for sep in [' – ', ' - ', ': ', ' | ', '. ']:
            if sep in text[:100]:
                text = text[:text.index(sep)]
                break
        else:
            text = text[:100]
    return text.strip()

def is_good_title(text, source=''):
    """Check if text looks like a proper article/topic title, not a tweet"""
    if not text:
        return False

    # Twitter source = almost never a good title
    if 'twitter' in source.lower():
        return False

    # Reject if it looks like tweet garbage
    if text.count('@') > 0:  # Any mentions
        return False
    if text.count('→') > 0:  # Arrow formatting
        return False
    if '🧵' in text:  # Thread indicator
        return False
    if text.startswith(('I ', 'My ', 'We ', 'Im ', "I'm ", 'Just ', 'Woke ', 'People ')):
        return False
    if len(text) < 20:  # Too short
        return False
    if len(text.split()) < 4:  # Too few words
        return False
    # Check if it has proper capitalization (title case or sentence case)
    if text[0].islower():
        return False
    # Reject if mostly lowercase with random caps (tweet style)
    caps = sum(1 for c in text if c.isupper())
    if caps > 10:  # Too many caps = ALL CAPS or weird
        return False
    return True

def extract_topic_signature(text):
    """Extract a signature that can match similar topics across sources.
    For example: 'Xcode 26.3 coding agents' and 'Apple adds coding agents to Xcode'
    should match on 'xcode' + 'coding agent' or 'xcode' + 'agent'"""
    if not text:
        return set()

    text_lower = text.lower()
    signature = set()

    # Specific products/tools to look for
    markers = [
        'xcode', 'cursor', 'copilot', 'windsurf', 'vscode',
        'claude', 'chatgpt', 'gpt-4', 'gpt-5', 'gemini', 'grok', 'deepseek', 'llama', 'qwen',
        'openai', 'anthropic', 'google', 'apple', 'microsoft', 'meta',
        'mcp', 'langchain', 'langgraph', 'crewai', 'autogen',
        'n8n', 'zapier', 'make.com', 'composio', 'retell', 'vapi',
        'midjourney', 'sora', 'runway', 'flux', 'stable diffusion',
        'openclaw', 'clawdbot', 'ollama', 'huggingface',
        'deno', 'bun', 'rust', 'typescript', 'golang',
        'ghidra', 'docker', 'kubernetes', 'supabase', 'vercel', 'netlify',
    ]

    for marker in markers:
        if marker in text_lower:
            signature.add(marker)

    # Add key concepts that make topics specific
    concepts = [
        'coding agent', 'ai agent', 'voice agent',
        'open source', 'self-hosted', 'local llm',
        'bankruptcy', 'acquisition', 'funding', 'launch', 'release',
        'mcp server', 'reverse engineering',
    ]

    for concept in concepts:
        if concept in text_lower:
            signature.add(concept.replace(' ', '_'))

    return signature

def normalize_signature(sig):
    """Normalize signature for better matching"""
    normalized = set()
    for s in sig:
        # Treat coding_agent and ai_agent as equivalent
        if s in ('coding_agent', 'ai_agent', 'voice_agent'):
            normalized.add('agent')
        else:
            normalized.add(s)
    return normalized

def topics_match(sig1, sig2):
    """Check if two topic signatures are similar enough to be the same topic"""
    if not sig1 or not sig2:
        return False

    # Normalize signatures for comparison
    norm1 = normalize_signature(sig1)
    norm2 = normalize_signature(sig2)

    overlap = norm1 & norm2

    # Match if 2+ overlapping, OR if both have same specific product + agent concept
    if len(overlap) >= 2:
        return True

    # Also match if they share a specific product (not a generic company)
    specific_products = {'xcode', 'cursor', 'copilot', 'windsurf', 'claude', 'chatgpt',
                        'gemini', 'grok', 'deepseek', 'mcp', 'n8n', 'openclaw', 'deno', 'ollama'}
    shared_products = overlap & specific_products
    if shared_products and ('agent' in norm1 or 'agent' in norm2):
        return True

    return len(overlap) == 1 and len(sig1) == 1 and len(sig2) == 1

def fetch_reddit_hot(subreddit):
    """Fetch hot posts from a subreddit via JSON API"""
    import requests
    import time
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            posts = []
            for post in data.get('data', {}).get('children', []):
                p = post.get('data', {})
                posts.append({
                    'title': p.get('title', ''),
                    'url': f"https://reddit.com{p.get('permalink', '')}",
                    'score': p.get('score', 0),
                    'subreddit': subreddit
                })
            return posts
        return []
    except:
        return []

def gather_all_content():
    """Gather content from all sources - use FULL TITLES as potential topics"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    all_content = []

    # 0. Reddit (live fetch from key subreddits)
    reddit_subs = ['LocalLLaMA', 'ChatGPT', 'ClaudeAI', 'OpenAI', 'SideProject', 'SaaS', 'n8n']
    for sub in reddit_subs:
        try:
            posts = fetch_reddit_hot(sub)
            for p in posts[:5]:
                title = normalize_title(p['title'])
                sig = extract_topic_signature(title)
                if sig:  # Only include if it has relevant markers
                    all_content.append({
                        'title': title,
                        'source': f"reddit/r/{sub}",
                        'url': p['url'],
                        'signature': sig,
                        'engagement': f"{p['score']}⬆"
                    })
            import time
            time.sleep(0.5)
        except:
            pass

    # 1. HN / Real trends
    try:
        cursor.execute('''
            SELECT topic, source, url, traffic FROM real_trends
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for topic, source, url, traffic in cursor.fetchall():
            title = normalize_title(topic)
            sig = extract_topic_signature(title)
            if sig:
                all_content.append({
                    'title': title,
                    'source': source,
                    'url': url,
                    'signature': sig,
                    'engagement': traffic
                })
    except: pass

    # 2. IndieHackers
    try:
        cursor.execute('''
            SELECT title, url, score FROM indiehacker_posts
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for title, url, score in cursor.fetchall():
            title = normalize_title(title)
            sig = extract_topic_signature(title)
            if sig:
                all_content.append({
                    'title': title,
                    'source': 'indiehackers',
                    'url': url,
                    'signature': sig,
                    'engagement': f"{score}⬆"
                })
    except: pass

    # 3. YouTube
    try:
        cursor.execute('''
            SELECT title, channel, url FROM youtube_videos
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for title, channel, url in cursor.fetchall():
            title = normalize_title(title)
            sig = extract_topic_signature(title)
            if sig:
                all_content.append({
                    'title': title,
                    'source': f'youtube/{channel}',
                    'url': url,
                    'signature': sig,
                    'engagement': 'video'
                })
    except: pass

    # 4. Twitter
    try:
        cursor.execute('''
            SELECT text, author, url, likes FROM twitter_trends
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for text, author, url, likes in cursor.fetchall():
            # For tweets, use full text as title
            title = normalize_title(text)
            sig = extract_topic_signature(title)
            if sig:
                all_content.append({
                    'title': title,
                    'source': f'twitter/@{author}',
                    'url': url,
                    'signature': sig,
                    'engagement': f"{likes} likes"
                })
    except: pass

    # 5. Dev.to / Hashnode
    try:
        cursor.execute('''
            SELECT title, source, url, reactions FROM devto_posts
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for title, source, url, reactions in cursor.fetchall():
            title = normalize_title(title)
            sig = extract_topic_signature(title)
            if sig:
                all_content.append({
                    'title': title,
                    'source': source,
                    'url': url,
                    'signature': sig,
                    'engagement': f"{reactions} reactions"
                })
    except: pass

    # 6. Newsletters (Substack)
    try:
        cursor.execute('''
            SELECT title, newsletter, url FROM substack_posts
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for title, newsletter, url in cursor.fetchall():
            title = normalize_title(title)
            sig = extract_topic_signature(title)
            if sig:
                all_content.append({
                    'title': title,
                    'source': f'newsletter/{newsletter}',
                    'url': url,
                    'signature': sig,
                    'engagement': 'newsletter'
                })
    except: pass

    # 7. Email newsletters
    try:
        cursor.execute('''
            SELECT subject, sender, snippet FROM email_newsletters
            WHERE created_at > datetime('now', '-48 hours')
        ''')
        for subject, sender, snippet in cursor.fetchall():
            title = normalize_title(subject)
            sig = extract_topic_signature(f"{subject} {snippet}")
            if sig:
                sender_name = sender.split('<')[0].strip() if '<' in sender else sender[:20]
                all_content.append({
                    'title': title,
                    'source': f'email/{sender_name}',
                    'url': '',
                    'signature': sig,
                    'engagement': 'inbox'
                })
    except: pass

    # 8. Product Hunt
    try:
        cursor.execute('''
            SELECT title, tagline, url, votes FROM producthunt_posts
            WHERE created_at > datetime('now', '-24 hours')
        ''')
        for title, tagline, url, votes in cursor.fetchall():
            full_title = f"{title}: {tagline}" if tagline else title
            full_title = normalize_title(full_title)
            sig = extract_topic_signature(full_title)
            if sig:
                all_content.append({
                    'title': full_title,
                    'source': 'producthunt',
                    'url': url,
                    'signature': sig,
                    'engagement': f"{votes}⬆"
                })
    except: pass

    conn.close()
    return all_content

def aggregate_topics(all_content):
    """Find SPECIFIC topics that appear across multiple sources.
    Group similar content by signature matching, use best title as topic name."""

    # Group content by similar signatures
    clusters = []

    for item in all_content:
        sig = item['signature']
        source_type = item['source'].split('/')[0].split('@')[0]

        # Try to find existing cluster this matches
        matched = False
        for cluster in clusters:
            if topics_match(sig, cluster['signature']):
                # Add to existing cluster
                if source_type not in cluster['source_types']:
                    cluster['source_types'].add(source_type)
                    cluster['sources'].append(item['source'])
                cluster['items'].append(item)
                # Update signature to be union
                cluster['signature'] = cluster['signature'] | sig
                matched = True
                break

        if not matched:
            # Start new cluster
            clusters.append({
                'signature': sig,
                'source_types': {source_type},
                'sources': [item['source']],
                'items': [item]
            })

    # Convert clusters to hot topics (only if 2+ source types)
    hot_topics = []
    for cluster in clusters:
        if len(cluster['source_types']) >= 2:
            items = cluster['items']

            # Find the best title - prefer good titles over long ones
            good_titles = [i for i in items if is_good_title(i['title'], i.get('source', ''))]
            if good_titles:
                best_title = max(good_titles, key=lambda x: len(x['title']))['title']
            else:
                # Fall back to longest if no good titles
                best_title = max(items, key=lambda x: len(x['title']))['title']

            # Clean up the title one more time
            best_title = normalize_title(best_title)

            hot_topics.append({
                'topic': best_title,
                'source_count': len(cluster['source_types']),
                'sources': list(cluster['source_types']),
                'mentions': [
                    {
                        'source_type': i['source'].split('/')[0],
                        'source_full': i['source'],
                        'text': i['title'],
                        'url': i['url'],
                        'engagement': i['engagement']
                    }
                    for i in items[:5]
                ],
                'total_mentions': len(items)
            })

    # Score topics by: source count + relevance boost for builder topics
    # Builder-relevant markers get a boost
    builder_markers = {
        'xcode', 'cursor', 'copilot', 'windsurf', 'vscode', 'neovim',
        'claude', 'chatgpt', 'gemini', 'deepseek', 'llama', 'qwen',
        'mcp', 'langchain', 'langgraph', 'crewai', 'autogen',
        'n8n', 'zapier', 'composio', 'retell', 'vapi',
        'openclaw', 'ollama', 'huggingface', 'supabase', 'vercel',
        'deno', 'typescript', 'rust', 'golang',
        'coding_agent', 'ai_agent', 'voice_agent', 'mcp_server',
        'open_source', 'self-hosted', 'local_llm', 'launch', 'release',
    }

    # News/boring markers get penalized
    news_markers = {'raided', 'investigation', 'lawsuit', 'arrested', 'died', 'war', 'election'}

    for ht in hot_topics:
        sig = set()
        for item in ht.get('mentions', []):
            text_lower = item.get('text', '').lower()
            for marker in builder_markers:
                if marker.replace('_', ' ') in text_lower or marker in text_lower:
                    sig.add(marker)

        # Calculate relevance score
        builder_score = len(sig & builder_markers)
        news_penalty = sum(1 for m in news_markers if m in ht['topic'].lower())

        # Final score: source_count + builder_boost - news_penalty
        ht['relevance_score'] = ht['source_count'] + (builder_score * 0.5) - (news_penalty * 2)

    # Sort by relevance score, then source count
    hot_topics.sort(key=lambda x: (x.get('relevance_score', 0), x['source_count'], x['total_mentions']), reverse=True)

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
