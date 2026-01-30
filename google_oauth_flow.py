#!/usr/bin/env python3
"""
Google OAuth2 flow for Calendar and Gmail
"""
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes we need
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def create_oauth_flow(client_id, client_secret):
    """Create OAuth flow with client credentials"""
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }
    
    flow = InstalledAppFlow.from_client_config(
        client_config, SCOPES)
    
    return flow

def run_oauth_flow(client_id, client_secret):
    """Run OAuth flow and return credentials"""
    flow = create_oauth_flow(client_id, client_secret)
    
    # Run console-based flow (prints URL, you paste code)
    creds = flow.run_console()
    
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

if __name__ == "__main__":
    CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '1065692947130-821rth5vjk1nb1onhbulu5o8pjihgvkt.apps.googleusercontent.com')
    CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    if not CLIENT_SECRET:
        print("ERROR: Need GOOGLE_CLIENT_SECRET environment variable")
        print("\nTo get client secret:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Find the OAuth client")
        print("3. Click the download icon (JSON)")
        print("4. Copy the 'client_secret' value")
        exit(1)
    
    print("Running OAuth2 flow...")
    print("\n1. You'll get a URL to open in your browser")
    print("2. Log in and authorize the app")
    print("3. Copy the authorization code")
    print("4. Paste it back here\n")
    
    creds = run_oauth_flow(CLIENT_ID, CLIENT_SECRET)
    
    print("\n✓ OAuth2 complete!")
    print(f"Refresh token: {creds['refresh_token'][:20]}...")
    
    # Save to file
    with open('/root/.clawdbot/google_credentials.json', 'w') as f:
        json.dump(creds, f, indent=2)
    
    print("\nSaved to: /root/.clawdbot/google_credentials.json")
