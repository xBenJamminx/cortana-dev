#!/usr/bin/env python3
"""
Cortana Morning Briefing v2 - Full data integration
Pulls from: Calendar, Twitter (Composio), Airtable, Notion, Trending News
"""
import os
import json
import sqlite3
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Config
BOT_TOKEN = "REDACTED_TELEGRAM_BOT_TOKEN"
CHAT_ID = "1455611839"
MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
GOOGLE_CREDS_FILE = "/root/.openclaw/google_credentials.json"
USER_MD = Path("/root/clawd/USER.md")
COMPOSIO_SCRIPT = "/root/clawd/skills/composio/composio-mcp.py"
LOG_FILE = Path("/root/clawd/logs/briefing.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def send_telegram(message, parse_mode="Markdown"):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }, timeout=30)
        return r.json().get("ok", False)
    except Exception as e:
        log(f"Telegram error: {e}")
        return False

def composio_exec(tool, params=None):
    """Execute a Composio tool"""
    try:
        cmd = [COMPOSIO_SCRIPT, "--exec", tool]
        if params:
            cmd.append(json.dumps(params))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Try to parse JSON from output
            for line in result.stdout.strip().split("\n"):
                try:
                    return json.loads(line)
                except:
                    pass
        return None
    except Exception as e:
        log(f"Composio error ({tool}): {e}")
        return None

# ============= DATA GATHERING =============

def get_weather():
    try:
        r = requests.get("https://wttr.in/Carle+Place+NY?format=j1", timeout=10)
        c = r.json().get("current_condition", [{}])[0]
        return f"{c.get('temp_F', '?')}°F, {c.get('weatherDesc', [{}])[0].get('value', 'Unknown')}"
    except:
        return "Weather unavailable"

def get_calendar_events():
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        with open(GOOGLE_CREDS_FILE) as f:
            d = json.load(f)
        creds = Credentials(token=d.get("token"), refresh_token=d.get("refresh_token"),
                           token_uri=d.get("token_uri"), client_id=d.get("client_id"),
                           client_secret=d.get("client_secret"), scopes=d.get("scopes"))
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            d["token"] = creds.token
            with open(GOOGLE_CREDS_FILE, "w") as f:
                json.dump(d, f, indent=2)

        service = build("calendar", "v3", credentials=creds)
        now = datetime.utcnow()
        start = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
        end = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

        result = service.events().list(calendarId="primary", timeMin=start, timeMax=end,
                                       maxResults=10, singleEvents=True, orderBy="startTime").execute()

        events = []
        for e in result.get("items", []):
            start_time = e.get("start", {}).get("dateTime", e.get("start", {}).get("date", ""))
            time_str = "All day"
            if "T" in start_time:
                try:
                    t = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    time_str = t.strftime("%I:%M %p")
                except:
                    pass
            events.append({"time": time_str, "title": e.get('summary', 'No title')})
        return events
    except Exception as e:
        log(f"Calendar error: {e}")
        return []

def get_twitter_stats():
    """Get Twitter profile stats via Composio"""
    try:
        result = composio_exec("TWITTER_USER_LOOKUP_ME")
        if result and "data" in result:
            data = result["data"]
            return {
                "followers": data.get("public_metrics", {}).get("followers_count", 0),
                "following": data.get("public_metrics", {}).get("following_count", 0),
                "tweets": data.get("public_metrics", {}).get("tweet_count", 0),
            }
        return None
    except Exception as e:
        log(f"Twitter stats error: {e}")
        return None

def get_recent_tweets_engagement():
    """Get engagement on recent tweets"""
    try:
        # Search for my recent tweets
        result = composio_exec("TWITTER_RECENT_SEARCH", {
            "query": "from:xBenJamminx",
            "max_results": 10
        })
        if result and "data" in result:
            tweets = result["data"]
            total_likes = sum(t.get("public_metrics", {}).get("like_count", 0) for t in tweets)
            total_retweets = sum(t.get("public_metrics", {}).get("retweet_count", 0) for t in tweets)
            top_tweet = max(tweets, key=lambda t: t.get("public_metrics", {}).get("like_count", 0)) if tweets else None
            top_tweet_url = None
            if top_tweet:
                tweet_id = top_tweet.get("id")
                if tweet_id:
                    top_tweet_url = f"https://twitter.com/xBenJamminx/status/{tweet_id}"
            return {
                "total_likes": total_likes,
                "total_retweets": total_retweets,
                "top_tweet": top_tweet.get("text", "") if top_tweet else None,
                "top_tweet_url": top_tweet_url
            }
        return None
    except Exception as e:
        log(f"Twitter engagement error: {e}")
        return None

def get_airtable_content_queue():
    """Get pending content from Airtable"""
    try:
        # First list bases to find content OS
        bases = composio_exec("AIRTABLE_LIST_BASES")
        if bases and "bases" in bases:
            for base in bases["bases"]:
                if "content" in base.get("name", "").lower():
                    # Get records from this base
                    records = composio_exec("AIRTABLE_LIST_RECORDS", {
                        "baseId": base["id"],
                        "tableIdOrName": "Content"  # Adjust table name as needed
                    })
                    if records and "records" in records:
                        pending = [r for r in records["records"]
                                  if r.get("fields", {}).get("Status") in ["Draft", "Ready", "Scheduled"]]
                        return pending[:5]
        return None
    except Exception as e:
        log(f"Airtable error: {e}")
        return None

def get_notion_tasks():
    """Get pending tasks from Notion"""
    try:
        # Search for task-related pages
        result = composio_exec("NOTION_SEARCH_NOTION_PAGE", {
            "query": "tasks"
        })
        if result and "results" in result:
            return result["results"][:5]
        return None
    except Exception as e:
        log(f"Notion error: {e}")
        return None

def get_trending_news():
    """Get trending news from our monitor with URLs"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, source, url FROM trending_news
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY created_at DESC LIMIT 5
        ''')
        news = cursor.fetchall()
        conn.close()
        return news
    except:
        return []

def get_indiehacker_posts():
    """Get top indie hacker posts from our monitor"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, source, score, url FROM indiehacker_posts
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY score DESC LIMIT 5
        ''')
        posts = cursor.fetchall()
        conn.close()
        return posts
    except:
        return []

def get_producthunt_launches():
    """Get top Product Hunt launches"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, tagline, url, votes FROM producthunt_posts
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY votes DESC LIMIT 5
        ''')
        posts = cursor.fetchall()
        conn.close()
        return posts
    except:
        return []

