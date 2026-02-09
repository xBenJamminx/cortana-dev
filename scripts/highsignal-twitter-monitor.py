#!/usr/bin/env python3
"""
High-Signal Twitter Monitor v3 - Uses Bird CLI with dual account cookies

Fetches tweets from curated high-signal accounts using Bird CLI.
Rotates between two accounts to avoid rate limits.
Extracts topics from tweet CONTENT using Claude.
No hardcoded keyword searches - purely organic discovery.
"""
import sqlite3
import subprocess
import json
import os
import re
import sys
import logging
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import time

# Setup lib path
sys.path.insert(0, "/root/clawd")
from lib.retry import retry_with_backoff
from lib.alerting import send_alert

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/highsignal-twitter.log")
COOKIE_FILE = Path("/root/.config/bird/cookies.json")
CONFIG_FILE = Path("/root/clawd/config/high_signal_sources.json")
SUCCESS_MARKER = Path("/root/clawd/logs/.twitter-monitor-last-success")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("twitter-monitor")

# Fallback high-signal accounts if config not found
DEFAULT_HIGH_SIGNAL_ACCOUNTS = [
    # AI Labs & Official
    "OpenAI", "AnthropicAI", "GoogleDeepMind", "xai", "NVIDIAAI",
    # Researchers & Thought Leaders
    "karpathy", "sama", "ylecun", "fchollet", "demishassabis",
    "lexfridman", "DrJimFan",
    # AI News & Newsletters
    "rowancheung", "TheRundownAI", "kimmonismus", "_akhaliq",
    "bensbites", "theneuron", "superhumanai", "tldrai",
    "theresanaiforthat", "AravSrinivas",
    # Builders & Creators
    "LinusEkenstam", "levelsio", "LiamOttley", "mattshumer_",
    "hwchase17", "mckaywrigley", "swyx", "bentossell",
    "dannypostmaa", "marc_louvion", "skirank",
]

def load_config():
    """Load high-signal accounts from config file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                return config.get("twitter_accounts", DEFAULT_HIGH_SIGNAL_ACCOUNTS)
        except Exception as e:
            log.warning("Failed to load config: %s", e)
    return DEFAULT_HIGH_SIGNAL_ACCOUNTS

def load_cookies():
    """Load cookies for both accounts"""
    if COOKIE_FILE.exists():
        with open(COOKIE_FILE) as f:
            return json.load(f)
    return None

def ensure_tables():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS highsignal_tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id TEXT UNIQUE,
            author TEXT,
            text TEXT,
            topic TEXT,
            likes INTEGER,
            retweets INTEGER,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discovered_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            mention_count INTEGER,
            accounts TEXT,
            sample_tweets TEXT,
            source TEXT DEFAULT 'twitter',
            created_at TEXT,
            UNIQUE(topic, created_at)
        )
    """)
    conn.commit()
    conn.close()

@retry_with_backoff(
    max_retries=2,
    base_delay=5.0,
    retryable_exceptions=(subprocess.TimeoutExpired, json.JSONDecodeError),
    on_exhausted=lambda e: send_alert(
        "twitter_bird_cli",
        f"Bird CLI failed after retries: {e}",
        level="warning",
        cooldown=3600,
    ),
)
def fetch_user_tweets_bird(username, auth_token, ct0, count=5):
    """Fetch recent tweets from a user using Bird CLI"""
    result = subprocess.run(
        ["bird", "search", f"from:{username}", "--json", "-n", str(count),
         "--auth-token", auth_token, "--ct0", ct0],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        stderr = result.stderr[:200]
        # Check for rate limit
        if "429" in stderr or "rate" in stderr.lower():
            log.warning("Rate limited fetching @%s: %s", username, stderr[:100])
            raise Exception(f"Rate limited for @{username}")
        log.warning("Bird CLI error for @%s: %s", username, stderr[:100])
        return []

    tweets = []
    data = json.loads(result.stdout)
    items = data if isinstance(data, list) else data.get("tweets", [])

    for tweet in items:
        text = tweet.get("text", "") or tweet.get("full_text", "")
        # Skip retweets
        if text.startswith("RT @"):
            continue

        metrics = tweet.get("public_metrics", {})
        tweets.append({
            "tweet_id": str(tweet.get("id", "") or tweet.get("id_str", "")),
            "author": username,
            "text": text,
            "likes": tweet.get("favorite_count", 0) or metrics.get("like_count", 0),
            "retweets": tweet.get("retweet_count", 0) or metrics.get("retweet_count", 0),
            "created_at": tweet.get("created_at")
        })

    return tweets

def extract_topics_with_claude(tweets_batch):
    """Use Claude to extract topics from a batch of tweets"""
    if not tweets_batch:
        return {}

    # Format tweets for Claude
    tweet_list = "\n".join([
        f"{i+1}. @{t['author']}: {t['text'][:280]}"
        for i, t in enumerate(tweets_batch[:20])
    ])

    prompt = f"""Analyze these tweets from tech/AI thought leaders. For each tweet, extract the main topic they're discussing in 3-8 words. Be SPECIFIC - not "AI" but "Claude 4 coding agents" or "OpenAI ads in ChatGPT" or "Xcode 26 MCP integration".

If a tweet is just personal/off-topic/promotional without news, write "SKIP".

Tweets:
{tweet_list}

Respond with just the topics, one per line, numbered to match:
1. [topic]
2. [topic]
..."""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, timeout=60
        )

        if result.returncode != 0:
            log.error("Claude extraction failed: %s", result.stderr[:200])
            return {}

        topics = {}
        for line in result.stdout.strip().split("\n"):
            match = re.match(r'^(\d+)\.\s*(.+)$', line.strip())
            if match:
                idx = int(match.group(1)) - 1
                topic = match.group(2).strip()
                if idx < len(tweets_batch) and topic.upper() != "SKIP":
                    topics[tweets_batch[idx]['tweet_id']] = topic

        return topics
    except Exception as e:
        log.error("Claude extraction error: %s", e)
        return {}

