#!/usr/bin/env python3
"""Scheduled reminder: Memory System post
Scheduled for: Tuesday Feb 11, 2026 at 10:00 AM ET (15:00 UTC)
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

draft = """Your @OpenClaw bot has a memory system out of the box. It indexes a few files and calls it a day.

Mine indexes 76.

Here's what I changed with @CortanaOps:

System prompt (MEMORY.md): 58 lines. Just the essentials that load every session -- auth configs, active projects, writing rules, where to find everything else. Lean on purpose.

Topic files: Deep context split into separate files. My profile, content strategy, product roadmap, competitor research. They don't bloat every session. She pulls them when needed.

Searchable workspace: QMD indexes 76 files across the entire workspace. Research, reports, daily logs, drafts. She searches her own memory instead of guessing. Auto-reindexes every 6 hours.

Error log: 14 documented errors with cause, fix, and prevention. She's required to check it before attempting any fix. Tonight she crashed my gateway with a bad config change. It's already logged so she won't do it again.

Steal this prompt. Send it to your @OpenClaw bot or paste it into Claude Code:

"Upgrade your memory system. Keep MEMORY.md lean -- under 100 lines, just my preferences, active projects, and key configs. Create separate topic files for deeper context like my profile and project details. Create an ERROR_LOG.md to document every error with cause, fix, and prevention. Check it before debugging anything. Set up QMD to index your full workspace and add a cron job to reindex every 6 hours. Search your memory before making assumptions."

The difference between a chatbot and an operator is what it remembers."""

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

Here's your Memory System post draft. Format it however you want and post when ready.

---

{draft}"""

log("Sending memory system post reminder to Telegram...")

if send_telegram(reminder):
    log("Memory post reminder sent successfully")
    print("Reminder sent")
else:
    log("Memory post reminder FAILED")
    print("Failed to send reminder")
