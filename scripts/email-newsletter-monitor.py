#!/usr/bin/env python3
"""
Email Newsletter Monitor - Extract trending topics from Ben's newsletter subscriptions
Pulls from Gmail, extracts key topics from newsletter content
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

# Newsletter senders to look for
NEWSLETTER_SENDERS = [
    'rundown',           # The Rundown AI
    'tldr',              # TLDR
    'morningbrew',       # Morning Brew
    'bensbites',         # Ben's Bites
    'superhuman',        # Superhuman AI
    'thehustle',         # The Hustle
    'lenny',             # Lenny's Newsletter
    'stratechery',       # Stratechery
    'producthunt',       # Product Hunt Daily
    'indiehackers',      # Indie Hackers
    'hackernewsletter',  # Hacker Newsletter
    'aiweekly',          # AI Weekly
    'techcrunch',        # TechCrunch
    'theprofile',        # The Profile
]

# Niche keywords for relevance scoring
NICHE_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'llm', 'gpt',
    'chatgpt', 'claude', 'gemini', 'openai', 'anthropic', 'deepseek',
    'automation', 'workflow', 'no-code', 'nocode', 'api', 'agent',
    'saas', 'startup', 'founder', 'indie', 'solopreneur', 'creator',
    'coding', 'developer', 'software', 'tech', 'app', 'launch',
    'mcp', 'cursor', 'copilot', 'midjourney', 'video', 'content'
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
        CREATE TABLE IF NOT EXISTS email_newsletters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            sender TEXT,
            snippet TEXT,
            topics TEXT,
            relevance_score INTEGER,
            email_id TEXT UNIQUE,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def parse_sse_response(response):
    if 'text/event-stream' in response.headers.get('content-type', ''):
        for line in response.text.split('\n'):
            if line.startswith('data:'):
                return json.loads(line[5:])
    return response.json()

def fetch_emails():
    """Fetch recent emails from Gmail - newsletters and updates"""
    try:
        response = requests.post(MCP_URL, headers=HEADERS, json={
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'COMPOSIO_MULTI_EXECUTE_TOOL',
                'arguments': {
                    'tools': [{
                        'tool_slug': 'GMAIL_FETCH_EMAILS',
                        'arguments': {
                            'max_results': 30
                        }
                    }]
                }
            },
            'id': 1
        }, timeout=30)

        result = parse_sse_response(response)
        if 'result' in result:
            data = json.loads(result['result']['content'][0]['text'])
            if data.get('successful'):
                # Navigate the nested response structure
                results = data.get('data', {}).get('results', [])
                if results:
                    response_data = results[0].get('response', {}).get('data_preview', {})
                    return response_data.get('messages', [])
        return []
    except Exception as e:
        log(f"Gmail fetch error: {e}")
        return []

def extract_topics(subject, snippet):
    """Extract topics/keywords from email subject and snippet"""
    text = f"{subject} {snippet}".lower()
    found_topics = []

    # Find matching niche keywords
    for kw in NICHE_KEYWORDS:
        if kw in text:
            found_topics.append(kw)

    # Extract capitalized phrases (likely product/company names)
    caps = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', f"{subject} {snippet}")
    for cap in caps[:5]:
        if len(cap) > 3 and cap.lower() not in ['the', 'and', 'for', 'with']:
            found_topics.append(cap)

    return list(set(found_topics))[:10]

def score_relevance(topics, text):
    """Score relevance to our niche"""
    score = 0
    text_lower = text.lower()
    for kw in NICHE_KEYWORDS:
        if kw in text_lower:
            score += 10
    return min(score, 100)

def process_emails(emails):
    """Process emails and extract newsletter content"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    for email in emails:
        try:
            email_id = email.get('messageId', '')
            subject = email.get('subject', '')
            sender = email.get('sender', '')
            # Get content from messageText or preview body
            snippet = email.get('messageText', email.get('preview', {}).get('body', ''))[:500]

            # Extract topics
            topics = extract_topics(subject, snippet)
            relevance = score_relevance(topics, f"{subject} {snippet}")

            # Only save if somewhat relevant
            if relevance >= 10:
                cursor.execute('''
                    INSERT OR IGNORE INTO email_newsletters
                    (subject, sender, snippet, topics, relevance_score, email_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (subject, sender, snippet, json.dumps(topics), relevance, email_id, now))

                if cursor.rowcount > 0:
                    saved += 1
                    log(f"Saved: {subject[:50]}... (relevance: {relevance})")
        except Exception as e:
            log(f"Process error: {e}")

    conn.commit()
    conn.close()
    return saved

def get_newsletter_topics():
    """Get recent newsletter topics for briefing"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT subject, sender, snippet, topics, relevance_score
        FROM email_newsletters
        WHERE created_at > datetime('now', '-48 hours')
        ORDER BY relevance_score DESC, created_at DESC
        LIMIT 10
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def main():
    log("Email Newsletter Monitor starting...")
    ensure_table()

    emails = fetch_emails()
    log(f"Fetched {len(emails)} emails")

    if emails:
        saved = process_emails(emails)
        log(f"Saved {saved} new newsletter items")

    # Show what we found
    topics = get_newsletter_topics()
    if topics:
        print("\n📬 NEWSLETTER TOPICS:")
        for subject, sender, snippet, topics_json, relevance in topics[:5]:
            print(f"\n[{relevance}] {subject[:60]}...")
            print(f"    From: {sender[:40]}")
            topics_list = json.loads(topics_json) if topics_json else []
            if topics_list:
                print(f"    Topics: {', '.join(topics_list[:5])}")

    log("Done")

if __name__ == "__main__":
    main()
