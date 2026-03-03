#!/usr/bin/env python3
"""
Google Calendar via Composio, with attendee cleanup patch.
Creates event, then immediately patches to remove attendees.

Usage:
  python3 gcal.py list
  python3 gcal.py events [calendar_id] [days]
  python3 gcal.py create_one '<json>'
  python3 gcal.py create <json_file>

Event JSON:
  {"summary": "...", "start": "2026-03-03T11:00:00", "end": "2026-03-03T12:00:00",
   "description": "optional", "calendar_id": "primary"}
"""
import os, sys, json, requests
from datetime import datetime, timedelta, timezone

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

API_KEY  = os.environ.get('COMPOSIO_API_KEY', '')
CONN_ID  = os.environ.get('COMPOSIO_GCAL_CONNECTION_ID', '49bd9332-c345-4ae8-a832-e046ec8835d0')
BASE     = 'https://backend.composio.dev/api/v2/actions'
HEADERS  = {'x-api-key': API_KEY, 'Content-Type': 'application/json'}

def execute(action, params):
    r = requests.post(f'{BASE}/{action}/execute', headers=HEADERS,
                      json={'input': params, 'connectedAccountId': CONN_ID}, timeout=20)
    data = r.json()
    if not r.ok or not data.get('successful'):
        return {'error': data.get('error', data)}
    return data.get('data', {})

def _patch_remove_attendees(calendar_id, event_id):
    """Patch event to remove attendees so it doesn't show as pending invite."""
    result = execute('GOOGLECALENDAR_PATCH_EVENT', {
        'calendar_id': calendar_id,
        'event_id': event_id,
        'attendees': []
    })
    return result

def list_calendars():
    r = execute('GOOGLECALENDAR_LIST_CALENDARS', {})
    if 'error' in r:
        print('ERROR:', r['error']); return
    for c in r.get('calendars', []):
        print(f"{c['id']} - {c['summary']} ({c['accessRole']})")

def list_events(calendar_id='primary', days=7):
    now = datetime.now(timezone.utc)
    r = execute('GOOGLECALENDAR_LIST_EVENTS', {
        'calendar_id': calendar_id,
        'timeMin': now.isoformat(),
        'timeMax': (now + timedelta(days=days)).isoformat(),
        'maxResults': 50, 'singleEvents': True, 'orderBy': 'startTime'
    })
    if 'error' in r:
        print('ERROR:', r['error']); return
    events = r.get('items', [])
    print(f"{len(events)} events in next {days} days:")
    for e in events:
        start = e.get('start', {}).get('dateTime', e.get('start', {}).get('date', ''))
        print(f"  {start[:16]} - {e.get('summary', '(no title)')}")

def create_event(event_data):
    cal_id = event_data.pop('calendar_id', 'primary')
    tz     = event_data.pop('timezone', 'America/New_York')

    result = execute('GOOGLECALENDAR_CREATE_EVENT', {
        'calendar_id': cal_id,
        'timezone': tz,
        'send_updates': False,
        "start_datetime": event_data.pop("start"), "end_datetime": event_data.pop("end"), **event_data
    })
    if 'error' in result:
        print('ERROR:', result['error']); return None

    rd       = result.get('response_data', result)
    event_id = rd.get('id', '')
    link     = rd.get('htmlLink', '')

    # Remove the auto-injected attendee so event lands clean
    if event_id:
        _patch_remove_attendees(cal_id, event_id)

    print(f"Created: {rd.get('summary','?')} @ {rd.get('start',{}).get('dateTime','?')[:16]} -> {link}")
    return rd

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        list_calendars()
    elif cmd == 'events':
        cal  = sys.argv[2] if len(sys.argv) > 2 else 'primary'
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        list_events(cal, days)
    elif cmd == 'create_one':
        create_event(json.loads(sys.argv[2]))
    elif cmd == 'create':
        with open(sys.argv[2]) as f:
            events = json.load(f)
        if isinstance(events, dict):
            events = [events]
        for e in events:
            create_event(e)
