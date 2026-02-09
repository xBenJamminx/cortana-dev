import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def search_shannon():
    # Attempt to load credentials
    creds_path = '/root/.clawdbot/google_credentials.json'
    if not os.path.exists(creds_path):
        print("Credentials file not found.")
        return

    with open(creds_path) as f:
        creds_data = json.load(f)
    
    creds = Credentials.from_authorized_user_info(creds_data)
    
    # Gmail search
    print("Searching Gmail...")
    import httplib2
    http = httplib2.Http(ca_certs='/etc/ssl/certs/ca-certificates.crt')
    gmail = build('gmail', 'v1', credentials=creds, http=http)
    results = gmail.users().messages().list(userId='me', q='Shannon', maxResults=10).execute()
    messages = results.get('messages', [])
    
    for msg in messages:
        m = gmail.users().messages().get(userId='me', id=msg['id']).execute()
        subject = next((h['value'] for h in m['payload']['headers'] if h['name'] == 'Subject'), 'No Subject')
        print(f"Subject: {subject}")
        print(f"Snippet: {m['snippet']}")
        print("-" * 20)

    # Contacts search
    print("\nSearching Contacts...")
    people = build('people', 'v1', credentials=creds, http=http)
    results = people.people().searchContacts(query='Shannon', readMask='names,emailAddresses,biographies').execute()
    connections = results.get('results', [])
    for person in connections:
        p = person.get('person', {})
        names = p.get('names', [])
        if names:
            print(f"Contact Name: {names[0].get('displayName')}")
            emails = p.get('emailAddresses', [])
            if emails:
                print(f"Email: {emails[0].get('value')}")

if __name__ == "__main__":
    search_shannon()
