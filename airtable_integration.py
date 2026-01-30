#!/usr/bin/env python3
"""
Airtable Integration for Ben's Systems
Access content pipeline and bookmark management
"""
import os
import json
import requests
from pathlib import Path

AIRTABLE_TOKEN = os.getenv('AIRTABLE_API_KEY') or Path('/root/.config/airtable/api_key').read_text().strip()
HEADERS = {
    'Authorization': f'Bearer {AIRTABLE_TOKEN}',
    'Content-Type': 'application/json'
}

def list_bases():
    """List all accessible Airtable bases"""
    url = 'https://api.airtable.com/v0/meta/bases'
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_base_schema(base_id):
    """Get tables and fields for a base"""
    url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
    response = requests.get(url, headers=HEADERS)
    return response.json()

def list_records(base_id, table_name, max_records=100):
    """List records from a table"""
    url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
    params = {'maxRecords': max_records}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

def create_record(base_id, table_name, fields):
    """Create a new record"""
    url = f'https://airtable.com/v0/{base_id}/{table_name}'
    data = {'fields': fields}
    response = requests.post(url, headers=HEADERS, json=data)
    return response.json()

if __name__ == '__main__':
    print("Airtable Access Test")
    print("="*50)
    
    bases = list_bases()
    if 'bases' in bases:
        print(f"\nFound {len(bases['bases'])} accessible bases:")
        for base in bases['bases']:
            print(f"  - {base['name']} (ID: {base['id']})")
    else:
        print(f"Error: {bases.get('error', 'Unknown error')}")
