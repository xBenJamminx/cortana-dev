#!/usr/bin/env python3
"""
Topic Aggregator v6 - Smart trending detection

TWO types of signals:
1. CROSS-PLATFORM TRENDING - Same story on 2+ platforms (confirmed hot)
2. SINGLE-PLATFORM EXPLOSION - Viral on ONE platform, early signal to be first

Output:
- 🔴 TRENDING (3+ platforms)
- 🟡 SPREADING (2 platforms)
- ⚡ EXPLODING (viral on 1 platform - 10X normal engagement)
"""
import sqlite3
import json
import re
import requests
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/topic-aggregator.log")

# Baseline engagement thresholds (what's "normal")
# Anything significantly above this = exploding
BASELINE = {
    "hackernews": 150,      # Average front page post ~150 pts
    "reddit": 100,          # Average hot post ~100 pts
    "twitter": 30,          # Average trending topic ~30 posts
    "youtube": 1,           # Any video counts
    "producthunt": 100,     # Average launch ~100 votes
    "dev.to": 50,           # Average article ~50 reactions
    "news": 1,              # Any news coverage counts
    "newsletter": 1,        # Any newsletter mention counts
}

# Multiplier for "exploding" - 5X baseline = exploding
EXPLOSION_MULTIPLIER = 5

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def normalize_url(url):
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.rstrip("/")
        return f"{domain}{path}"
    except:
        return url.lower()

def title_similarity(t1, t2):
    if not t1 or not t2:
        return 0
    t1 = re.sub(r'[^\w\s]', '', t1.lower())
    t2 = re.sub(r'[^\w\s]', '', t2.lower())
    words1 = set(t1.split())
    words2 = set(t2.split())
    if not words1 or not words2:
        return 0
    overlap = len(words1 & words2)
    total = min(len(words1), len(words2))
    return overlap / total if total > 0 else 0

def extract_entities(text):
    if not text:
        return set()
    text_lower = text.lower()
    entities = set()
    KEYWORDS = [
        "claude", "anthropic", "openai", "chatgpt", "gpt-4", "gpt-5",
        "gemini", "grok", "copilot", "cursor", "windsurf", "xcode",
        "mcp", "ollama", "deepseek", "llama", "mistral", "qwen",
        "ghidra", "n8n", "supabase", "vercel", "deno", "bun",
        "openclaw", "huggingface", "langchain", "vapi", "retell",
        "coding agent", "ai agent", "vibe coding", "ad-free", "ads",
    ]
    for kw in KEYWORDS:
        if kw in text_lower:
            entities.add(kw)
    return entities

def normalize_title(text):
    if not text:
        return ""
    text = re.sub(r'^(Show HN:|Ask HN:|Launch HN:|Tell HN:)\s*', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:150]

def is_good_title(title):
    if not title or len(title) < 25:
        return False
    if title.lower().strip() in ["claude", "openai", "mcp", "chatgpt", "xcode"]:
        return False
    if title.lower().startswith(("i ", "my ", "just ", "we ", "people ", "here ")):
        return False
    return True

def items_match(item1, item2):
    url1 = normalize_url(item1.get("url", ""))
    url2 = normalize_url(item2.get("url", ""))
    if url1 and url2 and url1 == url2:
        return True
    sim = title_similarity(item1.get("title", ""), item2.get("title", ""))
    if sim >= 0.5:
        return True
    entities1 = item1.get("entities", set())
    entities2 = item2.get("entities", set())
    if len(entities1 & entities2) >= 2:
        return True
    return False

def is_exploding(source_type, score):
    """Check if this score is significantly above baseline"""
    baseline = BASELINE.get(source_type, 50)
    return score >= baseline * EXPLOSION_MULTIPLIER

def fetch_reddit_hot(subreddit):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; TrendBot/1.0)"}
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            posts = []
            for post in resp.json().get("data", {}).get("children", []):
                p = post.get("data", {})
                posts.append({
                    "title": p.get("title", ""),
                    "url": f"https://reddit.com{p.get('permalink', '')}",
                    "external_url": p.get("url", ""),
                    "score": p.get("score", 0)
                })
            return posts
    except:
        pass
    return []

