#!/usr/bin/env python3
"""
Google OAuth2 flow - Generate authorization URL with ALL scopes
"""
import json
import os

# Load credentials from the new file
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'REDACTED_GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', 'REDACTED_GOOGLE_CLIENT_SECRET')

# All relevant Google API scopes
ALL_SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/cloud-platform', # For ML APIs like Vision, NL, Speech
    'https://www.googleapis.com/auth/photoslibrary', # Photos
    'https://www.googleapis.com/auth/analytics.readonly', # Google Analytics
    'https://www.googleapis.com/auth/webmasters.readonly' # Search Console
]

# Build authorization URL
auth_url = (
    f"https://accounts.google.com/o/oauth2/auth?"
    f"client_id={CLIENT_ID}&"
    f"redirect_uri=http://localhost&"
    f"scope={'%20'.join(ALL_SCOPES)}&"
    f"response_type=code&"
    f"access_type=offline&"
    f"prompt=consent"
)

print("="*70)
print("GOOGLE OAUTH2 RE-AUTHORIZATION (FULL ACCESS)")
print("="*70)
print("\n1. OPEN THIS URL IN YOUR BROWSER:")
print("-"*70)
print(auth_url)
print("-"*70)
print("\n2. LOG IN AND AUTHORIZE ALL REQUESTED PERMISSIONS")
print("3. YOU'LL BE REDIRECTED TO localhost (may show error - that's OK)")
print("4. COPY THE 'code' PARAMETER FROM THE URL")
print("   (looks like: 4/0A...)")
print("\n5. PASTE THE CODE HERE")
print("\n=======================================================================")
print("Waiting for authorization code...")
