#!/usr/bin/env python3
"""
Auto-categorize X bookmarks using AI
"""
import json
import os
from pathlib import Path

def categorize_bookmark(tweet_text, author):
    """Simple rule-based categorization (fast, no API needed)"""
    text_lower = (tweet_text + ' ' + author).lower()
    
    # Category rules
    categories = {
        'AI Tools & Coding': ['claude', 'gpt', 'ai agent', 'coding', 'vibe coding', 'llm', 'openai', 'cursor', 'replit', 'code generation', 'programming'],
        'SaaS Launch & Marketing': ['producthunt', 'launch', 'marketing', 'growth', 'affiliate', 'seo', 'landing page', 'conversion', 'sales'],
        'No-Code & Automation': ['n8n', 'make.com', 'zapier', 'automation', 'no-code', 'workflow', 'notion', 'airtable'],
        'Content & Social': ['twitter', 'content', 'social media', 'post', 'thread', 'viral', 'engagement', 'followers'],
        'Monetization': ['mrr', 'revenue', 'pricing', 'monetize', 'income', 'money', 'profit', 'saas revenue'],
        'Development & Tech': ['api', 'github', 'react', 'javascript', 'python', 'database', 'server', 'deploy'],
        'Business Strategy': ['founder', 'startup', 'business', 'strategy', 'pivot', 'decision', 'framework'],
        'Productivity & Tools': ['tool', 'app', 'software', 'productivity', 'efficiency', 'workflow'],
    }
    
    scores = {}
    for cat, keywords in categories.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores, key=scores.get)
    return 'Other'

def process_bookmarks(input_file, output_file):
    with open(input_file) as f:
        bookmarks = json.load(f)
    
    processed = []
    for b in bookmarks:
        category = categorize_bookmark(b.get('text', ''), b.get('author', {}).get('username', ''))
        processed.append({
            'tweet_id': b.get('id'),
            'url': f"https://x.com/{b.get('author', {}).get('username')}/status/{b.get('id')}",
            'content': b.get('text', '')[:500],
            'author': b.get('author', {}).get('username'),
            'author_name': b.get('author', {}).get('name'),
            'likes': b.get('likeCount', 0),
            'retweets': b.get('retweetCount', 0),
            'replies': b.get('replyCount', 0),
            'created_at': b.get('createdAt'),
            'category': category,
            'media': len(b.get('media', [])) > 0
        })
    
    # Sort by likes (highest first)
    processed.sort(key=lambda x: x['likes'], reverse=True)
    
    with open(output_file, 'w') as f:
        json.dump(processed, f, indent=2)
    
    # Summary
    print(f"Processed {len(processed)} bookmarks")
    print("\nCategories:")
    cats = {}
    for p in processed:
        cats[p['category']] = cats.get(p['category'], 0) + 1
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    print(f"\nTop engagement: {processed[0]['likes']} likes")
    print(f"Saved to: {output_file}")

if __name__ == '__main__':
    process_bookmarks('/tmp/all_bookmarks.json', '/tmp/categorized_bookmarks.json')
