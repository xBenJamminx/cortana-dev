#!/usr/bin/env python3
"""
Create a new, comprehensive Airtable table and populate it with bookmarks.
"""
import json
import os
import requests
from pathlib import Path
import time

AIRTABLE_TOKEN = os.getenv('AIRTABLE_API_KEY') or Path('/root/.config/airtable/api_key').read_text().strip()
BASE_ID = 'appFPKQxzO0SClFdR' # Confirmed new Base ID
NEW_TABLE_NAME = 'Clawdbot Bookmarks' # New table name
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

def create_and_populate_bookmarks_table(base_id, table_name, bookmarks):
    # 1. Delete existing table if it exists (for a clean start)
    list_tables_url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
    response = requests.get(list_tables_url, headers=HEADERS)
    existing_tables = response.json().get('tables', [])
    
    for table in existing_tables:
        if table['name'] == table_name:
            print(f'Deleting existing table: {table_name} (ID: {table['id']})')
            delete_table_url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table['id']}'
            requests.delete(delete_table_url, headers=HEADERS)
            time.sleep(1) # Give Airtable time
            break

    # 2. Create the new table with all desired columns
    create_table_url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
    table_schema = {
        'name': table_name,
        'fields': [
            {'name': 'Content', 'type': 'multilineText'},
            {'name': 'Author', 'type': 'singleLineText'},
            {'name': 'Author Name', 'type': 'singleLineText'},
            {'name': 'Likes', 'type': 'number', 'options': {'precision': 0}},
            {'name': 'Retweets', 'type': 'number', 'options': {'precision': 0}},
            {'name': 'Replies', 'type': 'number', 'options': {'precision': 0}},
            {'name': 'Category', 'type': 'singleSelect', 'options': {'choices': [
                {'name': 'AI Tools & Coding', 'color': 'blueLight2'},
                {'name': 'SaaS Launch & Marketing', 'color': 'greenLight2'},
                {'name': 'No-Code & Automation', 'color': 'yellowLight2'},
                {'name': 'Content & Social', 'color': 'purpleLight2'},
                {'name': 'Monetization', 'color': 'orangeLight2'},
                {'name': 'Development & Tech', 'color': 'grayLight2'},
                {'name': 'Business Strategy', 'color': 'redLight2'},
                {'name': 'Productivity & Tools', 'color': 'cyanLight2'},
                {'name': 'Other', 'color': 'grayLight1'}
            ]}},
            {'name': 'URL', 'type': 'url'},
            {'name': 'Has Media', 'type': 'singleSelect', 'options': {'choices': [
                {'name': 'Yes', 'color': 'greenLight2'},
                {'name': 'No', 'color': 'grayLight1'}
            ]}},
            {'name': 'Created At', 'type': 'singleLineText'},
            {'name': 'Status', 'type': 'singleSelect', 'options': {'choices': [
                {'name': 'Todo', 'color': 'grayLight2'},
                {'name': 'In progress', 'color': 'yellowLight2'},
                {'name': 'Done', 'color': 'greenLight2'}
            ]}}
        ]
    }
    response = requests.post(create_table_url, headers=HEADERS, json=table_schema)
    new_table_id = response.json().get('id')
    print(f'Created new table: {table_name} (ID: {new_table_id})')
    time.sleep(1) # Give Airtable time

    # 3. Populate the new table with bookmarks
    add_url = f'https://api.airtable.com/v0/{base_id}/{new_table_id}'
    created = 0
    errors = 0
    
    print(f'Starting to add {len(bookmarks)} bookmarks to {table_name}...')
    for i in range(0, len(bookmarks), 10):
        batch = bookmarks[i:i+10]
        records = []
        for b in batch:
            fields = {
                'Content': b.get('text', '')[:500],
                'Author': f"@{b.get('author', {}).get('username', '')}",
                'Author Name': b.get('author', {}).get('name', ''),
                'Likes': b.get('likeCount', 0),
                'Retweets': b.get('retweetCount', 0),
                'Replies': b.get('replyCount', 0),
                'Category': categorize_bookmark(b.get('text', ''), b.get('author', {}).get('username', '')),
                'URL': f"https://x.com/{b.get('author', {}).get('username')}/status/{b['id']}",
                'Has Media': 'Yes' if b.get('media') else 'No',
                'Created At': b.get('createdAt', ''),
                'Status': 'Todo' # Default status
            }
            records.append({'fields': fields})
        
        data = {'records': records}
        response = requests.post(add_url, headers=HEADERS, json=data)
        
        if response.status_code == 200:
            created += len(batch)
            if created % 100 == 0:
                print(f'  Added {created}/{len(bookmarks)}')
        else:
            errors += 1
            print(f'  Error batch {i//10}: {response.status_code} - {response.text[:200]}')
        
        time.sleep(0.2)
    
    return created, errors

if __name__ == '__main__':
    # Load all bookmarks
    with open('/tmp/all_bookmarks_full.json') as f:
        data = json.load(f)
        all_tweets = data.get('tweets', [])
    
    # Filter out political ones
    non_political = [t for t in all_tweets if not is_political(t.get('text', ''))]
    
    print(f'Total X bookmarks: {len(all_tweets)}')
    print(f'Political (excluded): {len(all_tweets) - len(non_political)}')
    print(f'Non-political to load: {len(non_political)}')
    
    # Create and populate the new table
    created, errors = create_and_populate_bookmarks_table(BASE_ID, NEW_TABLE_NAME, non_political)
    print(f'\nDone! Added {created} bookmarks to {NEW_TABLE_NAME} ({errors} errors)')
