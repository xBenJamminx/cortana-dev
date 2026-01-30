#!/usr/bin/env python3
"""
Reload all 1,309 non-political bookmarks to the NEW Airtable base's 'Table 1'
Adjusted to fit existing 'Table 1' schema.
Logs to /tmp/repopulate_log.txt
"""
import json
import os
import requests
from pathlib import Path
import time
import sys

LOG_FILE = '/tmp/repopulate_log.txt'

def log_message(message):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(message) # Also print to stdout for real-time monitoring

AIRTABLE_TOKEN = os.getenv('AIRTABLE_API_KEY') or Path('/root/.config/airtable/api_key').read_text().strip()
NEW_BASE_ID = 'appFPKQxzO0SClFdR' # Confirmed new Base ID
NEW_TABLE_NAME = 'Table 1' # Confirmed table name
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

def clear_all_records(base_id, table_name):
    """Delete ALL existing records from the specified table"""
    url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
    all_record_ids = []
    offset = None
    
    log_message(f'Attempting to fetch existing records from {table_name} for deletion...')
    # Get all record IDs
    while True:
        params = {'fields': [], 'maxRecords': 100}
        if offset:
            params['offset'] = offset
        
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        
        if 'records' not in data:
            log_message(f'Error fetching records for deletion: {data}')
            break
            
        all_record_ids.extend([r['id'] for r in data.get('records', [])])
        
        offset = data.get('offset')
        if not offset:
            break
    
    log_message(f'Found {len(all_record_ids)} existing records to delete from {table_name}.')
    
    # Delete in batches of 10 for rate limiting
    for i in range(0, len(all_record_ids), 10):
        batch = all_record_ids[i:i+10]
        delete_url = f'{url}?records[]={'&records[]='.join(batch)}'
        response = requests.delete(delete_url, headers=HEADERS)
        if response.status_code != 200:
            log_message(f'  Error deleting batch {i//10}: {response.text[:100]}')
        else:
            if i % 100 == 0:
                log_message(f'  Deleted {i}/{len(all_record_ids)}')
        time.sleep(0.2) # Rate limiting
    
    log_message(f'Cleared {len(all_record_ids)} records from {table_name}')

def add_bookmarks(base_id, table_name, bookmarks):
    url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
    created = 0
    errors = 0
    
    log_message(f'Starting to add {len(bookmarks)} bookmarks to {table_name}...')
    for i in range(0, len(bookmarks), 10):
        batch = bookmarks[i:i+10]
        records = []
        for b in batch:
            # Map to existing Table 1 fields: Name, Notes, Status
            # We will put most data into Notes for now
            fields = {
                'Name': b.get('text', '')[:50] + '...' if len(b.get('text', '')) > 50 else b.get('text', ''),
                'Notes': f"Author: @{b.get('author', {}).get('username', '')}\nAuthor Name: {b.get('author', {}).get('name', '')}\nLikes: {b.get('likeCount', 0)}\nRetweets: {b.get('retweetCount', 0)}\nReplies: {b.get('replyCount', 0)}\nCategory: {categorize_bookmark(b.get('text', ''), b.get('author', {}).get('username', ''))}\nURL: {f'https://x.com/{b.get('author', {}).get('username')}/status/{b['id']}'}\nHas Media: {f'Yes' if b.get('media') else 'No'}\nCreated At: {b.get('createdAt', '')}\n\n{b.get('text', '')}",
                'Status': 'Todo' # Using one of the allowed options
            }
            records.append({'fields': fields})
        
        data = {'records': records}
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code == 200:
            created += len(batch)
            if created % 100 == 0:
                log_message(f'  Added {created}/{len(bookmarks)}')
        else:
            errors += 1
            log_message(f'  Error batch {i//10}: {response.status_code} - {response.text[:200]}')
        
        # Rate limiting
        time.sleep(0.2)
    
    return created, errors

if __name__ == '__main__':
    log_message('--- Starting bookmark repopulation script ---')
    # Load all bookmarks
    with open('/tmp/all_bookmarks_full.json') as f:
        data = json.load(f)
        all_tweets = data.get('tweets', [])
    
    # Filter out political ones
    non_political = [t for t in all_tweets if not is_political(t.get('text', ''))]
    
    log_message(f'Total X bookmarks: {len(all_tweets)}')
    log_message(f'Political (excluded): {len(all_tweets) - len(non_political)}')
    log_message(f'Non-political to load: {len(non_political)}')
    
    # Clear existing records from the NEW table
    clear_all_records(NEW_BASE_ID, NEW_TABLE_NAME)
    
    # Add all non-political bookmarks to the NEW table
    log_message(f'\nLoading {len(non_political)} bookmarks to {NEW_TABLE_NAME} in {NEW_BASE_ID}...')
    created, errors = add_bookmarks(NEW_BASE_ID, NEW_TABLE_NAME, non_political)
    log_message(f'\nDone! Added {created} bookmarks ({errors} errors)')
