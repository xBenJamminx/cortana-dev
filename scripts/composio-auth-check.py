#!/usr/bin/env python3
"""Check Composio Twitter connection status and send re-auth link if expired.

Usage:
    composio-auth-check.py                  # Check and alert if expired
    composio-auth-check.py --entity NAME    # Check specific entity
    composio-auth-check.py --refresh        # Force refresh attempt
    composio-auth-check.py --quiet          # Only output if action needed

Can be imported as a module:
    from composio_auth_check import ensure_composio_auth
    conn_id = ensure_composio_auth("cortanaops")  # Returns conn_id or None
"""
import os
import sys
import json
import requests
from datetime import datetime

def _load_env():
    for env_path in [
        os.path.expanduser("~/.openclaw/.env"),
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

API_KEY = os.environ.get("COMPOSIO_API_KEY") or os.environ.get("COMPOSIO_MCP_API_KEY", "")
BASE = "https://backend.composio.dev/api"
INTEGRATION_ID = "d1a6672e-99f6-4e96-825a-6863504f5f8c"

def get_twitter_connections():
    """Get all Twitter connections."""
    resp = requests.get(
        f"{BASE}/v3/connected_accounts",
        headers={"x-api-key": API_KEY},
        params={"appName": "twitter", "limit": 50},
        timeout=15
    )
    if resp.status_code == 200:
        return resp.json().get("items", [])
    return []

def find_connection(entity_id="cortanaops"):
    """Find the most recent active or expired connection for an entity."""
    connections = get_twitter_connections()
    # Filter by entity, prefer ACTIVE, then most recent EXPIRED
    matches = [c for c in connections if c.get("user_id") == entity_id]
    active = [c for c in matches if c.get("status") == "ACTIVE"]
    if active:
        return active[0]
    expired = sorted(matches, key=lambda c: c.get("updated_at", ""), reverse=True)
    return expired[0] if expired else None

def check_connection(entity_id="cortanaops"):
    """Check if a connection is active. Returns (is_active, conn_uuid, v3_id)."""
    conn = find_connection(entity_id)
    if not conn:
        return False, None, None

    uuid = conn.get("uuid", "")
    v3_id = conn.get("id", "")
    status = conn.get("status", "")

    if status == "ACTIVE":
        # Verify it actually works
        resp = requests.post(
            f"{BASE}/v2/actions/TWITTER_USER_LOOKUP_ME/execute",
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            json={"connectedAccountId": uuid, "input": {}},
            timeout=15
        )
        data = resp.json()
        if data.get("successful"):
            return True, uuid, v3_id

    return False, uuid, v3_id

def generate_auth_link(entity_id="cortanaops"):
    """Generate a fresh OAuth auth link."""
    resp = requests.post(
        f"{BASE}/v1/connectedAccounts",
        headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
        json={
            "integrationId": INTEGRATION_ID,
            "entityId": entity_id,
            "redirectUri": "https://www.google.com",
            "data": {}
        },
        timeout=15
    )
    if resp.status_code == 200:
        data = resp.json()
        return data.get("redirectUrl"), data.get("connectedAccountId")
    return None, None

def send_telegram(message):
    """Send a message via Telegram."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        return False
    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10
        )
        return True
    except:
        return False

def ensure_composio_auth(entity_id="cortanaops", silent=False):
    """Check auth and send re-auth link if expired.
    Returns connection UUID if active, None if expired (link sent)."""
    is_active, uuid, v3_id = check_connection(entity_id)

    if is_active:
        if not silent:
            print(f"✅ @{entity_id} Twitter connection is active (uuid={uuid[:12]}...)")
        return uuid

    # Connection expired — generate new auth link
    auth_url, new_conn_id = generate_auth_link(entity_id)
    if auth_url:
        msg = f"🔑 Twitter auth expired for *{entity_id}*\n\nRe-auth here:\n{auth_url}"
        if not silent:
            print(f"⚠️ @{entity_id} Twitter connection expired.")
            print(f"Re-auth link: {auth_url}")
            print(f"New connection ID: {new_conn_id}")
        send_telegram(msg)
        return None
    else:
        if not silent:
            print(f"❌ Failed to generate auth link for {entity_id}")
        return None

def main():
    entities = ["cortanaops"]
    quiet = "--quiet" in sys.argv

    if "--entity" in sys.argv:
        idx = sys.argv.index("--entity")
        if idx + 1 < len(sys.argv):
            entities = [sys.argv[idx + 1]]

    for entity in entities:
        result = ensure_composio_auth(entity, silent=quiet)
        if result and quiet:
            pass  # Active, no output needed
        elif not result and quiet:
            print(f"EXPIRED:{entity}")

if __name__ == "__main__":
    main()
