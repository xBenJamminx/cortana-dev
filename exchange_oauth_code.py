#!/usr/bin/env python3
"""
Exchange authorization code for refresh token (with new credentials)
"""
import requests
import json
import os

# Authorization code from user
auth_code = "4/0ASc3gC3ucgZ5mjt4Dt6sBXnJsPhHy9swhtwVPWkm1Bq6yMllX3dnAJX8MvJn7uTkXuDo0Q"

# Load new client credentials
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '1065692947130-5diqmvre0cse8sk48394ujs0a0cbrv4b.apps.googleusercontent.com')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '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')

# Exchange code for tokens
token_url = "https://oauth2.googleapis.com/token"

data = {
    "code": auth_code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": "http://localhost",
    "grant_type": "authorization_code"
}

response = requests.post(token_url, data=data)
result = response.json()

if 'error' in result:
    print(f"ERROR: {result['error']}")
    print(f"Description: {result.get('error_description', '')}")
else:
    print("✓ OAuth2 successful!")
    print(f"\nAccess token: {result['access_token'][:20]}...")
    print(f"Refresh token: {result['refresh_token'][:20]}...")
    print(f"Expires in: {result['expires_in']} seconds")
    
    # Save credentials
    creds = {
        'token': result['access_token'],
        'refresh_token': result['refresh_token'],
        'token_uri': 'https://oauth2.googleapis.com/token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scopes': result['scope'].split()
    }
    
    with open('/root/.clawdbot/google_credentials.json', 'w') as f:
        json.dump(creds, f, indent=2)
    
    print("\n✓ Credentials saved to: /root/.clawdbot/google_credentials.json")
    print("\nALL Google services should now be connected with full access!")
