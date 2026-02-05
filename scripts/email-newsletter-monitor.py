#!/usr/bin/env python3
"""
Email Newsletter Monitor v2 - Extract content topics from Ben's AI/creator newsletters
Uses GMAIL_LIST_THREADS + GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID for reliable data
"""
import sqlite3
import json
import re
import requests
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/email-newsletters.log")

MCP_URL = 'https://backend.composio.dev/tool_router/trs_r19DmEN65WU9/mcp'
API_KEY = 'REDACTED_COMPOSIO_MCP_KEY'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream',
    'x-api-key': API_KEY
}

# AI/Creator newsletters we care about (from Ben's actual inbox)
# Format: sender email fragment -> display name
NEWSLETTER_WHITELIST = {
    'therundown': 'The Rundown AI',
    'rundownai': 'The Rundown AI',
    'aiforwork': 'AI For Work',
    'unwindai': 'Unwind AI',
    'whatsupinai': "What's Up in AI",
    'dailybite@mail.beehiiv': 'Snack Prompt',
    'snackprompt': 'Snack Prompt',
    'socialgrowthengineer': 'Social Growth Engineers',
    'wavy@mail.beehiiv': 'Kallaway',
    'kallaway': 'Kallaway',
    'unicorne@mail.beehiiv': 'Marc Lou',
    'marclou': 'Marc Lou',
    'hypefury': 'Hypefury',
    'lenny': "Lenny's Newsletter",
    'tinylaunch': 'TinyLaunch',
    'tinylog': 'TinyLaunch',
    'ideabrowser': 'Ideabrowser',
    'bensbites': "Ben's Bites",
    'superhuman': 'Superhuman AI',
    'tldr': 'TLDR',
    'theneuron': 'The Neuron',
    'producthunt': 'Product Hunt',
}

# Senders to SKIP (crypto, not relevant)
SENDER_BLACKLIST = [
    'dailybones',       # The Daily Bone (crypto)
    'luckytrader',      # Morning Minute (crypto)
    'circleboom',       # Social tool notifications
    'noreply-apps-scripts',  # Google Apps Script
]

# Topics relevant to Ben's niche
NICHE_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt',
    'chatgpt', 'claude', 'gemini', 'openai', 'anthropic', 'deepseek',
    'automation', 'workflow', 'no-code', 'nocode', 'api', 'agent',
    'saas', 'startup', 'founder', 'indie', 'solopreneur', 'creator',
    'coding', 'vibecod', 'developer', 'software', 'app', 'launch',
    'mcp', 'cursor', 'copilot', 'midjourney', 'video', 'content',
    'tool', 'build', 'ship', 'product', 'revenue', 'mrr', 'growth',
    'n8n', 'make.com', 'zapier', 'retell', 'vapi', 'elevenlabs',
]

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def ensure_table():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            sender_name TEXT,
            sender_email TEXT,
            content TEXT,
            topics TEXT,
            links TEXT,
            relevance_score INTEGER,
            email_id TEXT UNIQUE,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def composio_call(tools):
    """Make a Composio multi-execute call"""
    try:
        response = requests.post(MCP_URL, headers=HEADERS, json={
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'COMPOSIO_MULTI_EXECUTE_TOOL',
                'arguments': {'tools': tools}
            },
            'id': 1
        }, timeout=60)

        for line in response.text.split('\n'):
            if line.startswith('data:'):
                data = json.loads(line[5:])
                text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if text:
                    return json.loads(text)
        return None
    except Exception as e:
        log(f"Composio call error: {e}")
        return None

def is_whitelisted(sender_email):
    """Check if sender is in our whitelist"""
    sender_lower = sender_email.lower()
    for fragment in NEWSLETTER_WHITELIST:
        if fragment in sender_lower:
            return True
    return False

def is_blacklisted(sender_email):
    """Check if sender is blacklisted"""
    sender_lower = sender_email.lower()
    for fragment in SENDER_BLACKLIST:
        if fragment in sender_lower:
            return True
    return False

def get_sender_name(sender_email):
    """Get friendly name for a sender"""
    sender_lower = sender_email.lower()
    for fragment, name in NEWSLETTER_WHITELIST.items():
        if fragment in sender_lower:
            return name
    return sender_email.split('<')[0].strip().strip('"')

