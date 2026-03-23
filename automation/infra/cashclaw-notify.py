#!/usr/bin/env python3
"""CashClaw → Telegram notification bridge.

Polls the CashClaw API for new inbox tasks and forwards them
to Ben via Telegram (Business topic #31).
"""

import json
import subprocess
import sys
import time
import urllib.request

CASHCLAW_API = "http://127.0.0.1:3777"
POLL_INTERVAL = 30  # seconds
SEEN_FILE = "/tmp/cashclaw-seen-tasks.json"
TG_SCRIPT = "/root/.openclaw/workspace/lib/telegram.py"
TG_TOPIC = "31"  # Business


def load_seen():
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def api_get(path):
    try:
        req = urllib.request.Request(f"{CASHCLAW_API}{path}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"API error ({path}): {e}", file=sys.stderr)
        return None


def send_tg(msg):
    try:
        subprocess.run(
            ["python3", TG_SCRIPT, "--topic", TG_TOPIC, msg],
            timeout=15,
            capture_output=True,
        )
    except Exception as e:
        print(f"TG send error: {e}", file=sys.stderr)


def check_inbox():
    seen = load_seen()
    data = api_get("/api/status")
    if not data or not data.get("running"):
        return

    # Use mltl inbox to get tasks
    try:
        result = subprocess.run(
            ["mltl", "inbox", "--agent", "31007", "--json"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return
        tasks = json.loads(result.stdout)
    except Exception:
        return

    if not isinstance(tasks, list):
        tasks = tasks.get("tasks", []) if isinstance(tasks, dict) else []

    for task in tasks:
        tid = task.get("id", "")
        status = task.get("status", "")
        if tid in seen:
            continue

        # New task - notify Ben
        task_desc = task.get("task", task.get("description", "No description"))
        client = task.get("client", "unknown")[:10]

        if status == "requested":
            msg = (
                f"💰 CashClaw — New Work Request\n\n"
                f"Task ID: {tid}\n"
                f"Client: {client}...\n"
                f"Task: {task_desc}\n\n"
                f"Reply 'quote {tid} 0.02' to quote, or 'decline {tid}' to pass."
            )
            send_tg(msg)
        elif status == "accepted":
            msg = (
                f"✅ CashClaw — Quote Accepted!\n\n"
                f"Task ID: {tid}\n"
                f"Task: {task_desc}\n\n"
                f"Funds locked in escrow. CashClaw is working on it."
            )
            send_tg(msg)
        elif status == "completed":
            msg = (
                f"🎉 CashClaw — Task Complete\n\n"
                f"Task ID: {tid}\n"
                f"Task: {task_desc}"
            )
            send_tg(msg)

        seen.add(tid)

    save_seen(seen)


def main():
    print("CashClaw notification bridge started")
    # Mark existing tasks as seen on first run
    while True:
        try:
            check_inbox()
        except Exception as e:
            print(f"Loop error: {e}", file=sys.stderr)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
