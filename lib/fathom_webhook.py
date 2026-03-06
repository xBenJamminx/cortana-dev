#!/usr/bin/env python3
"""
Fathom webhook receiver - handles incoming meeting transcripts
Stores transcripts to memory/ directory for Cortana to process
"""
import os
import sys
import json
import hmac
import hashlib
import base64
import time
from datetime import datetime
from pathlib import Path

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

WEBHOOK_SECRET = os.environ.get('FATHOM_WEBHOOK_SECRET', '')
MEMORY_DIR = Path(os.path.expanduser('~/.openclaw/workspace/memory'))

def verify_webhook(headers: dict, raw_body: str) -> bool:
    """Verify webhook signature from Fathom"""
    if not WEBHOOK_SECRET:
        print("WARNING: No webhook secret configured, skipping verification")
        return True
    
    webhook_id = headers.get('webhook-id')
    webhook_timestamp = headers.get('webhook-timestamp')
    webhook_signature = headers.get('webhook-signature')
    
    if not all([webhook_id, webhook_timestamp, webhook_signature]):
        print("Missing webhook headers")
        return False
    
    # Verify timestamp (within 5 minutes)
    try:
        timestamp = int(webhook_timestamp)
        current_timestamp = int(time.time())
        if abs(current_timestamp - timestamp) > 300:
            print(f"Timestamp too old: {timestamp} vs {current_timestamp}")
            return False
    except ValueError:
        print("Invalid timestamp")
        return False
    
    # Construct signed content
    signed_content = f"{webhook_id}.{webhook_timestamp}.{raw_body}"
    
    # Base64 decode the secret (part after whsec_)
    try:
        secret_bytes = base64.b64decode(WEBHOOK_SECRET.split('_')[1])
    except (IndexError, base64.binascii.Error) as e:
        print(f"Invalid webhook secret format: {e}")
        return False
    
    # Calculate expected signature
    expected_signature = base64.b64encode(
        hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    ).decode()
    
    # Extract signatures from header (remove version prefixes like v1,)
    signatures = []
    for sig in webhook_signature.split(' '):
        parts = sig.split(',')
        signatures.append(parts[1] if len(parts) > 1 else parts[0])
    
    # Constant-time comparison
    return any(hmac.compare_digest(expected_signature, sig) for sig in signatures)

def store_transcript(payload: dict) -> Path:
    """Store transcript to memory directory"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Extract meeting info
    recording_id = payload.get('recording', {}).get('id', 'unknown')
    meeting_name = payload.get('recording', {}).get('name', 'Untitled Meeting')
    meeting_date = payload.get('recording', {}).get('created_at', '')
    
    # Parse date for filename
    try:
        if meeting_date:
            dt = datetime.fromisoformat(meeting_date.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d')
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
    except:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Clean meeting name for filename
    clean_name = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in meeting_name).replace(' ', '_')[:50]
    
    filename = f"{date_str}_fathom_{clean_name}_{recording_id[:8]}.json"
    filepath = MEMORY_DIR / filename
    
    # Add metadata
    enriched = {
        'source': 'fathom',
        'received_at': datetime.now().isoformat(),
        'processed': False,
        'payload': payload
    }
    
    with open(filepath, 'w') as f:
        json.dump(enriched, f, indent=2)
    
    return filepath

def handle_webhook(raw_body: str, headers: dict) -> dict:
    """Main webhook handler"""
    if not verify_webhook(headers, raw_body):
        return {'status': 'error', 'message': 'Invalid webhook signature'}
    
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as e:
        return {'status': 'error', 'message': f'Invalid JSON: {e}'}
    
    # Check if this is a content-ready webhook
    event_type = payload.get('event_type', '')
    if event_type != 'new_meeting_content_ready':
        return {'status': 'ignored', 'message': f'Event type {event_type} not processed'}
    
    # Store the transcript
    filepath = store_transcript(payload)
    
    # Extract key info for summary
    recording = payload.get('recording', {})
    transcript = recording.get('transcript', '')
    summary = recording.get('summary', '')
    action_items = recording.get('action_items', [])
    
    print(f"✅ Stored transcript: {filepath}")
    print(f"   Meeting: {recording.get('name', 'Untitled')}")
    print(f"   Duration: {recording.get('duration', 'unknown')}s")
    print(f"   Transcript length: {len(transcript)} chars")
    print(f"   Action items: {len(action_items)}")
    
    return {
        'status': 'success',
        'file': str(filepath),
        'meeting_name': recording.get('name'),
        'transcript_length': len(transcript),
        'action_items_count': len(action_items)
    }

def main():
    """CLI test mode - process a JSON file"""
    if len(sys.argv) < 2:
        print("Usage: fathom_webhook.py <webhook_payload.json>")
        print("Or import handle_webhook() for server use")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        raw_body = f.read()
    
    # Mock headers for testing (no verification in test mode)
    headers = {}
    result = handle_webhook(raw_body, headers)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
