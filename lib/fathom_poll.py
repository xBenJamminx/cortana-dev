#!/usr/bin/env python3
"""
Poll Fathom API for new meetings and store transcripts
Run via cron every 5 minutes
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone
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

API_KEY = os.environ.get('FATHOM_API_KEY', '')
MEMORY_DIR = Path(os.path.expanduser('~/.openclaw/workspace/memory'))
BASE_URL = 'https://api.fathom.ai/external/v1'
HEADERS = {'X-Api-Key': API_KEY, 'Content-Type': 'application/json'}

def get_meetings(since_hours=24):
    """Get meetings from the last N hours"""
    since = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    url = f'{BASE_URL}/meetings?created_after={since.isoformat()}&include_transcript=true&include_summary=true&include_action_items=true'
    
    r = requests.get(url, headers=HEADERS, timeout=30)
    if not r.ok:
        print(f"Error fetching meetings: {r.status_code} - {r.text[:200]}")
        return []
    
    return r.json().get('items', [])

def already_stored(recording_id):
    """Check if we already have this meeting stored"""
    pattern = f"*_fathom_*_{recording_id[:8]}.json"
    return any(MEMORY_DIR.glob(pattern))

def store_meeting(meeting):
    """Store meeting transcript to memory"""
    recording_id = meeting.get('recording_id', 'unknown')
    meeting_name = meeting.get('title', 'Untitled Meeting')
    created_at = meeting.get('created_at', '')
    
    try:
        if created_at:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d')
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
    except:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    clean_name = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in meeting_name).replace(' ', '_')[:50]
    filename = f"{date_str}_fathom_{clean_name}_{recording_id}.json"
    filepath = MEMORY_DIR / filename
    
    # Build transcript from the meeting data
    transcript = meeting.get('transcript', '')
    summary = meeting.get('default_summary', '')
    action_items = meeting.get('action_items', [])
    
    # If transcript is None, try to fetch it separately
    if transcript is None:
        transcript = fetch_transcript(recording_id)
    
    enriched = {
        'source': 'fathom',
        'received_at': datetime.now().isoformat(),
        'processed': False,
        'meeting': {
            'title': meeting_name,
            'recording_id': recording_id,
            'created_at': created_at,
            'url': meeting.get('url', ''),
            'share_url': meeting.get('share_url', ''),
            'recorded_by': meeting.get('recorded_by', {}),
            'calendar_invitees': meeting.get('calendar_invitees', []),
        },
        'transcript': transcript,
        'summary': summary,
        'action_items': action_items
    }
    
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(enriched, f, indent=2)
    
    return filepath

def fetch_transcript(recording_id):
    """Fetch transcript for a specific recording"""
    url = f'{BASE_URL}/recordings/{recording_id}/transcript'
    r = requests.get(url, headers=HEADERS, timeout=30)
    if not r.ok:
        return None
    return r.json()

def main():
    if not API_KEY:
        print("ERROR: FATHOM_API_KEY not set")
        sys.exit(1)
    
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check last 6 hours for new meetings
    meetings = get_meetings(since_hours=6)
    
    new_count = 0
    for meeting in meetings:
        recording_id = str(meeting.get('recording_id', ''))
        if not recording_id:
            continue
        
        if already_stored(recording_id):
            continue
        
        # Check if meeting has transcript data
        if not meeting.get('transcript') and not meeting.get('default_summary'):
            # Meeting might still be processing
            continue
        
        filepath = store_meeting(meeting)
        new_count += 1
        print(f"Stored: {filepath.name}")
    
    if new_count == 0:
        print("No new meetings with transcripts found")
    else:
        print(f"Stored {new_count} new meeting(s)")

if __name__ == '__main__':
    main()
