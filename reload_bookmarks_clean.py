#!/usr/bin/env python3
"""
Reload non-political bookmarks to Airtable
"""
import json
import os
import requests
from pathlib import Path

AIRTABLE_TOKEN = os.getenv('AIRTABLE_API_KEY') or Path('/root/.config/airtable/api_key').read_text().strip()
BASE_ID = 'app5ByPgxLUWzKsS0'
TABLE_NAME = 'Bookmarks%20(Organized)'
HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}',
    'Content-Type': 'application/json'
}

POLITICAL_KEYWORDS = ['trump', 'biden', 'election', 'vote', 'democrat', 'republican', 
                      'political', 'politics', 'government', 'congress', 'senate', 
                      'liberal', 'conservative', 'leftist', 'woke', 'maga', 'policy', 
                      'president', 'campaign', 'epstein', 'fbi', 'doj']

def is_political(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in POLITICAL_KEYWORDS)

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

def clear_table():
    """Delete all existing records"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    all_records = []
    offset = None
    
    while True:
        params = {'fields': [], 'maxRecords': 100}
        if offset:
            params['offset'] = offset
        
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        all_records.extend(data.get('records', []))
        
        offset = data.get('offset')
        if not offset:
            break
    
    print(f'Clearing {len(all_records)} existing records...')
    for record in all_records:
        delete_url = f'{url}/{record["id"]}'
        requests.delete(delete_url, headers=HEADERS)
    
    print(f'Cleared {len(all_records)} records')

def add_to_airtable(bookmarks):
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    created = 0
    
    for i in range(0, len(bookmarks), 10):
        batch = bookmarks[i:i+10]
        records = []
        for b in batch:
            fields = {
                'Content': b.get('text', ''),
                'Author': f"@{b.get('author', {}).get('username', '')}",
                'Author Name': b.get('author', {}).get('name', ''),
                'Likes': b.get('likeCount', 0),
                'Retweets': b.get('retweetCount', 0),
                'Replies': b.get('replyCount', 0),
                'Category': categorize_bookmark(b.get('text', ''), b.get('author', {}).get('username', '')),
                'URL': f"https://x.com/{b.get('author', {}).get('username')}/status/{b['id']}",
                'Has Media': 'Yes' if b.get('media') else 'No',
                'Created At': b.get('createdAt', ''),
                'Status': 'Todo'
            }
            records.append({'fields': fields})
        
        data = {'records': records}
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code == 200:
            created += len(batch)
            print(f'Added {created}/{len(bookmarks)}')
        else:
            print(f'Error: {response.text[:200]}')
            break
    
    return created

if __name__ == '__main__':
    # Load all bookmarks
    with open('/tmp/all_bookmarks_full.json') as f:
        data = json.load(f)
        all_tweets = data.get('tweets', [])
    
    # Filter out political ones
    non_political = [t for t in all_tweets if not is_political(t.get('text', ''))]
    
    print(f'Total bookmarks: {len(all_tweets)}')
    print(f'Political (filtered out): {len(all_tweets) - len(non_political)}')
    print(f'Non-political to load: {len(non_political)}')
    
    # Clear and reload
    clear_table()
    
    print(f'\nLoading {len(non_political)} bookmarks...')
    created = add_to_airtable(non_political)
    print(f'\nDone! Added {created} bookmarks.')
