#!/usr/bin/env python3
"""
YouTube OAuth Flow - Run this to authenticate
"""
import json
import os
from pathlib import Path

# Google OAuth imports
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Installing required packages...")
    os.system("pip install google-auth-oauthlib google-api-python-client -q")
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

# Config
CLIENT_SECRET_FILE = Path("/root/.config/youtube/client_secret.json")
CREDENTIALS_FILE = Path("/root/.config/youtube/credentials.json")
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def main():
    print("="*60)
    print("YouTube OAuth Setup")
    print("="*60)
    
    if not CLIENT_SECRET_FILE.exists():
        print(f"❌ Client secret file not found: {CLIENT_SECRET_FILE}")
        return
    
    print("\n🔄 Starting OAuth flow...")
    print("A browser window should open for authorization.")
    print("If running headless, copy the URL and paste the auth code.\n")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE),
            SCOPES
        )
        
        # Try headless first, fall back to console
        try:
            credentials = flow.run_local_server(port=8080)
        except Exception as e:
            print(f"Local server failed ({e}), trying console auth...")
            credentials = flow.run_console()
        
        # Save credentials
        creds_data = {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'token_uri': credentials.token_uri
        }
        
        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(creds_data, f, indent=2)
        
        print(f"\n✅ Credentials saved to: {CREDENTIALS_FILE}")
        
        # Test the connection
        print("\n🧪 Testing connection...")
        youtube = build('youtube', 'v3', credentials=credentials)
        channels_response = youtube.channels().list(part='snippet,statistics', mine=True).execute()
        
        if channels_response.get('items'):
            channel = channels_response['items'][0]
            print(f"\n✅ Connected!")
            print(f"   Channel: {channel['snippet']['title']}")
            print(f"   Subscribers: {channel['statistics'].get('subscriberCount', 'N/A')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