def aggregate_topics(all_tweets_with_topics):
    """Aggregate topics to find what multiple accounts are discussing"""
    topic_data = defaultdict(lambda: {
        "accounts": set(),
        "tweets": [],
        "total_likes": 0,
        "total_retweets": 0
    })

    for tweet in all_tweets_with_topics:
        topic = tweet.get("topic")
        if not topic:
            continue

        topic_key = topic.lower().strip()

        topic_data[topic_key]["accounts"].add(tweet["author"])
        topic_data[topic_key]["tweets"].append(tweet)
        topic_data[topic_key]["total_likes"] += tweet.get("likes", 0)
        topic_data[topic_key]["total_retweets"] += tweet.get("retweets", 0)

        if "display_name" not in topic_data[topic_key]:
            topic_data[topic_key]["display_name"] = topic

    results = []
    for topic_key, data in topic_data.items():
        results.append({
            "topic": data.get("display_name", topic_key),
            "account_count": len(data["accounts"]),
            "accounts": list(data["accounts"]),
            "total_likes": data["total_likes"],
            "total_retweets": data["total_retweets"],
            "sample_tweets": data["tweets"][:5]
        })

    results.sort(key=lambda x: (x["account_count"], x["total_likes"] + x["total_retweets"]), reverse=True)
    return results

