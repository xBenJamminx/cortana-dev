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
    "testing": "C08MV404LVD",
    "action-agents": "C09LK4E6873",
    "alert-errors": "C0A7338719D",
    "updates": "C0AL8LLGULQ",
    "ai-skills": "C0AB5AGMWER",
    "alpha": "C0AKHJ5JDMG",
    "design": "C09JBLC6V3Q",
    "social": "C08K8GFSM8C",
    "mcp": "C08KXEFDFK6",
    "apis": "C08KFS565NV",
    "animocaminds": "C0AGSM6E1GT",
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
