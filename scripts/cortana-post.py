#!/usr/bin/env python3
"""Post to @CortanaOps Twitter via Composio v2 API.

Usage:
  cortana-post.py "Tweet text here"
  cortana-post.py --file /path/to/tweet.txt
  cortana-post.py --test  # Check connection status
"""
import os
import sys
import json
import requests
from datetime import datetime

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

# CortanaOps Composio connection
CONNECTED_ACCOUNT_ID = "1fc9b642-233c-41c0-b754-3879b85ec0bb"
COMPOSIO_API_KEY = os.environ["COMPOSIO_MCP_API_KEY"]
BASE_URL = "https://backend.composio.dev/api"
LOG = "/root/clawd/logs/cortana-posts.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

def check_connection():
    """Check if CortanaOps Twitter connection is active."""
    resp = requests.get(
        f"{BASE_URL}/v1/connectedAccounts/{CONNECTED_ACCOUNT_ID}",
        headers={"x-api-key": COMPOSIO_API_KEY},
        timeout=15
    )
    if resp.status_code == 200:
        data = resp.json()
        status = data.get("status", "unknown")
        app = data.get("appUniqueId", "unknown")
        entity = data.get("clientUniqueUserId", "unknown")
        print(f"App: {app}")
        print(f"Entity: {entity}")
        print(f"Status: {status}")
        if status == "ACTIVE":
            # Verify identity
            me = execute_action("TWITTER_USER_LOOKUP_ME", {})
            if me and me.get("successful"):
                user = me.get("data", {}).get("data", {})
                print(f"Authenticated as: @{user.get('username')} ({user.get('name')})")
            return True
        else:
            print(f"Connection not active. Auth URL may be needed.")
            return False
    else:
        print(f"Failed to check connection: {resp.status_code}")
        return False

def execute_action(action_slug, params):
    """Execute a Composio action via v2 API with CortanaOps account."""
    resp = requests.post(
        f"{BASE_URL}/v2/actions/{action_slug}/execute",
        headers={
            "x-api-key": COMPOSIO_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "connectedAccountId": CONNECTED_ACCOUNT_ID,
            "input": params
        },
        timeout=30
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"successful": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

def post_tweet(text):
    """Post a tweet as @CortanaOps."""
    if len(text) > 280:
        # Twitter allows longer posts now but warn
        log(f"Note: Tweet is {len(text)} chars")

    log(f"Posting as @CortanaOps: {text[:80]}...")
    result = execute_action("TWITTER_CREATION_OF_A_POST", {"text": text})

    if result.get("successful"):
        tweet_data = result.get("data", {})
        log(f"Posted successfully. Data: {json.dumps(tweet_data)[:200]}")
        return True
    else:
        error = result.get("error", "Unknown error")
        log(f"FAILED to post: {error}")
        return False

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--test":
        check_connection()
    elif sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Usage: cortana-post.py --file /path/to/tweet.txt")
            sys.exit(1)
        with open(sys.argv[2]) as f:
            text = f.read().strip()
        post_tweet(text)
    else:
        text = " ".join(sys.argv[1:])
        post_tweet(text)

if __name__ == "__main__":
    main()
