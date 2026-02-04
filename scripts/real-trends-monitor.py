#!/usr/bin/env python3
"""
Real Trends Monitor - Pull ACTUAL trending topics, then filter for relevance
Sources: Google Daily Trends, Twitter Trending, HN Front Page, Reddit Rising
"""
import sqlite3
import requests
import feedparser
import json
import re
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/real-trends.log")

# Our niche keywords for relevance scoring
NICHE_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'ml', 'llm', 'gpt',
    'chatgpt', 'claude', 'gemini', 'openai', 'anthropic', 'deepseek', 'mistral',
    'automation', 'workflow', 'no-code', 'nocode', 'low-code', 'api',
    'saas', 'startup', 'founder', 'indie', 'solopreneur', 'creator',
    'coding', 'programming', 'developer', 'software', 'tech', 'app',
    'agent', 'bot', 'copilot', 'cursor', 'vibe', 'mcp',
    'video', 'image', 'generation', 'midjourney', 'sora', 'flux',
    'twitter', 'x.com', 'social media', 'viral', 'content'
]

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def ensure_tables():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS real_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            source TEXT,
            traffic TEXT,
            relevance_score INTEGER,
            url TEXT,
            related_content TEXT,
            created_at TEXT,
            UNIQUE(topic, source, created_at)
        )
    ''')
    conn.commit()
    conn.close()

def score_relevance(text):
    """Score how relevant a topic is to our niche (0-100)"""
    text_lower = text.lower()
    score = 0
    matches = []
    for kw in NICHE_KEYWORDS:
        if kw in text_lower:
            score += 10
            matches.append(kw)
    return min(score, 100), matches

def fetch_google_daily_trends():
    """Fetch actual Google Daily Trends (not keyword searches)"""
    results = []
    try:
        # Google Trends RSS for daily trends
        url = "https://trends.google.com/trending/rss?geo=US"
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:20]:
            title = entry.get('title', '')
            traffic = entry.get('ht_approx_traffic', 'Unknown')
            link = entry.get('link', '')
            
            relevance, matches = score_relevance(title)
            
            results.append({
                'topic': title,
                'source': 'google_daily',
                'traffic': traffic,
                'relevance': relevance,
                'url': link,
                'matches': matches
            })
        log(f"Google Daily: {len(results)} trends")
    except Exception as e:
        log(f"Google Daily error: {e}")
    
    return results

def fetch_hn_front_page():
    """Fetch Hacker News front page stories"""
    results = []
    try:
        # HN top stories
        resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = resp.json()[:30]
        
        for sid in story_ids:
            try:
                story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
                title = story.get('title', '')
                url = story.get('url', f"https://news.ycombinator.com/item?id={sid}")
                score = story.get('score', 0)
                
                relevance, matches = score_relevance(title)
                
                results.append({
                    'topic': title,
                    'source': 'hackernews',
                    'traffic': f"{score} points",
                    'relevance': relevance,
                    'url': url,
                    'matches': matches
                })
            except:
                pass
        log(f"HN: {len(results)} stories")
    except Exception as e:
        log(f"HN error: {e}")
    
    return results

def fetch_reddit_rising():
    """Fetch Reddit rising posts from relevant subreddits"""
    results = []
    subreddits = ['technology', 'programming', 'artificial', 'MachineLearning', 'SideProject', 'startups']
    
    headers = {'User-Agent': 'CortanaBot/1.0'}
    
    for sub in subreddits:
        try:
            resp = requests.get(
                f"https://www.reddit.com/r/{sub}/rising.json?limit=10",
                headers=headers, timeout=10
            )
            data = resp.json()
            
            for post in data.get('data', {}).get('children', []):
                p = post.get('data', {})
                title = p.get('title', '')
                url = f"https://reddit.com{p.get('permalink', '')}"
                score = p.get('score', 0)
                
                relevance, matches = score_relevance(title)
                
                results.append({
                    'topic': title,
                    'source': f'reddit_{sub}',
                    'traffic': f"{score} upvotes",
                    'relevance': relevance,
                    'url': url,
                    'matches': matches
                })
        except Exception as e:
            log(f"Reddit {sub} error: {e}")
    
    log(f"Reddit: {len(results)} posts")
    return results

def fetch_twitter_trending():
    """Fetch actual trending from Twitter via bird CLI"""
    results = []
    try:
        import subprocess
        import os
        
        # Get auth from env
        auth_token = os.environ.get('AUTH_TOKEN', '')
        ct0 = os.environ.get('CT0', '')
        
        if not auth_token:
            # Try to read from bashrc
            bashrc = Path("/root/.bashrc").read_text()
            for line in bashrc.split('\n'):
                if 'AUTH_TOKEN=' in line and 'export' in line:
                    auth_token = line.split('=', 1)[1].strip().strip('"\'')
                if 'CT0=' in line and 'export' in line:
                    ct0 = line.split('=', 1)[1].strip().strip('"\'')
        
        # Search for viral AI content
        searches = ['AI viral', 'chatgpt announcement', 'llm breakthrough', 'AI agents']
        
        for query in searches[:2]:
            try:
                cmd = ['bird', 'search', query, '-n', '5', '--json']
                if auth_token:
                    cmd.extend(['--auth-token', auth_token])
                if ct0:
                    cmd.extend(['--ct0', ct0])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            tweet = json.loads(line)
                            text = tweet.get('text', '')[:100]
                            author = tweet.get('user', {}).get('screen_name', 'unknown')
                            likes = tweet.get('favorite_count', 0)
                            tweet_id = tweet.get('id_str', '')
                            
                            relevance, matches = score_relevance(text)
                            
                            results.append({
                                'topic': f"@{author}: {text}",
                                'source': 'twitter',
                                'traffic': f"{likes} likes",
                                'relevance': relevance,
                                'url': f"https://twitter.com/{author}/status/{tweet_id}" if tweet_id else '',
                                'matches': matches
                            })
                        except:
                            pass
            except:
                pass
        
        log(f"Twitter: {len(results)} tweets")
    except Exception as e:
        log(f"Twitter error: {e}")
    
    return results

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0
    now = datetime.now().strftime("%Y-%m-%d %H:00")  # Round to hour
    
    for r in results:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO real_trends 
                (topic, source, traffic, relevance_score, url, related_content, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                r['topic'], r['source'], r['traffic'], r['relevance'],
                r['url'], json.dumps(r.get('matches', [])), now
            ))
            if cursor.rowcount > 0:
                saved += 1
        except Exception as e:
            log(f"Save error: {e}")
    
    conn.commit()
    conn.close()
    return saved

def generate_report():
    """Generate a trending report sorted by relevance"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    
    # Get trends from last 6 hours, sorted by relevance
    cursor.execute('''
        SELECT topic, source, traffic, relevance_score, url 
        FROM real_trends
        WHERE created_at > datetime('now', '-6 hours')
        ORDER BY relevance_score DESC, created_at DESC
        LIMIT 30
    ''')
    trends = cursor.fetchall()
    conn.close()
    
    report = ["🔥 REAL TRENDS (sorted by niche relevance)\n"]
    report.append(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    # High relevance (our niche)
    report.append("\n📍 HIGH RELEVANCE (AI/Tech/Creator):")
    high = [t for t in trends if t[3] >= 20]
    for topic, source, traffic, rel, url in high[:10]:
        report.append(f"  [{rel}] {topic[:60]}...")
        report.append(f"      {source} | {traffic}")
    
    # General trending (might be opportunities)
    report.append("\n🌍 GENERAL TRENDING:")
    general = [t for t in trends if t[3] < 20][:10]
    for topic, source, traffic, rel, url in general:
        report.append(f"  {topic[:60]}...")
        report.append(f"      {source} | {traffic}")
    
    return "\n".join(report)

def main():
    log("Real Trends Monitor starting...")
    ensure_tables()
    
    all_results = []
    
    # Fetch from all sources
    all_results.extend(fetch_google_daily_trends())
    all_results.extend(fetch_hn_front_page())
    all_results.extend(fetch_reddit_rising())
    all_results.extend(fetch_twitter_trending())
    
    log(f"Total: {len(all_results)} items")
    
    saved = save_results(all_results)
    log(f"Saved: {saved} new items")
    
    report = generate_report()
    print(report)
    
    # Save report
    Path("/root/clawd/memory/real_trends_report.txt").write_text(report)
    
    log("Done")

if __name__ == "__main__":
    main()