def save_discovered_topics(topics):
    """Save discovered topics to database"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:00")
    saved = 0

    for t in topics[:30]:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO discovered_topics
                (topic, mention_count, accounts, sample_tweets, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                t["topic"],
                t["account_count"],
                json.dumps(t["accounts"]),
                json.dumps([{
                    "author": tw["author"],
                    "text": tw["text"][:200],
                    "likes": tw.get("likes", 0),
                    "retweets": tw.get("retweets", 0)
                } for tw in t["sample_tweets"]]),
                "twitter_highsignal",
                now
            ))
            saved += 1
        except Exception as e:
            log.error("Error saving topic: %s", e)

    conn.commit()
    conn.close()
    return saved

def touch_success_marker():
    """Touch a marker file so the watchdog knows this ran successfully."""
    SUCCESS_MARKER.parent.mkdir(parents=True, exist_ok=True)
    SUCCESS_MARKER.write_text(datetime.now().isoformat())

def main():
    log.info("High-Signal Twitter Monitor v3 (Bird CLI) starting...")
    ensure_tables()

    # Load cookies
    cookies = load_cookies()
    if not cookies:
        log.error("No cookies found at %s", COOKIE_FILE)
        send_alert(
            "twitter_no_cookies",
            "Twitter monitor: no cookies found. Cannot fetch tweets.",
            level="warning",
            cooldown=3600,
        )
        return

    # Get both accounts
    accounts_creds = []
    for account_name in ["xbenjamminx", "cortanaops"]:
        if account_name in cookies:
            accounts_creds.append({
                "name": account_name,
                "auth_token": cookies[account_name]["auth_token"],
                "ct0": cookies[account_name]["ct0"]
            })

    if not accounts_creds:
        log.error("No valid account credentials found")
        send_alert(
            "twitter_no_creds",
            "Twitter monitor: no valid account credentials in cookies file.",
            level="warning",
            cooldown=3600,
        )
        return

    log.info("Loaded credentials for %d accounts", len(accounts_creds))

    # Load high-signal accounts to monitor
    target_accounts = load_config()
    log.info("Monitoring %d high-signal accounts", len(target_accounts))

    # Fetch tweets, rotating between our auth accounts
    all_tweets = []
    cred_index = 0
    fetch_errors = 0

    for i, username in enumerate(target_accounts):
        # Rotate credentials
        cred = accounts_creds[cred_index % len(accounts_creds)]
        cred_index += 1

        log.info("[%d/%d] Fetching @%s (using %s)...", i + 1, len(target_accounts), username, cred["name"])

        try:
            tweets = fetch_user_tweets_bird(
                username,
                cred["auth_token"],
                cred["ct0"],
                count=5
            )
            all_tweets.extend(tweets)
        except Exception as e:
            fetch_errors += 1
            log.error("Failed to fetch @%s: %s", username, e)

        # Small delay to be nice to Twitter
        time.sleep(0.5)

    log.info("Fetched %d tweets from %d accounts (%d errors)",
             len(all_tweets), len(target_accounts), fetch_errors)

    # Alert if too many fetch errors
    if fetch_errors > len(target_accounts) * 0.5:
        send_alert(
            "twitter_high_error_rate",
            f"Twitter monitor: {fetch_errors}/{len(target_accounts)} accounts failed to fetch. "
            f"Possible rate limit or cookie expiry.",
            level="warning",
            cooldown=3600,
        )

    if not all_tweets:
        log.warning("No tweets fetched, exiting")
        send_alert(
            "twitter_no_tweets",
            "Twitter monitor: zero tweets fetched from all accounts.",
            level="warning",
            cooldown=3600,
        )
        return

    # Extract topics using Claude
    log.info("Extracting topics with Claude...")

    batch_size = 20
    all_topics = {}

    for i in range(0, len(all_tweets), batch_size):
        batch = all_tweets[i:i+batch_size]
        topics = extract_topics_with_claude(batch)
        all_topics.update(topics)
        log.info("Processed batch %d, extracted %d topics", i // batch_size + 1, len(topics))

    # Apply topics to tweets
    for tweet in all_tweets:
        if tweet["tweet_id"] in all_topics:
            tweet["topic"] = all_topics[tweet["tweet_id"]]

    # Filter to tweets with topics
    tweets_with_topics = [t for t in all_tweets if t.get("topic")]
    log.info("Extracted topics from %d tweets", len(tweets_with_topics))

    # Aggregate to find trending
    discovered = aggregate_topics(tweets_with_topics)
    log.info("Found %d distinct topics", len(discovered))

    # Save to database
    saved = save_discovered_topics(discovered)
    log.info("Saved %d topics", saved)

    # Touch success marker for watchdog freshness monitoring
    touch_success_marker()

    # Print report
    print("\n" + "="*60)
    print("HIGH-SIGNAL TWITTER TOPICS (via Bird CLI)")
    print("="*60)

    hot_topics = [t for t in discovered if t["account_count"] >= 2]
    single_topics = [t for t in discovered if t["account_count"] == 1][:15]

    if hot_topics:
        print("\nMULTIPLE ACCOUNTS DISCUSSING:")
        for t in hot_topics[:10]:
            accounts_str = ", ".join([f"@{a}" for a in t["accounts"][:4]])
            if len(t["accounts"]) > 4:
                accounts_str += f" +{len(t['accounts'])-4} more"
            engagement = t["total_likes"] + t["total_retweets"]
            print(f"\n   **{t['topic']}**")
            print(f"   {t['account_count']} accounts: {accounts_str}")
            print(f"   {engagement:,} total engagement ({t['total_likes']:,} likes, {t['total_retweets']:,} RTs)")

    if single_topics:
        print("\nSINGLE ACCOUNT MENTIONS (watch list):")
        for t in single_topics[:10]:
            engagement = t["total_likes"] + t["total_retweets"]
            print(f"   - {t['topic']} (@{t['accounts'][0]}) [{engagement:,} engagement]")

    print("\n" + "="*60)
    log.info("Done")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("Twitter monitor crashed: %s", e)
        send_alert(
            "twitter_crash",
            f"Twitter monitor crashed: {e}",
            level="critical",
            cooldown=3600,
        )
        sys.exit(1)
