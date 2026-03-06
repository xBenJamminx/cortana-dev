#!/usr/bin/env python3
"""
Simple webhook receiver for Fathom
Receives transcripts and stores them to memory/
Run: python3 fathom_server.py
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
from http.server import HTTPServer, BaseHTTPRequestHandler

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
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

class FathomHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{datetime.now().isoformat()}] {format % args}")
    
    def do_POST(self):
        if self.path != '/fathom/webhook':
            self.send_error(404)
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8')
        
        # Verify webhook
        if not self.verify_webhook(self.headers, raw_body):
            print("Webhook verification failed")
            self.send_error(401)
            return
        
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_error(400)
            return
        
        # Store the transcript
        result = self.store_transcript(payload)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
        
        print(f"✅ Stored: {result.get('file', 'unknown')}")
    
    def verify_webhook(self, headers, raw_body):
        if not WEBHOOK_SECRET:
            return True
        
        webhook_id = headers.get('webhook-id')
        webhook_timestamp = headers.get('webhook-timestamp')
        webhook_signature = headers.get('webhook-signature')
        
        if not all([webhook_id, webhook_timestamp, webhook_signature]):
            return False
        
        try:
            timestamp = int(webhook_timestamp)
            if abs(int(time.time()) - timestamp) > 300:
                return False
        except ValueError:
            return False
        
        signed_content = f"{webhook_id}.{webhook_timestamp}.{raw_body}"
        
        try:
            secret_bytes = base64.b64decode(WEBHOOK_SECRET.split('_')[1])
        except:
            return False
        
        expected_sig = base64.b64encode(
            hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
        ).decode()
        
        signatures = []
        for sig in webhook_signature.split(' '):
            parts = sig.split(',')
            signatures.append(parts[1] if len(parts) > 1 else parts[0])
        
        return any(hmac.compare_digest(expected_sig, sig) for sig in signatures)
    
    def store_transcript(self, payload):
        event_type = payload.get('event_type', '')
        if event_type != 'new_meeting_content_ready':
            return {'status': 'ignored', 'reason': f'event_type={event_type}'}
        
        recording = payload.get('recording', {})
        recording_id = recording.get('id', 'unknown')
        meeting_name = recording.get('name', 'Untitled Meeting')
        meeting_date = recording.get('created_at', '')
        
        try:
            if meeting_date:
                dt = datetime.fromisoformat(meeting_date.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d')
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
        except:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        clean_name = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in meeting_name).replace(' ', '_')[:50]
        filename = f"{date_str}_fathom_{clean_name}_{recording_id[:8]}.json"
        filepath = MEMORY_DIR / filename
        
        enriched = {
            'source': 'fathom',
            'received_at': datetime.now().isoformat(),
            'processed': False,
            'payload': payload
        }
        
        with open(filepath, 'w') as f:
            json.dump(enriched, f, indent=2)
        
        return {
            'status': 'success',
            'file': str(filepath),
            'meeting': meeting_name,
            'transcript_length': len(recording.get('transcript', ''))
        }

def main():
    port = int(os.environ.get('FATHOM_WEBHOOK_PORT', '8080'))
    server = HTTPServer(('0.0.0.0', port), FathomHandler)
    print(f"Fathom webhook receiver running on port {port}")
    print(f"Endpoint: http://0.0.0.0:{port}/fathom/webhook")
    print(f"Storing transcripts to: {MEMORY_DIR}")
    server.serve_forever()

if __name__ == '__main__':
    main()
