#!/usr/bin/env python3
"""
Discord CTA Cleanup Script
Removes "Want the full pack/guide/template? Ask in #general" lines
from bot messages in the EverydayAI Discord server.
"""

import os
import re
import time
import requests

# Load env
def load_env(path="/root/.openclaw/.env"):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                # Strip export prefix
                if line.startswith("export "):
                    line = line[7:]
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    return env

env = load_env()
BOT_TOKEN = env["DISCORD_BOT_TOKEN"]
GUILD_ID = env["DISCORD_GUILD_ID"]

BASE = "https://discord.com/api/v10"
HEADERS = {
    "Authorization": f"Bot {BOT_TOKEN}",
    "Content-Type": "application/json",
}

# Pattern to match the CTA lines (with or without bold markers)
# Matches the entire line containing "Want the full pack/guide/template?"
CTA_PATTERN = re.compile(
    r'\n*\**Want the full (pack|guide|template)\??\**[^\n]*',
    re.IGNORECASE
)

def get_bot_user_id():
    """Get the bot's own user ID so we only edit our own messages."""
    resp = requests.get(f"{BASE}/users/@me", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["id"]

def get_channels():
    """Get all channels in the guild."""
    resp = requests.get(f"{BASE}/guilds/{GUILD_ID}/channels", headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_messages(channel_id, limit=50):
    """Fetch recent messages from a channel."""
    resp = requests.get(
        f"{BASE}/channels/{channel_id}/messages",
        headers=HEADERS,
        params={"limit": limit}
    )
    if resp.status_code == 403:
        return []  # No access to this channel
    resp.raise_for_status()
    return resp.json()

def edit_message(channel_id, message_id, new_content):
    """Edit a message's content."""
    resp = requests.patch(
        f"{BASE}/channels/{channel_id}/messages/{message_id}",
        headers=HEADERS,
        json={"content": new_content}
    )
    resp.raise_for_status()
    return resp.json()

def clean_content(content):
    """Remove CTA lines and clean up extra blank lines."""
    cleaned = CTA_PATTERN.sub("", content)
    # Collapse triple+ newlines into double
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    # Strip trailing whitespace
    cleaned = cleaned.rstrip()
    return cleaned

def main():
    print("=" * 60)
    print("Discord CTA Cleanup Script")
    print("=" * 60)

    # Get bot user ID
    bot_id = get_bot_user_id()
    print(f"Bot user ID: {bot_id}")
    time.sleep(1)

    # Get all channels
    channels = get_channels()
    time.sleep(1)

    # Filter to text channels (type 0) and announcement channels (type 5)
    # Also include threads (type 11, 12) and forum posts (type 15)
    text_channels = [
        ch for ch in channels
        if ch.get("type") in (0, 5, 11, 12, 15)
    ]

    print(f"\nFound {len(text_channels)} text/announcement channels:")
    for ch in text_channels:
        print(f"  #{ch['name']} (ID: {ch['id']}, type: {ch['type']})")

    total_edited = 0
    total_checked = 0

    for ch in text_channels:
        ch_name = ch["name"]
        ch_id = ch["id"]

        print(f"\n--- Scanning #{ch_name} ---")
        time.sleep(1.5)

        messages = get_messages(ch_id)
        if not messages:
            print(f"  No messages or no access")
            continue

        print(f"  Fetched {len(messages)} messages")

        for msg in messages:
            total_checked += 1
            # Only edit bot's own messages
            if msg["author"]["id"] != bot_id:
                continue

            content = msg.get("content", "")
            if not content:
                continue

            # Check if message contains CTA text
            if not CTA_PATTERN.search(content):
                continue

            # Found a match - clean it
            new_content = clean_content(content)

            if new_content == content:
                continue  # No actual change

            # Show what we're doing
            match = CTA_PATTERN.search(content)
            removed_text = match.group(0).strip()
            print(f"\n  Message ID {msg['id']} in #{ch_name}:")
            print(f"    REMOVING: {removed_text}")

            # Edit the message
            try:
                edit_message(ch_id, msg["id"], new_content)
                total_edited += 1
                print(f"    DONE - edited successfully")
            except Exception as e:
                print(f"    ERROR editing: {e}")

            time.sleep(3)  # Rate limit respect (bumped from 1.5 after 429s)

    print(f"\n{'=' * 60}")
    print(f"COMPLETE!")
    print(f"  Messages checked: {total_checked}")
    print(f"  Messages edited:  {total_edited}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
