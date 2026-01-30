#!/usr/bin/env python3
"""
Sync categorized bookmarks to Airtable
"""
import json
import os
import requests
from pathlib import Path

AIRTABLE_TOKEN = Path('/root/.config/airtable/api_key').read_text().strip()
BASE_ID = 'app5ByPgxLUWzKsS0'
TABLE_NAME = 'Table%201'
HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}',
    'Content-Type': 'application/json'
}

def clear_table():
    """Delete existing records"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    response = requests.get(url, headers=HEADERS, params={'maxRecords': 500})
    data = response.json()
    
    for record in data.get('records', []):
        delete_url = f'{url}/{record["id"]}'
        requests.delete(delete_url, headers=HEADERS)
    
    print(f"Cleared {len(data.get('records', []))} existing records")

def create_records(bookmarks):
    """Create records in batches of 10"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}'
    
    for i in range(0, len(bookmarks), 10):
        batch = bookmarks[i:i+10]
        records = []
        for b in batch:
            fields = {
                'Tweet URL': b['url'],
                'Content': b['content'],
                'Author': f"@{b['author']}",
                'Author Name': b['author_name'],
                'Likes': b['likes'],
                'Retweets': b['retweets'],
                'Replies': b['replies'],
                'Category': b['category'],
                'Has Media': 'Yes' if b['media'] else 'No',
                'Status': 'To Try'
            }
            records.append({'fields': fields})
        
        data = {'records': records}
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code == 200:
            print(f"Created batch {i//10 + 1}/{(len(bookmarks)+9)//10}")
        else:
            print(f"Error: {response.status_code} - {response.text[:200]}")

if __name__ == '__main__':
    with open('/tmp/categorized_bookmarks.json') as f:
        bookmarks = json.load(f)
    
    print(f"Loading {len(bookmarks)} bookmarks to Airtable...")
    create_records(bookmarks)
    print("Done!")