def fetch_newsletter_threads():
    """Fetch recent newsletter threads using GMAIL_LIST_THREADS"""
    # Build query for newsletter senders
    query = 'newer_than:2d (from:beehiiv OR from:substack OR from:newsletter OR from:rundown OR from:snackprompt OR from:aiforwork OR from:unwindai OR from:whatsupinai OR from:superhuman OR from:bensbites OR from:tldr OR from:theneuron OR from:hypefury OR from:ideabrowser OR from:producthunt)'

    result = composio_call([{
        'tool_slug': 'GMAIL_LIST_THREADS',
        'arguments': {
            'max_results': 50,
            'query': query
        }
    }])

    if not result or not result.get('successful'):
        log("Failed to list threads")
        return []

    results = result.get('data', {}).get('results', [])
    if not results:
        return []

    threads = results[0].get('response', {}).get('data', {}).get('threads', [])
    thread_ids = [t['id'] for t in threads]
    log(f"Found {len(thread_ids)} newsletter threads")

    if not thread_ids:
        return []

    # Fetch individual messages (batch of 20 at a time)
    messages = []
    for i in range(0, len(thread_ids), 20):
        batch = thread_ids[i:i+20]
        tools = [{'tool_slug': 'GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID', 'arguments': {'message_id': tid}} for tid in batch]

        result = composio_call(tools)
        if not result or not result.get('successful'):
            continue

        for r in result.get('data', {}).get('results', []):
            if isinstance(r, str):
                continue
            resp = r.get('response', {})
            msg_data = resp.get('data', resp.get('data_preview', {}))
            if msg_data:
                messages.append(msg_data)

    log(f"Fetched {len(messages)} message details")
    return messages