def gather_all_content():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    all_content = []

    # 1. REDDIT
    log("Fetching Reddit...")
    reddit_subs = json.load(open("/root/clawd/config/high_signal_sources.json"))["reddit_subreddits"]
    for sub in reddit_subs:
        posts = fetch_reddit_hot(sub)
        for p in posts[:8]:
            title = normalize_title(p["title"])
            entities = extract_entities(title)
            if is_good_title(title):
                all_content.append({
                    "title": title,
                    "source": f"reddit/r/{sub}",
                    "source_type": "reddit",
                    "url": p.get("external_url") or p["url"],
                    "entities": entities,
                    "engagement": f"{p['score']}pts",
                    "score": p["score"],
                    "is_exploding": is_exploding("reddit", p["score"])
                })
        import time
        time.sleep(0.3)

    # 2. HACKER NEWS
    log("Reading HN...")
    try:
        cursor.execute("""
            SELECT title, url, score FROM indiehacker_posts
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY score DESC
        """)
        for title, url, score in cursor.fetchall():
            title = normalize_title(title)
            if is_good_title(title):
                all_content.append({
                    "title": title,
                    "source": "hackernews",
                    "source_type": "hackernews",
                    "url": url,
                    "entities": extract_entities(title),
                    "engagement": f"{score}pts",
                    "score": score or 0,
                    "is_exploding": is_exploding("hackernews", score or 0)
                })
    except:
        pass

    # 3. NEWS/TRENDS
    try:
        cursor.execute("""
            SELECT topic, source, url, traffic FROM real_trends
            WHERE created_at > datetime('now', '-24 hours')
        """)
        for topic, source, url, traffic in cursor.fetchall():
            title = normalize_title(topic)
            if is_good_title(title):
                all_content.append({
                    "title": title,
                    "source": source or "news",
                    "source_type": "news",
                    "url": url,
                    "entities": extract_entities(title),
                    "engagement": traffic or "",
                    "score": 50,
                    "is_exploding": False
                })
    except:
        pass

    # 4. YOUTUBE
    log("Reading YouTube...")
    try:
        cursor.execute("""
            SELECT title, channel, url FROM youtube_videos
            WHERE created_at > datetime('now', '-48 hours')
        """)
        for title, channel, url in cursor.fetchall():
            title = normalize_title(title)
            if is_good_title(title):
                all_content.append({
                    "title": title,
                    "source": f"youtube/{channel}",
                    "source_type": "youtube",
                    "url": url,
                    "entities": extract_entities(title),
                    "engagement": "video",
                    "score": 100,
                    "is_exploding": False
                })
    except:
        pass

    # 5. DEV.TO
    try:
        cursor.execute("""
            SELECT title, source, url, reactions FROM devto_posts
            WHERE created_at > datetime('now', '-48 hours')
        """)
        for title, source, url, reactions in cursor.fetchall():
            title = normalize_title(title)
            if is_good_title(title):
                all_content.append({
                    "title": title,
                    "source": source or "dev.to",
                    "source_type": "dev.to",
                    "url": url,
                    "entities": extract_entities(title),
                    "engagement": f"{reactions} reactions",
                    "score": reactions or 0,
                    "is_exploding": is_exploding("dev.to", reactions or 0)
                })
    except:
        pass

    # 6. PRODUCT HUNT
    try:
        cursor.execute("""
            SELECT title, tagline, url, votes FROM producthunt_posts
            WHERE created_at > datetime('now', '-24 hours')
        """)
        for title, tagline, url, votes in cursor.fetchall():
            full_title = f"{title}: {tagline}" if tagline else title
            full_title = normalize_title(full_title)
            if is_good_title(full_title):
                all_content.append({
                    "title": full_title,
                    "source": "producthunt",
                    "source_type": "producthunt",
                    "url": url,
                    "entities": extract_entities(full_title),
                    "engagement": f"{votes}pts",
                    "score": votes or 0,
                    "is_exploding": is_exploding("producthunt", votes or 0)
                })
    except:
        pass

    # 7. NEWSLETTERS
    try:
        cursor.execute("""
            SELECT title, newsletter, url FROM substack_posts
            WHERE created_at > datetime('now', '-48 hours')
        """)
        for title, newsletter, url in cursor.fetchall():
            title = normalize_title(title)
            if is_good_title(title):
                all_content.append({
                    "title": title,
                    "source": f"newsletter/{newsletter}",
                    "source_type": "newsletter",
                    "url": url,
                    "entities": extract_entities(title),
                    "engagement": "newsletter",
                    "score": 50,
                    "is_exploding": False
                })
    except:
        pass

    # 8. TWITTER (high-engagement topics)
    log("Reading Twitter...")
    try:
        cursor.execute("""
            SELECT topic, post_count, topic_type, urls FROM twitter_topics
            WHERE created_at > datetime('now', '-12 hours')
            ORDER BY post_count DESC LIMIT 30
        """)
        for topic, post_count, topic_type, urls_json in cursor.fetchall():
            if topic_type == 'linked_content' and is_good_title(topic):
                urls = json.loads(urls_json) if urls_json else []
                all_content.append({
                    "title": normalize_title(topic),
                    "source": "twitter",
                    "source_type": "twitter",
                    "url": urls[0] if urls else "",
                    "entities": extract_entities(topic),
                    "engagement": f"{post_count} tweets",
                    "score": post_count,
                    "is_exploding": is_exploding("twitter", post_count)
                })
            elif topic_type == 'entity' and post_count >= 50:
                # High-engagement entity = something big happening
                all_content.append({
                    "title": f"{topic} trending on Twitter",
                    "source": "twitter",
                    "source_type": "twitter",
                    "url": "",
                    "entities": extract_entities(topic),
                    "engagement": f"{post_count} tweets",
                    "score": post_count,
                    "is_exploding": is_exploding("twitter", post_count)
                })
    except Exception as e:
        log(f"Twitter error: {e}")

    conn.close()
    return all_content

