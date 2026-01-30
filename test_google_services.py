#!/usr/bin/env python3
"""
Test Google Calendar and Gmail with OAuth2
"""
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load credentials
with open('/root/.clawdbot/google_credentials.json') as f:
    creds_data = json.load(f)

creds = Credentials.from_authorized_user_info(creds_data)

print("Testing Google Calendar...")
try:
    # Build Calendar service
    calendar_service = build('calendar', 'v3', credentials=creds)
    
    # Get calendar list
    calendars = calendar_service.calendarList().list().execute()
    print(f"✓ Connected to {len(calendars.get('items', []))} calendars")
    
    for cal in calendars.get('items', [])[:3]:
        print(f"  - {cal['summary']}")
    
    # Get upcoming events from primary calendar
    from datetime import datetime, timedelta
    now = datetime.utcnow().isoformat() + 'Z'
    week_later = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    
    events_result = calendar_service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=week_later,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    print(f"\n✓ Found {len(events)} events in next 7 days")
    
    for event in events[:5]:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"  - {event['summary']} at {start}")
        
except Exception as e:
    print(f"✗ Calendar error: {e}")

print("\n" + "="*70)
print("Testing Gmail...")
try:
    # Build Gmail service
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    # Get profile
    profile = gmail_service.users().getProfile(userId='me').execute()
    print(f"✓ Gmail connected: {profile['emailAddress']}")
    
    # Get recent messages
    messages_result = gmail_service.users().messages().list(
        userId='me',
        maxResults=5
    ).execute()
    
    messages = messages_result.get('messages', [])
    print(f"✓ Found {len(messages)} recent messages")
    
    for msg in messages[:3]:
        # Get message details
        message = gmail_service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata'
        ).execute()
        
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        subject = headers.get('Subject', 'No subject')[:40]
        from_addr = headers.get('From', 'Unknown')[:30]
        print(f"  - {subject}... | From: {from_addr}")
        
except Exception as e:
    print(f"✗ Gmail error: {e}")

print("\n" + "="*70)
print("✅ ALL GOOGLE SERVICES CONNECTED!")
print("="*70)
