#!/usr/bin/env python3
"""
Weekly bookmark sync - run this to add new bookmarks
"""
import json
import os
import requests
from pathlib import Path
import subprocess

AIRTABLE_TOKEN = os.getenv('AIRTABLE_API_KEY') or Path('/root/.config/airtable/api_key').read_text().strip()
BASE_ID = 'app5ByPgxLUWzKsS0'
TABLE_NAME = 'Table%201'
HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}',
    'Content-Type': 'application/json'
}

def categorize_bookmark(text, author):
    text_lower = (text + ' ' + author).lower()
    categories = {
        'AI Tools & Coding': ['claude', 'gpt', 'ai agent', 'coding', 'vibe coding', 'llm', 'openai', 'cursor', 'replit', 'programming'],
        'SaaS Launch & Marketing': ['producthunt', 'launch', 'marketing', 'growth', 'affiliate', 'seo', 'landing page'],
        'No-Code & Automation': ['n8n', 'make.com', 'zapier', 'automation', 'no-code', 'workflow', 'notion', 'airtable'],
        'Content & Social': ['twitter', 'content', 'social media', 'post', 'thread', 'viral', 'engagement'],
        'Monetization': ['mrr', 'revenue', 'pricing', 'monetize', 'income', 'money', 'saas revenue'],
        'Development & Tech': ['api', 'github', 'react', 'javascript', 'python', 'database', 'server'],
        'Business Strategy': ['founder', 'startup', 'business', 'strategy', 'pivot', 'decision'],
        'Productivity & Tools': ['tool', 'app', 'software', 'productivity', 'efficiency'],
    }
    scores = {cat: sum(1 for kw in keywords if kw in text_lower) for cat, keywords in categories.items()}
    return max(scores, key=scores.get) if scores else 'Other'

def get_existing_ids():
    """Get tweet IDs already in Airtable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    existing = set()
    offset = None
    
    while True:
        params = {'fields': ['Notes'], 'maxRecords': 100}
        if offset:
            params['offset'] = offset
        
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        
        for record in data.get('records', []):
            notes = record.get('fields', {}).get('Notes', '')
            # Extract tweet ID from URL in notes
            if '/status/' in notes:
                tid = notes.split('/status/')[1].split('\n')[0].strip()
                existing.add(tid)
        
        offset = data.get('offset')
        if not offset:
            break
    
    return existing

def pull_x_bookmarks():
    """Pull bookmarks from X via bird CLI"""
    result = subprocess.run(
        ['bird', 'bookmarks', '-n', '500', '--json'],
        capture_output=True,
        text=True,
        env={**os.environ, 'AUTH_TOKEN': 'REDACTED_TWITTER_AUTH_TOKEN', 'CT0': 'REDACTED_TWITTER_CT0'}
    )
    return json.loads(result.stdout)

def add_to_airtable(bookmarks):
    """Add new bookmarks to Airtable"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    created = 0
    
    for i in range(0, len(bookmarks), 10):
        batch = bookmarks[i:i+10]
        records = []
        for b in batch:
            fields = {
                'Name': b['content'][:50] + '...' if len(b['content']) > 50 else b['content'],
                'Notes': f\"Author: @{b['author']}\nLikes: {b['likes']}\nCategory: {b['category']}\nURL: {b['url']}\n\n{b['content'][:400]}\""
            }
            records.append({'fields': fields})
        
        data = {'records': records}
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code == 200:
            created += len(batch)
            print(f'Added {created}/{len(bookmarks)}')
        else:
            print(f'Error: {response.text[:100]}')
    
    return created

if __name__ == '__main__':
    print('Checking for new bookmarks...')
    
    # Get existing IDs
    existing = get_existing_ids()
    print(f'Found {len(existing)} existing bookmarks in Airtable')
    
    # Pull from X
    x_bookmarks = pull_x_bookmarks()
    print(f'Pulled {len(x_bookmarks)} bookmarks from X')
    
    # Find new ones
    new_bookmarks = []
    for b in x_bookmarks:
        if b['id'] not in existing:
            category = categorize_bookmark(b.get('text', ''), b.get('author', {}).get('username', ''))
            new_bookmarks.append({
                'content': b.get('text', ''),
                'author': b.get('author', {}).get('username'),
                'url': f\"https://x.com/{b.get('author', {}).get('username')}/status/{b['id']}\",
                'likes': b.get('likeCount', 0),
                'category': category,
                'id': b['id']
            })
    
    if new_bookmarks:
        print(f'Found {len(new_bookmarks)} new bookmarks')
        # Sort by likes (highest first)
        new_bookmarks.sort(key=lambda x: x['likes'], reverse=True)
        created = add_to_airtable(new_bookmarks)
        print(f'Added {created} new bookmarks to Airtable')
    else:
        print('No new bookmarks found')
