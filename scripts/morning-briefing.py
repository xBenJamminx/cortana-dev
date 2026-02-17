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


def _load_env():
    import os as _os
    env_path = _os.path.expanduser("~/.openclaw/.env")
    if _os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key = key.replace("export ", "").strip()
                    if key and not _os.environ.get(key):
                        _os.environ[key] = val
_load_env()

# Config
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = "-1003856131939"
BRIEFING_TOPIC_ID = 29  # Analytics & Monitoring topic
MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
GOOGLE_CREDS_FILE = "/root/.openclaw/google_credentials.json"
USER_MD = Path("/root/.openclaw/workspace/USER.md")
LOG_FILE = Path("/root/.openclaw/workspace/logs/briefing.log")
BIRD_ENV = Path(os.path.expanduser("~/.bird-env"))
AIRTABLE_PAT = os.environ.get("AIRTABLE_PAT", "")
AIRTABLE_BASE_ID = "appdFTSkXnphHLwfl"
AIRTABLE_TABLE_ID = "tblvLSX7DZxIRWU5g"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def send_telegram(message, parse_mode="Markdown"):
    """Send message to Telegram as one message, only split if over 4096 limit"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        MAX_LEN = 4000  # Telegram limit is 4096, small buffer

        def _send(text, pm=parse_mode):
            payload = {
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": pm,
                "disable_web_page_preview": True,
                "message_thread_id": BRIEFING_TOPIC_ID,
            }
            r = requests.post(url, json=payload, timeout=30)
            resp = r.json()
            if not resp.get("ok") and pm:
                # Retry without markdown if parsing fails
                payload.pop("parse_mode", None)
                r = requests.post(url, json=payload, timeout=30)
                return r.json().get("ok", False)
            return resp.get("ok", False)

        if len(message) <= MAX_LEN:
            return _send(message)

        # Only split if truly over limit — pack sections tightly
        import time
        sections = message.split("\n\n")
        chunks = []
        current = ""
        for section in sections:
            if current and len(current) + len(section) + 2 > MAX_LEN:
                chunks.append(current)
                current = section
            else:
                current = current + "\n\n" + section if current else section
        if current:
            chunks.append(current)

        success = True
        for chunk in chunks:
            success = _send(chunk) and success
            if len(chunks) > 1:
                time.sleep(0.3)
        return success
    except Exception as e:
        log(f"Telegram error: {e}")
        return False

def load_bird_env():
    """Load Bird CLI credentials from ~/.bird-env"""
    env = {}
    if BIRD_ENV.exists():
        with open(BIRD_ENV) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    env[key.strip()] = val.strip()
    return env

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
    """Get Twitter profile stats - not available via Bird CLI"""
    return None

def get_recent_tweets_engagement():
    """Get top tweets - DISABLED while @xBenJamminx is suspended"""
    return None

def get_airtable_content_queue():
    """Get pending content from Airtable (direct API, no Composio)"""
    try:
        resp = requests.get(
            f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}",
            headers={"Authorization": f"Bearer {AIRTABLE_PAT}"},
            params={
                "filterByFormula": "OR(Status='💡 Idea', Status='📝 Draft', Status='👀 Review', Status='✅ Approved', Status='📢 GTM Launch')",
                "pageSize": 10,
                "sort[0][field]": "Status",
                "sort[0][direction]": "asc"
            },
            timeout=15
        )
        if resp.status_code == 200:
            records = resp.json().get("records", [])
            return records[:8] if records else None
        else:
            log(f"Airtable API error: {resp.status_code}")
            return None
    except Exception as e:
        log(f"Airtable error: {e}")
        return None

def get_notion_tasks():
    """Notion tasks - not currently connected"""
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

def get_competitor_youtube():
    """Get latest YouTube videos from tracked channels"""
    try:
        conn = sqlite3.connect(MEMORY_DB)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT creator, content, url FROM competitor_content
            WHERE platform = 'youtube'
            AND created_at > datetime('now', '-48 hours')
            ORDER BY created_at DESC LIMIT 8
        ''')
        videos = cursor.fetchall()
        conn.close()
        return videos
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

def get_newsletter_content_topics():
    """Get top stories extracted from AI/creator newsletters.
    Returns individual stories with headlines, descriptions, and article links."""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    stories = []

    try:
        cursor.execute('''
            SELECT headline, description, article_url, source_name, relevance_score
            FROM newsletter_stories
            WHERE created_at > datetime('now', '-36 hours')
            ORDER BY relevance_score DESC, created_at DESC
            LIMIT 10
        ''')
        for headline, description, article_url, source_name, relevance in cursor.fetchall():
            stories.append({
                'headline': headline,
                'description': description or '',
                'url': article_url or '',
                'sender': source_name,
                'relevance': relevance,
            })
    except Exception as e:
        log(f"Newsletter stories query error: {e}")

    conn.close()
    return stories


def get_newsletter_nuggets():
    """Get nuggets (tutorials, tools, funding, etc.) from newsletters."""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    nuggets = []

    try:
        cursor.execute('''
            SELECT category, content, url, source_name
            FROM newsletter_nuggets
            WHERE created_at > datetime('now', '-36 hours')
            ORDER BY category, created_at DESC
        ''')
        for category, content, url, source_name in cursor.fetchall():
            nuggets.append({
                'category': category,
                'content': content or '',
                'url': url or '',
                'source': source_name,
            })
    except Exception as e:
        log(f"Newsletter nuggets query error: {e}")

    conn.close()
    return nuggets

def get_cross_source_hot_topics():
    """Get topics trending across multiple platforms (secondary signal)."""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    hot_topics = []

    try:
        cursor.execute('''
            SELECT topic, source_count, sources, mentions
            FROM hot_topics
            WHERE created_at > datetime('now', '-12 hours')
            AND source_count >= 3
            ORDER BY source_count DESC, created_at DESC
            LIMIT 5
        ''')
        for topic, source_count, sources_json, mentions_json in cursor.fetchall():
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


    # Top Tweets (previous day)
    engagement = get_recent_tweets_engagement()
    if engagement and engagement.get("top_tweets"):
        twitter_lines = ["📊 *Top Tweets*"]
        for t in engagement["top_tweets"]:
            text_preview = t["text"][:80].replace("\n", " ")
            # Sanitize for Telegram Markdown - escape problematic chars
            for ch in ['[', ']', '(', ')', '*', '_', '`']:
                text_preview = text_preview.replace(ch, '')
            twitter_lines.append(f"• {text_preview}")
            twitter_lines.append(f"  {t['likes']}❤ {t['retweets']}🔄 {t['replies']}💬 [link]({t['url']})")
        sections.append("\n".join(twitter_lines))

    # CONTENT TOPICS from newsletters (primary source)
    newsletter_stories = get_newsletter_content_topics()
    if newsletter_stories:
        topics_lines = ["📬 *CONTENT TOPICS* (from your newsletters)"]
        for story in newsletter_stories[:8]:
            headline = story['headline'][:70]
            sender = story['sender']
            url = story.get('url', '')
            description = story.get('description', '')

            # Multi-source indicator
            multi = "🔥 " if ',' in sender else ""

            # Headline with link if available
            if url:
                topics_lines.append(f"• {multi}[{headline}]({url}) _({sender})_")
            else:
                topics_lines.append(f"• {multi}*{headline}* _({sender})_")
            # Add description
            if description and len(description) > 20:
                import re as _re
                clean = _re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', description)
                clean = clean[:150]
                topics_lines.append(f"  _{clean}_")
        sections.append("\n".join(topics_lines))

    # NUGGETS from newsletters — grouped by category, deduped
    nuggets = get_newsletter_nuggets()
    if nuggets:
        cat_labels = {
            'TUTORIAL': '📖 How-To', 'TOOL': '🛠 Tools', 'FUNDING': '💰 Funding',
            'HIRING': '👔 Hiring', 'PROMPT': '💬 Prompts', 'TIP': '💡 Tips',
            'INSIGHT': '🧠 Insights'
        }
        # Deduplicate by first 40 chars of content
        seen = set()
        deduped = []
        for n in nuggets:
            key = n['content'][:40].lower().strip()
            if key not in seen:
                seen.add(key)
                deduped.append(n)

        # Group by category
        from collections import OrderedDict
        grouped = OrderedDict()
        for n in deduped[:15]:
            cat = n['category']
            grouped.setdefault(cat, []).append(n)

        nugget_lines = ["💎 *NUGGETS* (from your newsletters)"]
        for cat, items in grouped.items():
            label = cat_labels.get(cat, cat.title())
            nugget_lines.append(f"\n*{label}*")
            for n in items[:3]:
                url = n.get('url', '')
                content = n['content'][:120]
                if url:
                    nugget_lines.append(f"  • [{content}]({url}) _({n['source']})_")
                else:
                    nugget_lines.append(f"  • {content} _({n['source']})_")
        sections.append("\n".join(nugget_lines))

    # Cross-platform trending (only if 3+ platforms, secondary signal)
    hot_topics = get_cross_source_hot_topics()
    if hot_topics:
        trending_lines = ["🔥 *TRENDING* (3+ platforms)"]
        for ht in hot_topics[:3]:
            topic_name = ht['topic'][:50]
            source_count = ht['source_count']
            trending_lines.append(f"• *{topic_name}* ({source_count} platforms)")
        sections.append("\n".join(trending_lines))

    # Fresh Product Hunt launches
    ph_launches = get_producthunt_launches()
    if ph_launches:
        launch_lines = ["🚀 *Product Hunt Today*"]
        for item in (ph_launches or [])[:4]:
            title, tagline, url, votes = item
            votes_str = f" ({votes}⬆)" if votes else ""
            launch_lines.append(f"• [{title}]({url}){votes_str}")
        sections.append("\n".join(launch_lines))

    # YouTube - Latest from tracked channels
    yt_videos = get_competitor_youtube()
    if yt_videos:
        yt_lines = ["📺 *YouTube* (from tracked channels)"]
        for creator, title, url in yt_videos[:5]:
            # Truncate long titles
            title_short = title[:50] + "..." if len(title) > 50 else title
            yt_lines.append(f"• {creator}: [{title_short}]({url})")
        sections.append("\n".join(yt_lines))

    # Google Trends
    trends = get_google_trends()
    if trends:
        trend_lines = ["📈 *Google Trends*"]
        for term, category, traffic, url in trends[:4]:
            traffic_str = f" ({traffic})" if traffic else ""
            if url:
                trend_lines.append(f"• [{term}]({url}){traffic_str}")
            else:
                trend_lines.append(f"• {term}{traffic_str}")
        sections.append("\n".join(trend_lines))

    # System Status - check cron and key services
    status_parts = []
    try:
        import subprocess as _sp
        cron_check = _sp.run(["pgrep", "-x", "cron"], capture_output=True, timeout=5)
        status_parts.append("cron ✅" if cron_check.returncode == 0 else "cron ❌")
    except:
        status_parts.append("cron ❓")
    sections.append(f"⚙️ Systems: {', '.join(status_parts)}")

    # Footer
    sections.append("\n_I am your sword, I am your shield._")

    return "\n\n".join(sections)

def main():
    log("Morning briefing v2 starting...")

    # Run monitors first to refresh data
    SCRIPTS_DIR = "/root/.openclaw/workspace/scripts"
    monitors = [
        # Data collection from all sources
        (f"{SCRIPTS_DIR}/real-trends-monitor.py", "Real Trends (Google Daily, HN)"),
        (f"{SCRIPTS_DIR}/competitor-monitor.py", "Competitors"),
        (f"{SCRIPTS_DIR}/email-newsletter-monitor.py", "Email Newsletters"),
        (f"{SCRIPTS_DIR}/indiehacker-monitor.py", "Indie Hacker"),
        (f"{SCRIPTS_DIR}/producthunt-monitor.py", "Product Hunt"),
        (f"{SCRIPTS_DIR}/youtube-trending-monitor.py", "YouTube"),
        # CRITICAL: Topic aggregator runs LAST - finds cross-source hot topics
        (f"{SCRIPTS_DIR}/topic-aggregator.py", "Topic Aggregator"),
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