def get_google_trends():
    """Get Google Trends data"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT term, category, traffic, url FROM google_trends
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY created_at DESC LIMIT 5
        ''')
        trends = cursor.fetchall()
        conn.close()
        return trends
    except:
        return []

def get_twitter_trending():
    """Get trending tweets from our searches"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT author, text, likes, url FROM twitter_trends
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY likes DESC LIMIT 5
        ''')
        tweets = cursor.fetchall()
        conn.close()
        return tweets
    except:
        return []

def get_youtube_videos():
    """Get latest YouTube videos from tracked channels"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, channel, url FROM youtube_videos
            WHERE created_at > datetime('now', '-48 hours')
            ORDER BY created_at DESC LIMIT 5
        ''')
        videos = cursor.fetchall()
        conn.close()
        return videos
    except:
        return []

def get_devto_posts():
    """Get trending Dev.to/Hashnode posts"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, author, url, reactions, source FROM devto_posts
            WHERE created_at > datetime('now', '-48 hours')
            ORDER BY reactions DESC LIMIT 5
        ''')
        posts = cursor.fetchall()
        conn.close()
        return posts
    except:
        return []

def get_substack_posts():
    """Get latest newsletter posts"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, newsletter, url FROM substack_posts
            WHERE created_at > datetime('now', '-48 hours')
            ORDER BY created_at DESC LIMIT 5
        ''')
        posts = cursor.fetchall()
        conn.close()
        return posts
    except:
        return []

def get_exploding_topics():
    """Get exploding topics"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT topic, category, growth, url FROM exploding_topics
            WHERE created_at > datetime('now', '-48 hours')
            ORDER BY created_at DESC LIMIT 5
        ''')
        topics = cursor.fetchall()
        conn.close()
        return topics
    except:
        return []