def cluster_and_detect(all_content):
    """Cluster for cross-platform AND detect single-platform explosions"""
    clusters = []
    used_indices = set()

    # First pass: cluster matching items
    for i, item in enumerate(all_content):
        if i in used_indices:
            continue

        source_type = item["source_type"]
        cluster = {
            "sources": {source_type},
            "items": [item],
            "max_score": item["score"],
            "has_explosion": item.get("is_exploding", False)
        }
        used_indices.add(i)

        for j, other in enumerate(all_content):
            if j in used_indices:
                continue
            if items_match(item, other):
                other_source = other["source_type"]
                if other_source not in cluster["sources"]:
                    cluster["sources"].add(other_source)
                cluster["items"].append(other)
                cluster["max_score"] = max(cluster["max_score"], other["score"])
                if other.get("is_exploding"):
                    cluster["has_explosion"] = True
                used_indices.add(j)

        clusters.append(cluster)

    # Categorize results
    trending = []      # 3+ platforms
    spreading = []     # 2 platforms
    exploding = []     # 1 platform but viral

    for cluster in clusters:
        items = cluster["items"]
        best_item = max(items, key=lambda x: x["score"])

        # Dedupe by URL
        seen_urls = set()
        unique_items = []
        for item in items:
            url = normalize_url(item.get("url", ""))
            if not url or url not in seen_urls:
                if url:
                    seen_urls.add(url)
                unique_items.append(item)

        topic_data = {
            "topic": best_item["title"],
            "source_count": len(cluster["sources"]),
            "sources": list(cluster["sources"]),
            "max_score": cluster["max_score"],
            "is_exploding": cluster["has_explosion"],
            "mentions": [
                {
                    "source": i["source"],
                    "text": i["title"][:80],
                    "url": i["url"],
                    "engagement": i["engagement"],
                    "exploding": i.get("is_exploding", False)
                }
                for i in unique_items[:5]
            ]
        }

        if len(cluster["sources"]) >= 3:
            trending.append(topic_data)
        elif len(cluster["sources"]) >= 2:
            spreading.append(topic_data)
        elif cluster["has_explosion"]:
            # Single platform but exploding
            exploding.append(topic_data)

    # Sort each category
    trending.sort(key=lambda x: (x["source_count"], x["max_score"]), reverse=True)
    spreading.sort(key=lambda x: x["max_score"], reverse=True)
    exploding.sort(key=lambda x: x["max_score"], reverse=True)

    return trending, spreading, exploding

