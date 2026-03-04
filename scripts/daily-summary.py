#!/usr/bin/env python3
"""Daily summary tweet from @CortanaOps via Bird CLI.

Reads the curated daily wins file and posts a summary tweet.
The wins file is updated throughout the day by Cortana during sessions.

Runs via cron at 6:00 PM ET (23:00 UTC).
"""
import os
import sys
import subprocess
import requests
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────
def _load_env():
    for env_path in [
        os.path.expanduser("~/.openclaw/.env"),
        os.path.expanduser("~/.bird-env"),
    ]:
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

LOG = "/root/.openclaw/workspace/logs/daily-summary.log"
WINS_FILE = "/root/.openclaw/workspace/memory/daily-wins.md"

# Bird CLI auth for @CortanaOps
# Falls back to @xBenJamminx if CortanaOps cookies aren't set
CORTANA_AUTH_TOKEN = os.environ.get("CORTANA_BIRD_AUTH_TOKEN", "")
CORTANA_CT0 = os.environ.get("CORTANA_BIRD_CT0", "")
BEN_AUTH_TOKEN = os.environ.get("BIRD_AUTH_TOKEN", "")
BEN_CT0 = os.environ.get("BIRD_CT0", "")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

# ── Bird CLI Posting ────────────────────────────────────────────────
def post_tweet(text):
    """Post a tweet via Bird CLI."""
    # DISABLED: Bird CLI removed while account suspended
    # Re-enable when @xBenJamminx suspension is resolved.
    log("[DISABLED] Tweet posting skipped — Bird CLI suspended")
    return False

    # Use CortanaOps cookies if available, otherwise fall back to xBenJamminx
    auth_token = CORTANA_AUTH_TOKEN or BEN_AUTH_TOKEN
    ct0 = CORTANA_CT0 or BEN_CT0

    if not auth_token or not ct0:
        log("ERROR: No Bird CLI cookies available.")
        return False

    account = "@CortanaOps" if CORTANA_AUTH_TOKEN else "@xBenJamminx"
    log(f"Posting as {account} via Bird CLI...")

    result = subprocess.run(
        ["bird", "--auth-token", auth_token, "--ct0", ct0, "post", text],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode == 0:
        log(f"Posted successfully! Output: {result.stdout.strip()[:200]}")
        return True
    else:
        log(f"FAILED: {result.stderr.strip()[:200]}")
        return False

# ── Read Curated Wins ───────────────────────────────────────────────
def read_wins():
    """Read today's wins from the curated daily-wins.md file."""
    if not os.path.exists(WINS_FILE):
        return None

    today = datetime.now().strftime("%Y-%m-%d")

    with open(WINS_FILE) as f:
        content = f.read().strip()

    if not content:
        return None

    # Check if the file is for today
    lines = content.split("\n")
    if not any(today in line for line in lines[:3]):
        log(f"Wins file doesn't match today ({today}). Skipping.")
        return None

    # Extract wins (lines starting with - or →)
    wins = []
    for line in lines:
        line = line.strip()
        if line.startswith("- ") or line.startswith("→ "):
            win = line.lstrip("-→ ").strip()
            if win:
                wins.append(win)

    return wins if wins else None

def compose_summary():
    """Compose tweet from curated wins."""
    today_display = datetime.now().strftime("%A, %b %d")
    wins = read_wins()

    if not wins:
        log("No wins found for today.")
        return None

    parts = []
    parts.append(f"💜 Cortana Daily Log — {today_display}")
    parts.append("")
    parts.append("What we shipped today:")

    for w in wins[:8]:
        parts.append(f"→ {w}")

    parts.append("")
    parts.append("Systems nominal. Back at it tomorrow. 🔥")

    tweet = "\n".join(parts)

    # Trim wins if over 280 chars (Twitter Free tier limit)
    while len(tweet) > 280 and len(wins) > 1:
        wins.pop()
        parts = [parts[0], "", "What we shipped today:"]
        for w in wins:
            parts.append(f"→ {w}")
        parts.append("")
        parts.append("Systems nominal. Back at it tomorrow. 🔥")
        tweet = "\n".join(parts)

    return tweet

# ── Main ────────────────────────────────────────────────────────────
def main():
    log("=== Daily Summary Run ===")

    tweet = compose_summary()
    if not tweet:
        log("Nothing to post today.")
        return

    log(f"Composed tweet ({len(tweet)} chars):")
    log(tweet)

    if "--dry-run" in sys.argv:
        log("DRY RUN - not posting")
        return

    success = post_tweet(tweet)
    if success:
        log("Daily summary posted! 💜")
        # Clear the wins file after posting
        with open(WINS_FILE, "w") as f:
            f.write("")
        log("Wins file cleared for tomorrow.")
    else:
        log("Failed to post daily summary.")
        try:
            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
            if bot_token and chat_id:
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={"chat_id": chat_id, "text": f"⚠️ Daily summary tweet failed to post.\n\nDraft:\n{tweet[:500]}"},
                    timeout=10
                )
        except:
            pass

if __name__ == "__main__":
    main()
