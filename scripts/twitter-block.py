#!/usr/bin/env python3
"""
Twitter Block Script
Uses auth cookies to block accounts via Twitter's internal API
"""

import os
import sys
import time
import requests
from pathlib import Path

# Auth from environment
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
CT0 = os.environ.get("CT0")

if not AUTH_TOKEN or not CT0:
    print("ERROR: AUTH_TOKEN and CT0 must be set in environment")
    sys.exit(1)

# Bearer token from Twitter web app
BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

HEADERS = {
    "authorization": f"Bearer {BEARER}",
    "cookie": f"auth_token={AUTH_TOKEN}; ct0={CT0}",
    "x-csrf-token": CT0,
    "x-twitter-auth-type": "OAuth2Session",
    "x-twitter-active-user": "yes",
    "content-type": "application/x-www-form-urlencoded",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


def block_user(username: str) -> tuple[bool, str]:
    """Block a user by their screen name"""
    url = "https://twitter.com/i/api/1.1/blocks/create.json"
    data = f"screen_name={username}"

    try:
        resp = requests.post(url, headers=HEADERS, data=data, timeout=15)
        if resp.status_code == 200:
            return True, "OK"
        elif resp.status_code == 403:
            return False, "403-forbidden"
        elif resp.status_code == 429:
            return False, "429-rate-limited"
        elif resp.status_code == 404:
            return False, "404-not-found"
        else:
            return False, f"{resp.status_code}"
    except Exception as e:
        return False, str(e)


def main():
    if len(sys.argv) < 2:
        print("Usage: twitter-block.py <file_with_usernames> [--dry-run]")
        print("       twitter-block.py <single_username>")
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    target = sys.argv[1]

    # Check if it's a file or a single username
    if Path(target).exists():
        with open(target) as f:
            content = f.read()
        # Handle space-separated or newline-separated
        usernames = content.replace('\n', ' ').split()
    else:
        usernames = [target]

    print(f"Found {len(usernames)} accounts to block")
    if dry_run:
        print("DRY RUN - no actual blocking")

    blocked = 0
    failed = 0

    for i, username in enumerate(usernames):
        username = username.strip().lstrip('@')
        if not username:
            continue

        print(f"[{i+1}/{len(usernames)}] @{username}...", end=" ", flush=True)

        if dry_run:
            print("WOULD BLOCK")
            blocked += 1
            continue

        # Block the user
        success, msg = block_user(username)
        if success:
            print("BLOCKED")
            blocked += 1
        else:
            print(f"FAILED ({msg})")
            failed += 1
            if "429" in msg:
                print("Rate limited! Waiting 60s...")
                time.sleep(60)

        # Rate limit protection
        time.sleep(1.2)

    print(f"\nDone! Blocked: {blocked}, Failed: {failed}")


if __name__ == "__main__":
    main()
