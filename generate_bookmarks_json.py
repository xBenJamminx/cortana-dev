#!/usr/bin/env python3
"""
Generate a JSON file with all non-political bookmarks for manual Airtable import.
"""
import json
import os
from pathlib import Path

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

if __name__ == '__main__':
    # Load all bookmarks
    with open('/tmp/all_bookmarks_full.json') as f:
        data = json.load(f)
        all_tweets = data.get('tweets', [])
    
    # Filter out political ones
    non_political_tweets = [t for t in all_tweets if not is_political(t.get('text', ''))]
    
    # Prepare records for Airtable import format
    records_for_import = []
    for b in non_political_tweets:
        records_for_import.append({
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
        })

    output_file_path = '/tmp/non_political_bookmarks_for_import.json'
    with open(output_file_path, 'w') as f:
        json.dump(records_for_import, f, indent=2)
        
    print(f'Generated {len(records_for_import)} non-political bookmarks for manual import.')
    print(f'File saved to: {output_file_path}')
