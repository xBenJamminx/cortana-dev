#!/usr/bin/env python3
"""Scheduled reminder: Deploy a Web App with OpenClaw
Scheduled for: Wednesday Feb 12, 2026 at 10:00 AM ET (15:00 UTC)
Status: APPROVED (moved from Monday to Wednesday)
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

draft = """Your @OpenClaw bot can build, push, and deploy a web app for you.

I needed a landing page for a community I'm launching. Told @CortanaOps to build it in SvelteKit with Tailwind CSS, using the Neo-brutalist style. She wrote the whole thing, pushed it to GitHub, deployed it to Vercel, and handed me a live URL while I was making coffee.

I had her build a landing page, but you can build any kind of web app/site.

Here's how it's done:

Connect your bot to GitHub and Vercel through Composio MCP (or manually add auth tokens).

Then steal this prompt:

"Build me a landing page for [describe your project] using [SvelteKit / Vite + Tailwind / Next.js]. Use a [neo-brutalist / glassmorphism / retro terminal] design. Include a hero section, features grid, FAQ accordion, and a CTA button. When it's done, create a GitHub repo, push the code, and deploy it to Vercel. Give me the live URL."

You can personalize the prompt as much as you want, change it around as you see fit.

Paste it in and your bot handles the rest."""

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

Here's your Deploy Web App post draft. Format it however you want and post when ready.

---

{draft}"""

log("Sending deploy post reminder to Telegram...")

if send_telegram(reminder):
    log("Deploy post reminder sent successfully")
    print("Reminder sent")
else:
    log("Deploy post reminder FAILED")
    print("Failed to send reminder")
