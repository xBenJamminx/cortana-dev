#!/usr/bin/env python3
"""
List all enabled Google APIs in the project
Uses Service Usage API
"""
import json
import requests
from google.oauth2.credentials import Credentials

# Load credentials
with open('/root/.clawdbot/google_credentials.json') as f:
    creds_data = json.load(f)

# Try to get access token
token = creds_data.get('token')

print("Checking enabled Google APIs...")
print("="*70)

# Service Usage API endpoint
project_id = "gen-lang-client-0649414128"
url = f"https://serviceusage.googleapis.com/v1/projects/{project_id}/services?filter=state:ENABLED"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        services = data.get('services', [])
        
        print(f"\n✓ Found {len(services)} enabled APIs:\n")
        
        # Group by category
        categories = {
            'Google Workspace': [],
            'YouTube': [],
            'Maps/Places': [],
            'AI/ML': [],
            'Other': []
        }
        
        for service in services:
            name = service.get('config', {}).get('name', '')
            title = service.get('config', {}).get('title', name)
            
            if 'sheets' in name or 'docs' in name or 'gmail' in name or 'calendar' in name or 'drive' in name:
                categories['Google Workspace'].append(title)
            elif 'youtube' in name:
                categories['YouTube'].append(title)
            elif 'maps' in name or 'places' in name:
                categories['Maps/Places'].append(title)
            elif 'ml' in name or 'language' in name or 'vision' in name or 'speech' in name:
                categories['AI/ML'].append(title)
            else:
                categories['Other'].append(title)
        
        for category, items in categories.items():
            if items:
                print(f"\n{category}:")
                for item in sorted(items):
                    print(f"  ✓ {item}")
    else:
        print(f"Could not list APIs (status {response.status_code})")
        print(f"Response: {response.text[:200]}")
        print("\nAlternative: Check manually at:")
        print(f"https://console.cloud.google.com/apis/dashboard?project={project_id}")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nCheck manually at:")
    print(f"https://console.cloud.google.com/apis/dashboard?project={project_id}")

print("\n" + "="*70)
