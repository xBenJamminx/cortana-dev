#!/usr/bin/env python3
"""
Add remaining bookmarks to Airtable
"""
import json
import os
import requests
from pathlib import Path

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
            if '/status/' in notes:
                tid = notes.split('/status/')[1].split('\n')[0].strip()
                existing.add(tid)
        
        offset = data.get('offset')
        if not offset:
            break
    
    return existing

def add_to_airtable(bookmarks):
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    created = 0
    
    for i in range(0, len(bookmarks), 10):
        batch = bookmarks[i:i+10]
        records = []
        for b in batch:
            fields = {
                'Name': b['content'][:50] + '...' if len(b['content']) > 50 else b['content'],
                'Notes': f"Author: @{b['author']}\nLikes: {b['likes']}\nCategory: {b['category']}\nURL: {b['url']}\n\n{b['content'][:400]}"
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
    # Load all bookmarks from the --all export
    with open('/tmp/all_bookmarks_full.json') as f:
        data = json.load(f)
        all_tweets = data.get('tweets', [])
    
    print(f'Total in export: {len(all_tweets)}')
    
    # Get existing IDs
    existing = get_existing_ids()
    print(f'Already in Airtable: {len(existing)}')
    
    # Find new ones
    new_bookmarks = []
    for b in all_tweets:
        if b['id'] not in existing:
            category = categorize_bookmark(b.get('text', ''), b.get('author', {}).get('username', ''))
            new_bookmarks.append({
                'content': b.get('text', ''),
                'author': b.get('author', {}).get('username'),
                'url': f"https://x.com/{b.get('author', {}).get('username')}/status/{b['id']}",
                'likes': b.get('likeCount', 0),
                'category': category,
                'id': b['id']
            })
    
    print(f'New to add: {len(new_bookmarks)}')
    
    if new_bookmarks:
        # Sort by likes (highest first)
        new_bookmarks.sort(key=lambda x: x['likes'], reverse=True)
        created = add_to_airtable(new_bookmarks)
        print(f'Added {created} new bookmarks')
    else:
        print('No new bookmarks to add')