def extract_content_topics(subject, content):
    """Extract meaningful content topics from newsletter text"""
    text = f"{subject} {content}".lower()
    found = []

    # Find niche keyword matches
    for kw in NICHE_KEYWORDS:
        if kw in text:
            found.append(kw)

    # Extract product/company names (capitalized words)
    caps = re.findall(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b', f"{subject} {content}")
    known_products = ['Claude', 'ChatGPT', 'Gemini', 'OpenAI', 'Anthropic', 'DeepSeek',
                      'Cursor', 'Copilot', 'Midjourney', 'Grok', 'Perplexity', 'Sora',
                      'Codex', 'Xcode', 'GitHub', 'Vercel', 'Supabase', 'Retell', 'Vapi',
                      'ElevenLabs', 'Composio', 'Windsurf', 'Bolt', 'Lovable', 'Replit',
                      'Google', 'Apple', 'Meta', 'Microsoft', 'Amazon', 'Tesla', 'SpaceX']
    for cap in caps:
        if cap in known_products and cap.lower() not in found:
            found.append(cap)

    # Extract key phrases that indicate content-worthy stories
    story_patterns = [
        r'launch(?:ed|es|ing)',
        r'releas(?:ed|es|ing)',
        r'announc(?:ed|es|ing)',
        r'introduc(?:ed|es|ing)',
        r'new (?:tool|feature|model|update|version)',
        r'\$[\d,.]+[KMB]?\s+(?:ARR|MRR|revenue)',
        r'raised? \$[\d,.]+[KMB]',
        r'open.?sourc',
    ]
    for pattern in story_patterns:
        if re.search(pattern, text):
            match_context = re.search(r'(.{0,30}' + pattern + r'.{0,30})', text)
            if match_context:
                found.append(f"[story] {match_context.group(0).strip()[:60]}")

    return list(set(found))[:15]

def score_relevance(topics, text):
    """Score relevance to Ben's niche"""
    score = 0
    text_lower = text.lower()

    # Core AI topics worth more
    high_value = ['ai', 'automation', 'agent', 'vibecod', 'no-code', 'nocode',
                  'claude', 'mcp', 'cursor', 'build', 'ship', 'launch', 'tool']
    for kw in high_value:
        if kw in text_lower:
            score += 15

    # General relevance
    for kw in NICHE_KEYWORDS:
        if kw in text_lower and kw not in high_value:
            score += 5

    return min(score, 100)

def extract_links(content):
    """Extract useful links from newsletter content"""
    if not content:
        return []
    urls = re.findall(r'https?://[^\s\)>\]\*]+', content)
    good_urls = []
    skip_patterns = ['unsubscribe', 'beehiiv.com/cdn', 'tracking', 'click.', 'manage',
                     'preferences', 'mailchimp', 'list-manage', 'email.', 'mailto',
                     'beacon', 'pixel', 'open.substack', 'cdn-cgi', 'fonts.', 'static.']
    for u in urls:
        u_clean = u.rstrip('.,;:')
        u_lower = u_clean.lower()
        if any(s in u_lower for s in skip_patterns):
            continue
        if len(u_clean) < 15:
            continue
        good_urls.append(u_clean)
        if len(good_urls) >= 5:
            break
    return good_urls

def clean_snippet(content, max_len=200):
    """Clean newsletter content into a readable snippet"""
    if not content:
        return ""
    # Remove image references and captions
    text = re.sub(r'View image:.*?\)', '', content)
    text = re.sub(r'Caption:.*?(?:\n|$)', '', text)
    text = re.sub(r'Follow ima.*?(?:\n|$)', '', text)
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove formatting noise
    text = re.sub(r'[─═╌\-]{3,}', ' ', text)  # horizontal rules
    text = re.sub(r'[â]+', '', text)  # unicode box chars
    text = re.sub(r'\*{1,2}', '', text)  # bold markers
    text = re.sub(r'#{1,3}\s*', '', text)  # headers
    text = re.sub(r'\^', '', text)
    text = re.sub(r'View this post on the web at\s*\S+\s*', '', text)
    text = re.sub(r'Read Online\s*', '', text)
    text = re.sub(r'https?://\S+', '', text)  # strip URLs from snippet
    text = re.sub(r'GMGM,?\s*', '', text)
    text = re.sub(r'SPONSORED BY\s+\S+', '', text)
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Skip if too short after cleaning
    if len(text) < 10:
        return ""
    # Truncate
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + '...'
    return text

def process_messages(messages):
    """Process fetched messages and save relevant ones"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0
    skipped_blacklist = 0
    skipped_relevance = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    for msg in messages:
        try:
            email_id = msg.get('messageId', msg.get('id', ''))
            subject = msg.get('subject', '')
            sender_raw = msg.get('sender', msg.get('from', ''))
            raw_content = msg.get('messageText', msg.get('snippet', ''))

            # Skip blacklisted senders
            if is_blacklisted(sender_raw):
                skipped_blacklist += 1
                continue

            sender_name = get_sender_name(sender_raw)
            full_text = f"{subject} {raw_content or ''}"

            # Extract topics, links, and clean snippet
            topics = extract_content_topics(subject, raw_content or '')
            links = extract_links(raw_content or '')
            snippet = clean_snippet(raw_content or '')
            relevance = score_relevance(topics, full_text)

            # Only save if relevant enough
            if relevance >= 15:
                cursor.execute('''
                    INSERT OR IGNORE INTO newsletter_topics
                    (subject, sender_name, sender_email, content, topics, links, relevance_score, email_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (subject, sender_name, sender_raw, snippet, json.dumps(topics),
                      json.dumps(links), relevance, email_id, now))

                if cursor.rowcount > 0:
                    saved += 1
                    log(f"[{relevance}] {sender_name}: {subject[:50]}")
            else:
                skipped_relevance += 1
        except Exception as e:
            log(f"Process error: {e}")

    conn.commit()
    conn.close()
    log(f"Saved {saved} | Skipped: {skipped_blacklist} blacklisted, {skipped_relevance} low relevance")
    return saved

def get_content_topics_for_briefing():
    """Get top newsletter topics for the morning briefing"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT subject, sender_name, content, topics, links, relevance_score
        FROM newsletter_topics
        WHERE created_at > datetime('now', '-36 hours')
        ORDER BY relevance_score DESC, created_at DESC
        LIMIT 10
    ''')
    results = []
    for row in cursor.fetchall():
        subject, sender, content, topics_json, links_json, relevance = row
        results.append({
            'subject': subject,
            'sender': sender,
            'content': content or '',
            'topics': json.loads(topics_json) if topics_json else [],
            'links': json.loads(links_json) if links_json else [],
            'relevance': relevance
        })
    conn.close()
    return results

def main():
    log("Newsletter Monitor v2 starting...")
    ensure_table()

    messages = fetch_newsletter_threads()

    if messages:
        saved = process_messages(messages)
    else:
        log("No newsletter messages found")

    # Show what we found
    topics = get_content_topics_for_briefing()
    if topics:
        print(f"\n📬 NEWSLETTER CONTENT TOPICS ({len(topics)} stories):")
        for t in topics:
            print(f"\n[{t['relevance']}] {t['sender']}: {t['subject'][:70]}")
            if t['content']:
                print(f"    {t['content'][:150]}")
            if t['links']:
                for link in t['links'][:2]:
                    print(f"    🔗 {link[:100]}")
            topic_tags = [tag for tag in t['topics'] if not tag.startswith('[story]')][:5]
            if topic_tags:
                print(f"    Tags: {', '.join(topic_tags)}")

    log("Done")

if __name__ == "__main__":
    main()
