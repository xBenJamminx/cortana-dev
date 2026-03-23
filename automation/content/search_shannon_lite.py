import json
import os
import requests

def search_gmail(creds, query):
    print(f"Searching Gmail for: {query}")
    headers = {'Authorization': f'Bearer {creds["token"]}'}
    params = {'q': query, 'maxResults': 5}
    url = 'https://www.googleapis.com/gmail/v1/users/me/messages'
    
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"Gmail Error: {resp.text}")
        return
    
    messages = resp.json().get('messages', [])
    for msg in messages:
        msg_url = f'https://www.googleapis.com/gmail/v1/users/me/messages/{msg["id"]}'
        m_resp = requests.get(msg_url, headers=headers)
        if m_resp.status_code == 200:
            m = m_resp.json()
            subject = next((h['value'] for h in m['payload']['headers'] if h['name'] == 'Subject'), 'No Subject')
            print(f"Subject: {subject}")
            print(f"Snippet: {m['snippet']}")
            print("-" * 20)

def search_contacts(creds, query):
    print(f"\nSearching Contacts for: {query}")
    headers = {'Authorization': f'Bearer {creds["token"]}'}
    params = {'query': query, 'readMask': 'names,emailAddresses,biographies'}
    url = 'https://people.googleapis.com/v1/people:searchContacts'
    
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"Contacts Error: {resp.text}")
        return
    
    results = resp.json().get('results', [])
    for person in results:
        p = person.get('person', {})
        name = p.get('names', [{}])[0].get('displayName', 'Unknown')
        email = p.get('emailAddresses', [{}])[0].get('value', 'No Email')
        print(f"Contact: {name} ({email})")

if __name__ == "__main__":
    with open('/root/.clawdbot/google_credentials.json') as f:
        creds = json.load(f)
    
    # Check if token needs refresh (simplified for this test)
    # In a real tool we'd use the refresh_token
    
    search_gmail(creds, 'Shannon')
    search_contacts(creds, 'Shannon')
