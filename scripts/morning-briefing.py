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
    """Send message to Telegram, splitting if too long"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        # Telegram limit is 4096, but stay safe at 3500
        MAX_LEN = 3500

        if len(message) <= MAX_LEN:
            r = requests.post(url, json={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }, timeout=30)
            return r.json().get("ok", False)
        else:
            # Split into multiple messages by sections
            import time
            sections = message.split("\n\n")
            current_msg = ""
            success = True

            for section in sections:
                if len(current_msg) + len(section) + 2 > MAX_LEN:
                    # Send current message
                    if current_msg.strip():
                        r = requests.post(url, json={
                            "chat_id": CHAT_ID,
                            "text": current_msg,
                            "parse_mode": parse_mode,
                            "disable_web_page_preview": True
                        }, timeout=30)
                        success = success and r.json().get("ok", False)
                        time.sleep(0.5)
                    current_msg = section
                else:
                    current_msg = current_msg + "\n\n" + section if current_msg else section

            # Send remaining
            if current_msg.strip():
                r = requests.post(url, json={
                    "chat_id": CHAT_ID,
                    "text": current_msg,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True
                }, timeout=30)
                success = success and r.json().get("ok", False)

            return success
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

def get_cross_source_hot_topics():
    """Get topics that are trending ACROSS multiple sources.
    This is the key insight: if something is mentioned on HN + Twitter + Newsletter,
    it's actually hot - not just 'here are articles from IndieHackers'."""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    hot_topics = []

    try:
        cursor.execute('''
            SELECT topic, source_count, sources, mentions
            FROM hot_topics
            WHERE created_at > datetime('now', '-12 hours')
            ORDER BY source_count DESC, created_at DESC
            LIMIT 15
        ''')
        for topic, source_count, sources_json, mentions_json in cursor.fetchall():
            # Skip generic words
            if topic.lower() in ['how', 'what', 'here', 'this', 'that', 'with', 'from', 'your']:
                continue

            sources = json.loads(sources_json) if sources_json else []
            mentions = json.loads(mentions_json) if mentions_json else []

            hot_topics.append({
                'topic': topic,
                'source_count': source_count,
                'sources': sources,
                'mentions': mentions
            })
    except Exception as e:
        log(f"Hot topics query error: {e}")

    conn.close()
    return hot_topics

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

    # HOT TOPICS - Topics trending ACROSS multiple sources
    hot_topics = get_cross_source_hot_topics()
    if hot_topics:
        topics_lines = ["🔥 *HOT TOPICS* (trending across multiple sources)"]

        seen_topics = set()
        shown = 0
        for ht in hot_topics:
            if shown >= 8:
                break

            topic_name = ht['topic'].upper()

            # Skip duplicates
            if topic_name in seen_topics:
                continue
            seen_topics.add(topic_name)

            source_count = ht['source_count']
            sources = ', '.join(ht['sources'][:4])

            topics_lines.append(f"\n*{topic_name}* — {source_count} sources")
            topics_lines.append(f"_{sources}_")

            # Show 2 example mentions with links (dedupe URLs too)
            seen_urls = set()
            mention_count = 0
            for mention in ht['mentions']:
                if mention_count >= 2:
                    break
                url = mention.get('url', '')
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                text = mention.get('text', '')[:55]
                source = mention.get('source_full', '').replace('@@', '@')

                if url:
                    topics_lines.append(f"  • [{text}...]({url})")
                else:
                    topics_lines.append(f"  • {text}...")
                topics_lines.append(f"    _{source}_")
                mention_count += 1

            shown += 1

        sections.append("\n".join(topics_lines))

    # Fresh Product Hunt launches only (IH is now in hot topics)
    ph_launches = get_producthunt_launches()
    if ph_launches:
        launch_lines = ["🚀 *Product Hunt Today*"]
        for item in (ph_launches or [])[:4]:
            title, tagline, url, votes = item
            votes_str = f" ({votes}⬆)" if votes else ""
            launch_lines.append(f"• [{title}]({url}){votes_str}")
        sections.append("\n".join(launch_lines))

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
        # Data collection from all sources
        ("/root/clawd/scripts/real-trends-monitor.py", "Real Trends (Google Daily, HN)"),
        ("/root/clawd/scripts/competitor-monitor.py", "Competitors"),
        ("/root/clawd/scripts/email-newsletter-monitor.py", "Email Newsletters"),
        ("/root/clawd/scripts/indiehacker-monitor.py", "Indie Hacker"),
        ("/root/clawd/scripts/producthunt-monitor.py", "Product Hunt"),
        ("/root/clawd/scripts/youtube-trending-monitor.py", "YouTube"),
        ("/root/clawd/scripts/devto-hashnode-monitor.py", "Dev.to/Hashnode"),
        # CRITICAL: Topic aggregator runs LAST - finds cross-source hot topics
        ("/root/clawd/scripts/topic-aggregator.py", "Topic Aggregator"),
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