def get_system_status():
    try:
        r = requests.get("http://localhost:8787/health", timeout=5)
        return r.json().get("status", "unknown")
    except:
        return "unknown"

# ============= TOPIC ANALYTICS =============

def get_trending_topics_with_context():
    """Get trending topics with related content from all sources"""
    import re
    from collections import Counter

    def normalize(t):
        return re.sub(r'[^a-z0-9]', '', t.lower())

    all_topics = {}

    # Hot keywords to detect
    hot_keywords = [
        'chatgpt', 'claude', 'gemini', 'deepseek', 'openai', 'anthropic',
        'gpt-4', 'gpt4', 'gpt-5', 'llm', 'ai agent', 'ai agents',
        'automation', 'no-code', 'nocode', 'cursor', 'copilot',
        'midjourney', 'sora', 'dalle', 'flux', 'n8n', 'make.com',
        'saas', 'indie hacker', 'solopreneur', 'creator economy',
        'viral', 'launch', 'shipped', 'vibe coding', 'mcp'
    ]

    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    # Google Trends (high signal)
    try:
        cursor.execute("SELECT term, traffic, url FROM google_trends WHERE created_at > datetime('now', '-24 hours')")
        for term, traffic, url in cursor.fetchall():
            key = normalize(term)
            if key and len(key) > 2:
                if key not in all_topics:
                    all_topics[key] = {"name": term, "sources": [], "score": 0, "content": []}
                all_topics[key]["sources"].append("trends")
                all_topics[key]["score"] += 100
    except: pass

    # Twitter - extract topics and keep tweets as content
    try:
        cursor.execute("SELECT author, text, url, likes FROM twitter_trends WHERE created_at > datetime('now', '-24 hours')")
        for author, text, url, likes in cursor.fetchall():
            text_lower = text.lower()
            # Find keywords
            for kw in hot_keywords:
                if kw in text_lower:
                    key = normalize(kw)
                    if key not in all_topics:
                        all_topics[key] = {"name": kw, "sources": [], "score": 0, "content": []}
                    if "twitter" not in all_topics[key]["sources"]:
                        all_topics[key]["sources"].append("twitter")
                    all_topics[key]["score"] += max(likes or 0, 20)
                    all_topics[key]["content"].append({
                        "type": "tweet", "author": author, "text": text[:100], "url": url
                    })
            # Hashtags
            for tag in re.findall(r'#(\w+)', text):
                key = normalize(tag)
                if key and len(key) > 2:
                    if key not in all_topics:
                        all_topics[key] = {"name": tag, "sources": [], "score": 0, "content": []}
                    if "twitter" not in all_topics[key]["sources"]:
                        all_topics[key]["sources"].append("twitter")
                    all_topics[key]["score"] += max(likes or 0, 10)
                    all_topics[key]["content"].append({
                        "type": "tweet", "author": author, "text": text[:100], "url": url
                    })
    except: pass

    # YouTube - extract topics from titles
    try:
        cursor.execute("SELECT title, channel, url FROM youtube_videos WHERE created_at > datetime('now', '-48 hours')")
        for title, channel, url in cursor.fetchall():
            title_lower = title.lower()
            for kw in hot_keywords:
                if kw in title_lower:
                    key = normalize(kw)
                    if key not in all_topics:
                        all_topics[key] = {"name": kw, "sources": [], "score": 0, "content": []}
                    if "youtube" not in all_topics[key]["sources"]:
                        all_topics[key]["sources"].append("youtube")
                    all_topics[key]["score"] += 30
                    all_topics[key]["content"].append({
                        "type": "video", "title": title, "channel": channel, "url": url
                    })
    except: pass

    # Dev.to / Hashnode
    try:
        cursor.execute("SELECT title, author, url, reactions, source FROM devto_posts WHERE created_at > datetime('now', '-48 hours')")
        for title, author, url, reactions, source in cursor.fetchall():
            title_lower = title.lower()
            for kw in hot_keywords:
                if kw in title_lower:
                    key = normalize(kw)
                    if key not in all_topics:
                        all_topics[key] = {"name": kw, "sources": [], "score": 0, "content": []}
                    if "dev" not in all_topics[key]["sources"]:
                        all_topics[key]["sources"].append("dev")
                    all_topics[key]["score"] += min(reactions or 0, 20)
                    all_topics[key]["content"].append({
                        "type": "article", "title": title, "source": source, "url": url
                    })
    except: pass

    # Product Hunt
    try:
        cursor.execute("SELECT title, tagline, url, votes FROM producthunt_posts WHERE created_at > datetime('now', '-24 hours')")
        for title, tagline, url, votes in cursor.fetchall():
            combined = (title + " " + (tagline or "")).lower()
            for kw in hot_keywords:
                if kw in combined:
                    key = normalize(kw)
                    if key not in all_topics:
                        all_topics[key] = {"name": kw, "sources": [], "score": 0, "content": []}
                    if "ph" not in all_topics[key]["sources"]:
                        all_topics[key]["sources"].append("ph")
                    all_topics[key]["score"] += min(votes or 0, 30)
                    all_topics[key]["content"].append({
                        "type": "product", "title": title, "tagline": tagline, "url": url
                    })
    except: pass

    conn.close()

    # Sort by score and return top topics
    ranked = sorted(all_topics.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:8]

