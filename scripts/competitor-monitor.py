#!/usr/bin/env python3
"""
Competitor Monitor - Track what creators in our niche are posting about
Twitter accounts + YouTube channels we watch
"""
import sqlite3
import subprocess
import json
import feedparser
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/competitor-monitor.log")

# Twitter accounts to monitor (AI/automation/creator space)
TWITTER_COMPETITORS = [
    "therundownai",      # AI newsletter
    "mattshumer_",       # AI builder
    "mcaborern",         # AI content
    "LiamOttley",        # AI agency
    "dannypostmaa",      # Indie hacker
    "levelsio",          # Indie legend
    "marc_louvion",      # Indie hacker
    "thisguyknowsai",    # AI content
    "nonmayorpete",      # AI/automation
    "venturetwins",      # AI tools
]

# YouTube channels (already have RSS feeds)
YOUTUBE_COMPETITORS = [
    ("Fireship", "UCsBjURrPoezykLs9EqgamOA"),
    ("Matt Wolfe", "UCJIfeSCssxSC_Dhc5s7woww"),
    ("AI Explained", "UCNJ1Ymd5yFuUPtn21xtRbbw"),
    ("The AI Advantage", "UCLZGCe59kwxd9DlmEMVCPuw"),
    ("Liam Ottley", "UCWRBqP4RG1m_G96Hrg0DT-w"),
    ("Greg Isenberg", "UCGwuxdEeCf0TIA2RbPOj-8g"),
    ("My First Million", "UC5vNPzGPPQTIO7YCgjzU9PQ"),
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
        CREATE TABLE IF NOT EXISTS competitor_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator TEXT,
            platform TEXT,
            content TEXT,
            url TEXT,
            engagement TEXT,
            created_at TEXT,
            UNIQUE(creator, url)
        )
    ''')
    conn.commit()
    conn.close()

def get_twitter_auth():
    """Get Twitter auth tokens"""
    auth_token = ''
    ct0 = ''
    try:
        bashrc = Path("/root/.bashrc").read_text()
        for line in bashrc.split('\n'):
            if 'AUTH_TOKEN=' in line and 'export' in line:
                auth_token = line.split('=', 1)[1].strip().strip('"\'')
            if 'CT0=' in line and 'export' in line:
                ct0 = line.split('=', 1)[1].strip().strip('"\'')
    except:
        pass
    return auth_token, ct0

def fetch_twitter_competitors():
    """Fetch recent tweets from competitor accounts using user-tweets command"""
    results = []
    auth_token, ct0 = get_twitter_auth()

    import time

    for username in TWITTER_COMPETITORS:
        try:
            # Use user-tweets command instead of search
            cmd = ['bird', 'user-tweets', username, '-n', '3', '--json']
            if auth_token:
                cmd.extend(['--auth-token', auth_token])
            if ct0:
                cmd.extend(['--ct0', ct0])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # Check for rate limit
            if '429' in result.stderr or 'Rate limit' in result.stderr:
                log(f"  Rate limited, stopping Twitter fetch")
                break

            count = 0
            for line in result.stdout.strip().split('\n'):
                if line.strip() and line.startswith('{'):
                    try:
                        tweet = json.loads(line)
                        text = tweet.get('text', tweet.get('full_text', ''))
                        likes = tweet.get('favorite_count', tweet.get('likes', 0))
                        rts = tweet.get('retweet_count', tweet.get('retweets', 0))
                        tweet_id = tweet.get('id_str', tweet.get('id', ''))

                        results.append({
                            'creator': username,
                            'platform': 'twitter',
                            'content': text[:280],
                            'url': f"https://twitter.com/{username}/status/{tweet_id}",
                            'engagement': f"{likes} likes, {rts} RTs"
                        })
                        count += 1
                    except:
                        pass

            log(f"  @{username}: {count} tweets")
            time.sleep(2)  # Rate limit protection
        except Exception as e:
            log(f"  @{username} error: {e}")

    return results

def fetch_youtube_competitors():
    """Fetch recent videos from competitor channels"""
    results = []
    
    for name, channel_id in YOUTUBE_COMPETITORS:
        try:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:2]:
                results.append({
                    'creator': name,
                    'platform': 'youtube',
                    'content': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'engagement': entry.get('published', '')[:10]
                })
            
            log(f"  {name}: {min(2, len(feed.entries))} videos")
        except Exception as e:
            log(f"  {name} error: {e}")
    
    return results

def save_results(results):
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved = 0
    
    for r in results:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO competitor_content
                (creator, platform, content, url, engagement, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                r['creator'], r['platform'], r['content'],
                r['url'], r['engagement'], datetime.now().isoformat()
            ))
            if cursor.rowcount > 0:
                saved += 1
        except:
            pass
    
    conn.commit()
    conn.close()
    return saved

def generate_report():
    """Generate competitor activity report"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT creator, platform, content, engagement, url
        FROM competitor_content
        WHERE created_at > datetime('now', '-24 hours')
        ORDER BY created_at DESC
    ''')
    content = cursor.fetchall()
    conn.close()
    
    report = ["👀 COMPETITOR WATCH\n"]
    report.append(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    # Group by platform
    twitter = [c for c in content if c[1] == 'twitter']
    youtube = [c for c in content if c[1] == 'youtube']
    
    if twitter:
        report.append("\n🐦 TWITTER:")
        for creator, _, text, engagement, url in twitter[:10]:
            text_short = text[:80].replace('\n', ' ') + "..."
            report.append(f"  @{creator}: {text_short}")
            report.append(f"    {engagement}")
    
    if youtube:
        report.append("\n📺 YOUTUBE:")
        for creator, _, title, date, url in youtube[:10]:
            report.append(f"  {creator}: {title[:60]}")
            report.append(f"    Published: {date}")
    
    return "\n".join(report)

def main():
    log("Competitor Monitor starting...")
    ensure_tables()
    
    all_results = []
    
    log("Fetching Twitter competitors...")
    all_results.extend(fetch_twitter_competitors())
    
    log("Fetching YouTube competitors...")
    all_results.extend(fetch_youtube_competitors())
    
    log(f"Total: {len(all_results)} items")
    
    saved = save_results(all_results)
    log(f"Saved: {saved} new items")
    
    report = generate_report()
    print(report)
    
    Path("/root/clawd/memory/competitor_report.txt").write_text(report)
    
    log("Done")

if __name__ == "__main__":
    main()
