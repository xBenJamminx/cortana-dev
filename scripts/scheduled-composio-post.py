#!/usr/bin/env python3
"""Scheduled reminder: X API for Free via Composio
Scheduled for: Monday Feb 10, 2026 at 10:00 AM ET (15:00 UTC)
Status: APPROVED
Method: Telegram reminder (Ben posts manually)
"""
import os
import requests
import datetime

def _load_env():
    env_path = os.path.expanduser("~/.openclaw/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key = key.replace("export ", "").strip()
                    if key and not os.environ.get(key):
                        os.environ[key] = val
_load_env()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
LOG = "/root/clawd/logs/scheduled-posts.log"

draft = """The X API just went pay-per-use. Here's how to use it for $0.

@frankdegods shared an incredible tool yesterday that lets you search tweets, follow threads, and monitor accounts from the command line.

One problem: it connects directly to the X API. And X just killed their fixed plans. Everything is pay-per-use now. $0.005 per tweet read. 20,000 reads = $100.

So I forked it and connected it through Composio instead.

Composio is a platform that connects apps together. Their free tier gives you 20,000 calls/month. One of those connections? Twitter. Same search. Same data. $0.

They make money on paid tiers. The free tier is their developer funnel, same model as Vercel or Supabase. They bet you'll outgrow 20K calls and upgrade. Until then, it's free.

Same tool. Zero cost.

What you can do with it:
- Search any tweets from the last 7 days
- See likes, impressions, and bookmarks on any post
- Find every reply to your posts sorted by engagement
- Look up any account's recent activity
- Track specific accounts you care about
- Results get cached so you're not wasting calls

The math: 20K reads through X = $100. 20K calls through Composio = $0.

Here's the forked repo. Use it, build on it.

https://github.com/rohunvora/x-research-skill

Thanks @frankdegods for the original. This just makes it free."""

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": text,
    }, timeout=15)
    return resp.status_code == 200

reminder = f"""Hey Ben, it's posting time.

Here's your Composio X API article draft. Format it however you want and post when ready.

TODO: Replace https://github.com/rohunvora/x-research-skill with the GitHub repo URL before posting.

---

{draft}"""

log("Sending Composio article reminder to Telegram...")

if send_telegram(reminder):
    log("Composio article reminder sent successfully")
    print("Reminder sent")
else:
    log("Composio article reminder FAILED")
    print("Failed to send reminder")