# ============= BRIEFING BUILDER =============

def build_briefing():
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    day_name = now.strftime("%A")

    sections = []

    # Header with weather
    weather = get_weather()
    openers = {
        "Monday": "New week. Let's build.",
        "Tuesday": "Momentum day.",
        "Wednesday": "Midweek checkpoint.",
        "Thursday": "Push through.",
        "Friday": "Finish strong.",
        "Saturday": "Weekend grind or rest?",
        "Sunday": "Reset and plan."
    }
    sections.append(f"""🌅 *{date_str}*
{weather} in Carle Place

_{openers.get(day_name, "Let's go.")}_""")

    # Calendar
    events = get_calendar_events()
    if events:
        cal_lines = ["📅 *Schedule*"]
        for e in events[:5]:
            cal_lines.append(f"• {e['time']}: {e['title']}")
        sections.append("\n".join(cal_lines))
    else:
        sections.append("📅 *Schedule*\nNo meetings. Deep work day.")

    # Twitter Performance (your stats)
    twitter_stats = get_twitter_stats()
    engagement = get_recent_tweets_engagement()
    if twitter_stats or engagement:
        twitter_lines = ["📊 *Your Twitter*"]
        if twitter_stats:
            twitter_lines.append(f"Followers: {twitter_stats.get('followers', '?'):,}")
        if engagement:
            twitter_lines.append(f"Recent: {engagement.get('total_likes', 0)} likes, {engagement.get('total_retweets', 0)} RTs")
        sections.append("\n".join(twitter_lines))

    # HOT TOPICS - The main event
    topics = get_trending_topics_with_context()
    if topics:
        topics_lines = ["🔥 *HOT TOPICS* (content opportunities)"]
        for topic in topics[:5]:
            name = topic["name"].upper()
            sources = ", ".join(topic["sources"])
            topics_lines.append(f"\n*{name}* _{sources}_")

            # Show up to 2 pieces of content per topic
            for item in topic["content"][:2]:
                if item["type"] == "tweet":
                    text = item["text"][:50].replace("\n", " ") + "..."
                    topics_lines.append(f"  🐦 @{item['author']}: {text}")
                elif item["type"] == "video":
                    topics_lines.append(f"  📺 {item['title'][:40]}... ({item['channel']})")
                elif item["type"] == "article":
                    topics_lines.append(f"  📝 {item['title'][:45]}...")
                elif item["type"] == "product":
                    topics_lines.append(f"  🚀 {item['title']}: {(item['tagline'] or '')[:30]}...")

        sections.append("\n".join(topics_lines))

    # Fresh launches (PH + Indie)
    ph_launches = get_producthunt_launches()
    ih_posts = get_indiehacker_posts()
    if ph_launches or ih_posts:
        launch_lines = ["🚀 *Fresh Launches*"]
        for item in (ph_launches or [])[:3]:
            title, tagline, url, votes = item
            launch_lines.append(f"• [{title}]({url}) ({votes}⬆)")
        for item in (ih_posts or [])[:2]:
            title, source, score, url = item
            launch_lines.append(f"• [{title}]({url})")
        sections.append("\n".join(launch_lines))

    # Quick hits - YouTube + Newsletters (brief)
    yt = get_youtube_videos()
    nl = get_substack_posts()
    if yt or nl:
        quick_lines = ["📬 *Quick Reads/Watches*"]
        for item in (yt or [])[:2]:
            title, channel, url = item
            quick_lines.append(f"• [{title[:35]}...]({url})")
        for item in (nl or [])[:2]:
            title, newsletter, url = item
            quick_lines.append(f"• [{title[:35]}...]({url})")
        sections.append("\n".join(quick_lines))

    # Content Pipeline (Airtable)
    content = get_airtable_content_queue()
    if content:
        content_lines = ["📝 *Content Queue*"]
        for item in content[:3]:
            title = item.get("fields", {}).get("Title", "Untitled")
            status = item.get("fields", {}).get("Status", "?")
            content_lines.append(f"• {title} [{status}]")
        sections.append("\n".join(content_lines))

    # System Status
    status = get_system_status()
    status_emoji = "✅" if status == "healthy" else "⚠️"
    sections.append(f"{status_emoji} Systems: {status}")

    # Footer
    sections.append("\n_I am your sword, I am your shield._")

    return "\n\n".join(sections)

