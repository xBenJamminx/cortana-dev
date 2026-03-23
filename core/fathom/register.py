#!/usr/bin/env python3
"""
Register Fathom webhook via API
"""
import os
import sys
import json
import requests

def _load_env():
    p = os.path.expanduser('~/.openclaw/.env')
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k, v)

_load_env()

API_KEY = os.environ.get('FATHOM_API_KEY', '')
BASE_URL = 'https://api.fathom.ai/external/v1'
HEADERS = {
    'X-Api-Key': API_KEY,
    'Content-Type': 'application/json'
}

def list_webhooks():
    """List existing webhooks"""
    r = requests.get(f'{BASE_URL}/webhooks', headers=HEADERS, timeout=30)
    if not r.ok:
        print(f"Error: {r.status_code} - {r.text}")
        return []
    return r.json().get('webhooks', [])

def create_webhook(destination_url: str, triggered_for: list = None):
    """Create a new webhook"""
    if triggered_for is None:
        triggered_for = ['my_recordings']
    payload = {
        'destination_url': destination_url,
        'triggered_for': triggered_for,
        'include_transcript': True,
        'include_summary': True,
        'include_action_items': True,
        'include_crm_matches': False
    }
    
    r = requests.post(f'{BASE_URL}/webhooks', headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        print(f"Error creating webhook: {r.status_code} - {r.text}")
        return None
    
    return r.json()

def delete_webhook(webhook_id: str):
    """Delete a webhook"""
    r = requests.delete(f'{BASE_URL}/webhooks/{webhook_id}', headers=HEADERS, timeout=30)
    if not r.ok:
        print(f"Error deleting webhook: {r.status_code} - {r.text}")
        return False
    return True

def main():
    if not API_KEY:
        print("ERROR: FATHOM_API_KEY not set in .env")
        sys.exit(1)
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    
    if cmd == 'list':
        webhooks = list_webhooks()
        print(f"Found {len(webhooks)} webhook(s):")
        for wh in webhooks:
            print(f"  {wh.get('id')} -> {wh.get('destination_url')}")
            print(f"    Triggered for: {wh.get('triggered_for')}")
            print(f"    Include: transcript={wh.get('include_transcript')}, summary={wh.get('include_summary')}, actions={wh.get('include_action_items')}")
    
    elif cmd == 'create':
        if len(sys.argv) < 3:
            print("Usage: fathom_register.py create <destination_url> [triggered_for]")
            print("  triggered_for: me (default), shared_with_me, both")
            sys.exit(1)
        
        url = sys.argv[2]
        triggered = sys.argv[3] if len(sys.argv) > 3 else 'me'
        
        result = create_webhook(url, triggered)
        if result:
            print("Webhook created successfully!")
            print(json.dumps(result, indent=2))
        else:
            sys.exit(1)
    
    elif cmd == 'delete':
        if len(sys.argv) < 3:
            print("Usage: fathom_register.py delete <webhook_id>")
            sys.exit(1)
        
        webhook_id = sys.argv[2]
        if delete_webhook(webhook_id):
            print(f"Webhook {webhook_id} deleted")
        else:
            sys.exit(1)
    
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: fathom_register.py [list|create|delete]")
        sys.exit(1)

if __name__ == '__main__':
    main()
