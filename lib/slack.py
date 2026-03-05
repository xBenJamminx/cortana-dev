#!/usr/bin/env python3
"""Read Slack channels using the bot token from .env"""
import os, sys, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / ".openclaw" / ".env")
TOKEN = os.getenv("SLACK_BOT_TOKEN")
if not TOKEN:
    print("ERROR: SLACK_BOT_TOKEN not found in ~/.openclaw/.env")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
API = "https://slack.com/api"

CHANNELS = {
    "meeting-notes": "C09J78SH2FM",
    "poc": "C08K8GH4ZGU",
}

def read_channel(channel_name, limit=5):
    cid = CHANNELS.get(channel_name)
    if not cid:
        print(f"Unknown channel: {channel_name}. Known: {', '.join(CHANNELS.keys())}")
        sys.exit(1)
    r = requests.post(f"{API}/conversations.history", headers=HEADERS, json={"channel": cid, "limit": limit})
    data = r.json()
    if not data.get("ok"):
        print(f"ERROR: {data.get('error', 'unknown')}")
        sys.exit(1)
    for msg in reversed(data.get("messages", [])):
        user = msg.get("user", "bot")
        text = msg.get("text", "")
        print(f"[{user}] {text[:2000]}")
        print("---")

def list_channels():
    r = requests.post(f"{API}/conversations.list", headers=HEADERS, json={"limit": 100, "types": "public_channel,private_channel"})
    data = r.json()
    if not data.get("ok"):
        print(f"ERROR: {data.get('error')}")
        sys.exit(1)
    for ch in data.get("channels", []):
        print(f"  #{ch['name']}  {ch['id']}  {'(member)' if ch.get('is_member') else ''}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 slack.py <channel> [limit]")
        print("       python3 slack.py --list")
        sys.exit(1)
    if sys.argv[1] == "--list":
        list_channels()
    else:
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        read_channel(sys.argv[1], limit)