def main():
    log("Morning briefing v2 starting...")

    # Run monitors first to refresh data
    monitors = [
        ("/root/clawd/scripts/trending-monitor.py", "Trending"),
        ("/root/clawd/scripts/indiehacker-monitor.py", "Indie Hacker"),
        ("/root/clawd/scripts/producthunt-monitor.py", "Product Hunt"),
        ("/root/clawd/scripts/google-trends-monitor.py", "Google Trends"),
        ("/root/clawd/scripts/twitter-trends-monitor.py", "Twitter Trends"),
        ("/root/clawd/scripts/youtube-trending-monitor.py", "YouTube"),
        ("/root/clawd/scripts/devto-hashnode-monitor.py", "Dev.to/Hashnode"),
        ("/root/clawd/scripts/substack-monitor.py", "Newsletters"),
        ("/root/clawd/scripts/exploding-topics-monitor.py", "Exploding Topics"),
    ]

    for script, name in monitors:
        try:
            subprocess.run(["python3", script], timeout=120, capture_output=True)
            log(f"{name} data refreshed")
        except Exception as e:
            log(f"{name} monitor failed: {e}")

    briefing = build_briefing()
    log(f"Briefing built ({len(briefing)} chars)")

    if send_telegram(briefing):
        log("✅ Briefing sent")
    else:
        log("❌ Failed to send")

if __name__ == "__main__":
    main()
