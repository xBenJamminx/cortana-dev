#!/usr/bin/env python3
"""
Google OAuth2 - Generate authorization URL
"""
import json

# Load credentials
with open('/root/.clawdbot/media/inbound/c0ca9173-11ac-4cbf-b36f-b3adf8eb1032.json') as f:
    creds = json.load(f)

client_id = creds['installed']['client_id']
client_secret = creds['installed']['client_secret']
redirect_uri = creds['installed']['redirect_uris'][0]

# Scopes for Calendar + Gmail
scopes = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

# Build authorization URL
auth_url = (
    f"https://accounts.google.com/o/oauth2/auth?"
    f"client_id={client_id}&"
    f"redirect_uri={redirect_uri}&"
    f"scope={'%20'.join(scopes)}&"
    f"response_type=code&"
    f"access_type=offline&"
    f"prompt=consent"
)

print("="*70)
print("GOOGLE OAUTH2 AUTHORIZATION")
print("="*70)
print("\n1. OPEN THIS URL IN YOUR BROWSER:")
print("-"*70)
print(auth_url)
print("-"*70)
print("\n2. LOG IN AND AUTHORIZE THE APP")
print("3. YOU'LL BE REDIRECTED TO localhost (may show error - that's OK)")
print("4. COPY THE 'code' PARAMETER FROM THE URL")
print("   (looks like: 4/0A...)")
print("\n5. PASTE THE CODE HERE")
print("="*70)

# Save client secret for later
with open('/root/.clawdbot/google_client_secret.txt', 'w') as f:
    f.write(client_secret)

print("\n✓ Client secret saved")
print("Waiting for authorization code...")
