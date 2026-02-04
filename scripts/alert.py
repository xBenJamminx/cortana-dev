#!/usr/bin/env python3
"""
Cortana Alert System - Send critical alerts via multiple channels
Usage: alert.py "Alert message" [--level critical|warning|info]
"""
import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path

# Config
BOT_TOKEN = "REDACTED_TELEGRAM_BOT_TOKEN"
CHAT_ID = "1455611839"
ALERT_LOG = Path("/root/clawd/logs/alerts.log")
ERROR_LOG = Path("/root/clawd/ERROR_LOG.md")

# Alert level emojis
LEVEL_EMOJI = {
    "critical": "🚨",
    "warning": "⚠️",
    "info": "ℹ️"
}

def log(msg: str):
    """Log to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERT_LOG, "a") as f:
        f.write(line + "\n")

def send_telegram(message: str, level: str = "warning") -> bool:
    """Send alert via Telegram"""
    try:
        emoji = LEVEL_EMOJI.get(level, "⚠️")
        formatted = f"{emoji} *Cortana Alert*\n\n{message}\n\n_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": formatted,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }, timeout=30)

        result = r.json()
        if result.get("ok"):
            log(f"Telegram alert sent: {message[:50]}...")
            return True
        else:
            log(f"Telegram failed: {result}")
            return False
    except Exception as e:
        log(f"Telegram error: {e}")
        return False

def append_error_log(message: str, level: str = "warning", details: str = None):
    """Append to ERROR_LOG.md for tracking"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"""
---

## {timestamp}: {level.upper()} Alert

**Message:** {message}

"""
        if details:
            entry += f"""**Details:**
```
{details}
```

"""
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOG, "a") as f:
            f.write(entry)
        log(f"Logged to ERROR_LOG.md")
    except Exception as e:
        log(f"Error logging to ERROR_LOG.md: {e}")

def send_alert(message: str, level: str = "warning", details: str = None, log_error: bool = True):
    """Main alert function - sends via all configured channels"""
    log(f"Alert [{level}]: {message}")

    # Always try Telegram
    telegram_ok = send_telegram(message, level)

    # Log critical/warning errors to ERROR_LOG.md
    if log_error and level in ["critical", "warning"]:
        append_error_log(message, level, details)

    return telegram_ok

def main():
    parser = argparse.ArgumentParser(description="Send Cortana alerts")
    parser.add_argument("message", help="Alert message to send")
    parser.add_argument("--level", "-l", choices=["critical", "warning", "info"],
                       default="warning", help="Alert severity level")
    parser.add_argument("--details", "-d", help="Additional details (for error log)")
    parser.add_argument("--no-log", action="store_true", help="Don't log to ERROR_LOG.md")

    args = parser.parse_args()

    success = send_alert(
        message=args.message,
        level=args.level,
        details=args.details,
        log_error=not args.no_log
    )

    sys.exit(0 if success else 1)

# Can also be imported and used as a module
if __name__ == "__main__":
    main()
