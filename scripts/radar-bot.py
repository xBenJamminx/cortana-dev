#!/usr/bin/env python3
"""
Telegram Bot for Reply Radar — listens for /commands and runs searches.

Commands:
  /radar              — Run full radar (all pillars, last 3h)
  /radar ai_tools     — Run specific pillar
  /radar 6h           — Custom time window
  /radar ai_tools 6h  — Pillar + time window
  /search <query>     — Custom one-off X search
  /pillars            — List available pillars
  /help               — Show commands

Runs as a long-polling bot. Start with:
  python3 scripts/radar-bot.py &
"""

import json, os, sys, time, subprocess, re
from datetime import datetime, timezone, timedelta
import urllib.request

# ── Import radar functions ────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import util as importutil

# Load reply-radar module
spec = importutil.spec_from_file_location("reply_radar", os.path.join(os.path.dirname(os.path.abspath(__file__)), "reply-radar.py"))
radar = importutil.module_from_spec(spec)
spec.loader.exec_module(radar)

# ── Config ────────────────────────────────────────────────────────────────

BOT_TOKEN = radar.TELEGRAM_BOT_TOKEN
CHAT_ID = radar.TELEGRAM_CHAT_ID
POLL_INTERVAL = 2  # seconds between polling
LOG_FILE = "/root/.openclaw/workspace/logs/radar-bot.log"


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def send_message(chat_id: str, text: str, reply_to: int = None):
    """Send a message via Telegram Bot API."""
    # Split long messages at 4096 char limit
    chunks = []
    while len(text) > 4000:
        # Try to split at a newline
        split_at = text.rfind("\n", 0, 4000)
        if split_at == -1:
            split_at = 4000
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    chunks.append(text)

    for i, chunk in enumerate(chunks):
        payload = json.dumps({
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
            **({"reply_to_message_id": reply_to} if reply_to and i == 0 else {}),
        }).encode()

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                json.loads(resp.read())
        except Exception as e:
            log(f"Send error: {e}")

        if i < len(chunks) - 1:
            time.sleep(0.3)


def get_updates(offset: int = None) -> list:
    """Long-poll for new messages."""
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    payload = json.dumps(params).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                return result.get("result", [])
    except Exception as e:
        log(f"Poll error: {e}")
        time.sleep(5)
    return []


def handle_radar(args_str: str, chat_id: str, msg_id: int):
    """Handle /radar command."""
    parts = args_str.strip().split() if args_str.strip() else []

    pillar = "all"
    since = 3
    max_age = 3
    min_followers = 5000
    min_likes = 10
    top_n = 10

    for part in parts:
        # Check if it's a time spec like "6h" or "12h"
        time_match = re.match(r'^(\d+)h$', part)
        if time_match:
            since = int(time_match.group(1))
            max_age = since
            continue
        # Check if it's a number (top N)
        if part.isdigit():
            top_n = int(part)
            continue
        # Check if it's a pillar name
        if part in radar.SEARCH_QUERIES:
            pillar = part
            continue
        # Check partial match
        matches = [k for k in radar.SEARCH_QUERIES if part in k]
        if matches:
            pillar = matches[0]
            continue

    send_message(chat_id, f"🔍 Running radar... (pillar: {pillar}, last {since}h)", msg_id)

    # Select queries
    if pillar == "all":
        pillars = radar.SEARCH_QUERIES
    else:
        pillars = {pillar: radar.SEARCH_QUERIES[pillar]}

    # Run searches
    all_tweets = []
    for p_name, queries in pillars.items():
        for q in queries:
            tweets = radar.composio_search(q, max_results=50, since_hours=since)
            all_tweets.extend(tweets)
            time.sleep(0.6)

    unique = radar.dedupe(all_tweets)
    ranked = radar.score_and_rank(unique, min_followers=min_followers, min_likes=min_likes, max_age_hours=max_age)
    output = radar.format_results(ranked, top_n=top_n)

    send_message(chat_id, output, msg_id)
    log(f"Radar done: {len(all_tweets)} raw → {len(unique)} unique → {len(ranked)} ranked")


def handle_search(query: str, chat_id: str, msg_id: int):
    """Handle /search <query> — custom one-off search."""
    if not query.strip():
        send_message(chat_id, "Usage: /search <query>\nExample: /search claude code MCP", msg_id)
        return

    # Add lang:en if not already specified
    q = query.strip()
    if "lang:" not in q:
        q += " lang:en"
    if "-is:retweet" not in q:
        q += " -is:retweet"

    send_message(chat_id, f"🔍 Searching: {q}", msg_id)

    tweets = radar.composio_search(q, max_results=50, since_hours=6)
    unique = radar.dedupe(tweets)
    ranked = radar.score_and_rank(unique, min_followers=1000, min_likes=3, max_age_hours=6)

    if ranked:
        output = radar.format_results(ranked, top_n=10)
    elif unique:
        # Show unfiltered if nothing passes filters
        output = f"Found {len(unique)} tweets but none pass engagement filters. Top raw results:\n\n"
        for i, t in enumerate(sorted(unique, key=lambda x: x["likes"], reverse=True)[:5], 1):
            preview = t["text"][:100].replace("\n", " ")
            output += f"{i}. @{t['username']} ({t['followers']:,}) — {preview}...\n   ❤️ {t['likes']} | ⏱️ {t['age_hours']}h ago\n   {t['url']}\n\n"
    else:
        output = "No results found for that query."

    send_message(chat_id, output, msg_id)


def handle_pillars(chat_id: str, msg_id: int):
    """Handle /pillars — list available pillars."""
    lines = ["📋 Available pillars:\n"]
    for name, queries in radar.SEARCH_QUERIES.items():
        lines.append(f"• {name} ({len(queries)} queries)")
        for q in queries:
            lines.append(f"  → {q[:60]}...")
    lines.append(f"\nUsage: /radar <pillar_name>")
    send_message(chat_id, "\n".join(lines), msg_id)


def handle_help(chat_id: str, msg_id: int):
    """Handle /help — show commands."""
    text = """🎯 Reply Radar Bot Commands:

/radar — Full scan (all pillars, last 3h)
/radar ai_tools — Scan specific pillar
/radar 6h — Custom time window
/radar ai_tools 6h — Pillar + time
/radar hot_takes 12h 20 — Pillar + time + top N

/search <query> — Custom X search
/search "vibe coding" shipped
/search from:levelsio

/pillars — List all pillars & queries
/help — This message"""
    send_message(chat_id, text, msg_id)


def process_message(message: dict):
    """Process an incoming Telegram message."""
    chat_id = str(message.get("chat", {}).get("id", ""))
    msg_id = message.get("message_id")
    text = message.get("text", "").strip()

    if not text or not text.startswith("/"):
        return

    # Only respond to Ben's chat
    if chat_id != CHAT_ID:
        log(f"Ignoring message from chat {chat_id}")
        return

    log(f"Command: {text}")

    # Parse command
    if text.startswith("/radar"):
        args = text[6:].strip()
        handle_radar(args, chat_id, msg_id)
    elif text.startswith("/search"):
        query = text[7:].strip()
        handle_search(query, chat_id, msg_id)
    elif text.startswith("/pillars"):
        handle_pillars(chat_id, msg_id)
    elif text.startswith("/help"):
        handle_help(chat_id, msg_id)


def main():
    log("🎯 Reply Radar Bot starting...")
    send_message(CHAT_ID, "🎯 Reply Radar Bot is online!\n\nType /help for commands.")

    offset = None

    while True:
        updates = get_updates(offset)

        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message")
            if message:
                try:
                    process_message(message)
                except Exception as e:
                    log(f"Error processing message: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
