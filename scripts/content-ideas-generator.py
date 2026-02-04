#!/usr/bin/env python3
"""
Content Ideas Generator — Autonomous idea surfacing for Ben
Pulls from trends, competitors, and gaps to generate actionable content ideas
"""
import sqlite3
import json
import requests
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/content-ideas.log")
IDEAS_FILE = Path("/root/clawd/memory/daily_content_ideas.md")

# Ben's content pillars for relevance scoring
BENS_PILLARS = [
    'ai agents', 'automation', 'n8n', 'make.com', 'workflow',
    'claude', 'openai', 'llm', 'building in public', 'indie hacker',
    'solopreneur', 'creator', 'saas', 'no-code', 'low-code',
    'retell', 'content os', 'personal brand', 'ai tools',
    'mcp', 'composio', 'api', 'integration'
]

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def get_trending_topics():
    """Get today's trending topics from our monitors"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    topics = []
    
    # Real trends (HN, Google)
    try:
        cursor.execute('''
            SELECT topic, source, traffic, relevance_score 
            FROM real_trends 
            WHERE created_at > datetime('now', '-12 hours')
            AND relevance_score >= 10
            ORDER BY relevance_score DESC
            LIMIT 10
        ''')
        for row in cursor.fetchall():
            topics.append({
                'topic': row[0],
                'source': row[1],
                'signal': row[2],
                'relevance': row[3],
                'type': 'trending'
            })
    except: pass
    
    conn.close()
    return topics

def get_competitor_activity():
    """Get what competitors posted recently"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    activity = []
    
    try:
        cursor.execute('''
            SELECT creator, platform, content, url
            FROM competitor_content
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY created_at DESC
            LIMIT 15
        ''')
        for row in cursor.fetchall():
            activity.append({
                'creator': row[0],
                'platform': row[1],
                'content': row[2][:150],
                'url': row[3],
                'type': 'competitor'
            })
    except: pass
    
    conn.close()
    return activity

def get_twitter_viral():
    """Get viral tweets in our niche"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    tweets = []
    
    try:
        cursor.execute('''
            SELECT author, text, likes, url
            FROM twitter_trends
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY likes DESC
            LIMIT 10
        ''')
        for row in cursor.fetchall():
            tweets.append({
                'author': row[0],
                'text': row[1][:150],
                'likes': row[2],
                'url': row[3],
                'type': 'viral_tweet'
            })
    except: pass
    
    conn.close()
    return tweets

def generate_content_angles(topic, source_type):
    """Generate content angles for a topic"""
    angles = []
    
    if source_type == 'trending':
        angles = [
            f"Hot take: My thoughts on {topic}",
            f"Thread: What {topic} means for builders",
            f"How I'm using {topic} in my workflow",
        ]
    elif source_type == 'competitor':
        angles = [
            f"My take on what {topic} got right",
            f"Here's what I'd add to {topic}",
            f"Why {topic} matters for solopreneurs",
        ]
    elif source_type == 'viral_tweet':
        angles = [
            f"Adding to this conversation about {topic}",
            f"The part nobody's talking about: {topic}",
            f"Thread: Going deeper on {topic}",
        ]
    
    return angles

def generate_daily_ideas():
    """Generate today's content ideas"""
    ideas = []
    
    # From trends
    trends = get_trending_topics()
    for t in trends[:5]:
        topic = t['topic'][:50]
        ideas.append({
            'source': f"Trending ({t['source']})",
            'topic': topic,
            'angles': generate_content_angles(topic, 'trending'),
            'signal': t.get('signal', ''),
            'relevance': t.get('relevance', 0)
        })
    
    # From competitors
    activity = get_competitor_activity()
    for a in activity[:5]:
        ideas.append({
            'source': f"Competitor ({a['creator']})",
            'topic': a['content'][:60],
            'angles': [
                f"My perspective on what @{a['creator']} posted",
                f"Building on @{a['creator']}'s point",
            ],
            'url': a.get('url', ''),
            'relevance': 50
        })
    
    # From viral tweets
    tweets = get_twitter_viral()
    for tw in tweets[:3]:
        if tw['likes'] and tw['likes'] > 50:
            ideas.append({
                'source': f"Viral (@{tw['author']})",
                'topic': tw['text'][:60],
                'angles': [
                    "Quote tweet with my take",
                    "Thread expanding on this",
                ],
                'url': tw.get('url', ''),
                'relevance': min(tw['likes'], 100)
            })
    
    # Sort by relevance
    ideas.sort(key=lambda x: x.get('relevance', 0), reverse=True)
    
    return ideas[:10]

def format_ideas_report(ideas):
    """Format ideas into a readable report"""
    now = datetime.now()
    
    report = f"""# 💡 Content Ideas — {now.strftime('%A, %B %d')}

Generated: {now.strftime('%I:%M %p')}

---

## Top Opportunities

"""
    
    for i, idea in enumerate(ideas[:7], 1):
        report += f"""### {i}. {idea['topic'][:60]}{'...' if len(idea['topic']) > 60 else ''}

**Source:** {idea['source']}
"""
        if idea.get('signal'):
            report += f"**Signal:** {idea['signal']}\n"
        if idea.get('url'):
            report += f"**Link:** {idea['url']}\n"
        
        report += "\n**Angles:**\n"
        for angle in idea.get('angles', [])[:2]:
            report += f"- {angle}\n"
        report += "\n---\n\n"
    
    report += """
## Quick Wins (Low Effort)

- Reply to a trending thread with your take
- Share one thing you built/learned today
- Quote tweet a competitor with added value

## For Later (Higher Effort)

- Deep dive on the top trending topic
- Video breakdown of a workflow
- Build log from Retell progress

---

*Pick 1-2 and execute. Don't overthink.*
"""
    
    return report

def main():
    log("Content Ideas Generator starting...")
    
    ideas = generate_daily_ideas()
    log(f"Generated {len(ideas)} ideas")
    
    report = format_ideas_report(ideas)
    
    # Save report
    IDEAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    IDEAS_FILE.write_text(report)
    log(f"Report saved to {IDEAS_FILE}")
    
    print(report)
    
    log("Done")

if __name__ == "__main__":
    main()