def save_hot_topics(trending, spreading, exploding):
    """Save all categories to database"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hot_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            source_count INTEGER,
            sources TEXT,
            mentions TEXT,
            category TEXT,
            created_at TEXT,
            UNIQUE(topic, created_at)
        )
    """)

    now = datetime.now().strftime("%Y-%m-%d %H:00")
    saved = 0

    for category, items in [("trending", trending), ("spreading", spreading), ("exploding", exploding)]:
        for ht in items[:10]:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO hot_topics
                    (topic, source_count, sources, mentions, category, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    ht["topic"], ht["source_count"],
                    json.dumps(ht["sources"]), json.dumps(ht["mentions"]),
                    category, now
                ))
                saved += 1
            except:
                pass

    conn.commit()
    conn.close()
    return saved

def get_hot_topics_for_briefing():
    """Get all hot topics for morning briefing"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    results = {"trending": [], "spreading": [], "exploding": []}

    for category in ["trending", "spreading", "exploding"]:
        cursor.execute("""
            SELECT topic, source_count, sources, mentions
            FROM hot_topics
            WHERE created_at > datetime('now', '-12 hours')
            AND category = ?
            ORDER BY source_count DESC
            LIMIT 10
        """, (category,))

        for topic, source_count, sources_json, mentions_json in cursor.fetchall():
            results[category].append({
                "topic": topic,
                "source_count": source_count,
                "sources": json.loads(sources_json),
                "mentions": json.loads(mentions_json)[:5]
            })

    conn.close()
    return results

def main():
    log("Topic Aggregator v6 - Smart trending detection")

    all_content = gather_all_content()
    log(f"Gathered {len(all_content)} content items")

    trending, spreading, exploding = cluster_and_detect(all_content)
    log(f"Found: {len(trending)} trending, {len(spreading)} spreading, {len(exploding)} exploding")

    saved = save_hot_topics(trending, spreading, exploding)
    log(f"Saved {saved} topics")

    # Print report
    print("\n" + "="*60)
    print("📊 CONTENT INTEL REPORT")
    print("="*60)

    if trending:
        print("\n🔴 TRENDING (3+ platforms - confirmed hot)")
        for t in trending[:5]:
            print(f"\n   **{t['topic']}**")
            print(f"   Platforms: {', '.join(t['sources'])}")
            for m in t["mentions"][:2]:
                print(f"   • [{m['source']}] {m['engagement']}")

    if spreading:
        print("\n🟡 SPREADING (2 platforms)")
        for t in spreading[:5]:
            print(f"\n   **{t['topic']}**")
            print(f"   Platforms: {', '.join(t['sources'])}")
            for m in t["mentions"][:2]:
                print(f"   • [{m['source']}] {m['engagement']}")

    if exploding:
        print("\n⚡ EXPLODING (viral on 1 platform - early signal!)")
        for t in exploding[:5]:
            exp_mention = next((m for m in t["mentions"] if m.get("exploding")), t["mentions"][0])
            print(f"\n   **{t['topic']}**")
            print(f"   🚀 {exp_mention['engagement']} on {exp_mention['source']}")

    if not trending and not spreading and not exploding:
        print("\nNo significant trending topics detected right now.")

    print("\n" + "="*60)
    log("Done")

if __name__ == "__main__":
    main()
