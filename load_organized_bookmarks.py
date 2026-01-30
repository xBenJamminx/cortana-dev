#!/usr/bin/env python3
"""
Load bookmarks into organized Airtable table with proper columns
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
    # Load all bookmarks from the full export
    with open('/tmp/all_bookmarks_full.json') as f:
        data = json.load(f)
        all_tweets = data.get('tweets', [])
    
    print(f'Loading {len(all_tweets)} bookmarks to organized table...')
    created = add_to_airtable(all_tweets)
    print(f'Done! Added {created} bookmarks.')
