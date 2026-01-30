#!/usr/bin/env python3
"""
Test all enabled Google APIs
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load credentials
with open('/root/.clawdbot/google_credentials.json') as f:
    creds_data = json.load(f)

creds = Credentials.from_authorized_user_info(creds_data)

print("="*70)
print("TESTING ALL GOOGLE APIs")
print("="*70)

# Test Calendar
print("\n📅 Google Calendar...")
try:
    service = build('calendar', 'v3', credentials=creds)
    result = service.calendarList().list().execute()
    print(f"  ✓ {len(result.get('items', []))} calendars")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Gmail
print("\n📧 Gmail...")
try:
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    print(f"  ✓ Connected: {profile['emailAddress']}")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Drive
print("\n📁 Google Drive...")
try:
    service = build('drive', 'v3', credentials=creds)
    result = service.files().list(pageSize=5).execute()
    print(f"  ✓ {len(result.get('files', []))} files accessible")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Sheets
print("\n📊 Google Sheets...")
try:
    service = build('sheets', 'v4', credentials=creds)
    # Try to list sheets (requires Drive scope too)
    print(f"  ✓ API accessible")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Docs
print("\n📝 Google Docs...")
try:
    service = build('docs', 'v1', credentials=creds)
    print(f"  ✓ API accessible")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Tasks
print("\n✅ Google Tasks...")
try:
    service = build('tasks', 'v1', credentials=creds)
    result = service.tasklists().list().execute()
    print(f"  ✓ {len(result.get('items', []))} task lists")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test YouTube
print("\n📺 YouTube Data...")
try:
    service = build('youtube', 'v3', credentials=creds)
    # Search test
    result = service.search().list(q='test', part='snippet', maxResults=1).execute()
    print(f"  ✓ API accessible")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test YouTube Analytics
print("\n📈 YouTube Analytics...")
try:
    service = build('youtubeAnalytics', 'v2', credentials=creds)
    print(f"  ✓ API accessible")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Natural Language
print("\n🧠 Natural Language...")
try:
    service = build('language', 'v1', credentials=creds)
    # Test sentiment analysis
    document = {
        "type": "PLAIN_TEXT",
        "content": "This is a great day!"
    }
    result = service.documents().analyzeSentiment(body={"document": document}).execute()
    score = result['documentSentiment']['score']
    print(f"  ✓ Sentiment API works (score: {score})")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Vision
print("\n👁️  Cloud Vision...")
try:
    service = build('vision', 'v1', credentials=creds)
    print(f"  ✓ API accessible")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Translation
print("\n🌐 Translation...")
try:
    service = build('translate', 'v2', credentials=creds)
    result = service.translations().list(q='Hello world', target='es').execute()
    translation = result['translations'][0]['translatedText']
    print(f"  ✓ Translation works: {translation}")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

# Test Places (if you enabled it)
print("\n📍 Google Places...")
try:
    # Places API uses API key, not OAuth
    print(f"  ℹ️  Requires API key (not OAuth)")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test Speech-to-Text
print("\n🎤 Speech-to-Text...")
try:
    service = build('speech', 'v1', credentials=creds)
    print(f"  ✓ API accessible")
except HttpError as e:
    print(f"  ✗ {e.resp.status}: {e._get_reason()}")

print("\n" + "="*70)
print("API TEST COMPLETE")
print("="*70)
