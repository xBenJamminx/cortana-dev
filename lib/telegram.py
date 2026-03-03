#!/usr/bin/env python3
"""
Quick Telegram send — one-liner for sending messages to Ben.

Usage:
    python3 /root/.openclaw/workspace/lib/telegram.py "Your message here"

    # Or import in scripts:
    from lib.telegram import send
    send("Email is live! cortana-ops@agentmail.to ✅")
"""

import json
import sys
import urllib.request
from pathlib import Path


def _load_env():
    env = {}
    try:
        with open("/root/.openclaw/.env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    if line.startswith("export "):
                        line = line[7:]
                    key, val = line.split("=", 1)
                    env[key.strip()] = val.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env


def send(text: str, topic: int = None) -> bool:
    """Send a message to the Telegram group. Returns True on success.

    Args:
        text: Message text to send.
        topic: Optional forum topic/thread ID. Overrides TELEGRAM_THREAD_ID env var.
    """
    env = _load_env()
    bot_token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")
    thread_id = env.get("TELEGRAM_THREAD_ID", "")  # optional, for forum topics

    if not bot_token or not chat_id:
        print("⚠️ Telegram creds not found")
        return False

    # Split long messages
    chunks = []
    while text:
        if len(text) <= 4000:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, 4000)
        if split_at < 2000:
            split_at = 4000
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    ok = True
    for chunk in chunks:
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }
        effective_thread = topic if topic is not None else (int(thread_id) if thread_id else None)
        if effective_thread:
            payload["message_thread_id"] = effective_thread
        payload = json.dumps(payload).encode()

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                if not result.get("ok"):
                    print(f"⚠️ Telegram error: {result}")
                    ok = False
        except Exception as e:
            print(f"⚠️ Telegram failed: {e}")
            ok = False

    return ok


def react(message_id: int, emoji: str = "\U0001f440", chat_id: str = None) -> bool:
    """React to a Telegram message with an emoji.

    Args:
        message_id: The message ID to react to.
        emoji: Emoji to react with (default: eyes).
        chat_id: Override chat ID (defaults to TELEGRAM_CHAT_ID from env).

    Returns:
        True on success, False on failure.
    """
    env = _load_env()
    bot_token = env.get("TELEGRAM_BOT_TOKEN", "")
    if chat_id is None:
        chat_id = env.get("TELEGRAM_CHAT_ID", "")

    if not bot_token or not chat_id:
        print("\u26a0\ufe0f Telegram creds not found")
        return False

    payload = json.dumps({
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
    }).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/setMessageReaction",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if not result.get("ok"):
                print(f"\u26a0\ufe0f Telegram reaction error: {result}")
                return False
            return True
    except Exception as e:
        print(f"\u26a0\ufe0f Telegram reaction failed: {e}")
        return False


def mark_read(message_id: int, chat_id: str = None) -> bool:
    """Convenience alias: react with a checkmark to indicate message was processed.

    Args:
        message_id: The message ID to mark as read.
        chat_id: Override chat ID (defaults to TELEGRAM_CHAT_ID from env).

    Returns:
        True on success, False on failure.
    """
    return react(message_id, emoji="\u2705", chat_id=chat_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Send a Telegram message or react to one")
    parser.add_argument("message", nargs="*", help="Message text (omit when using --react)")
    parser.add_argument("--topic", type=int, default=None, help="Forum topic/thread ID")
    parser.add_argument("--react", type=int, default=None, metavar="MSG_ID",
                        help="React to a message by ID instead of sending")
    parser.add_argument("--emoji", type=str, default="\U0001f440",
                        help="Emoji for reaction (default: eyes)")
    args = parser.parse_args()

    if args.react is not None:
        success = react(args.react, emoji=args.emoji)
    else:
        if not args.message:
            parser.error("message text is required when not using --react")
        msg = " ".join(args.message)
        success = send(msg, topic=args.topic)
    sys.exit(0 if success else 1)
