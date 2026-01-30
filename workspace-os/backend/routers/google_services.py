"""
Google Services Router - Calendar, Drive, Gmail, Tasks
Full Google Workspace integration for Cortana OS
"""
import os
import json
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import base64

router = APIRouter()

GOOGLE_CREDS_PATH = '/root/.clawdbot/google_credentials.json'

def load_google_creds():
    """Load Google OAuth credentials"""
    if os.path.exists(GOOGLE_CREDS_PATH):
        with open(GOOGLE_CREDS_PATH, 'r') as f:
            return json.load(f)
    return None

def save_google_creds(creds):
    """Save refreshed credentials"""
    with open(GOOGLE_CREDS_PATH, 'w') as f:
        json.dump(creds, f, indent=2)

async def get_access_token():
    """Get valid access token, refreshing if needed"""
    creds = load_google_creds()
    if not creds:
        return None

    # Try to refresh the token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            creds['token_uri'],
            data={
                'client_id': creds['client_id'],
                'client_secret': creds['client_secret'],
                'refresh_token': creds['refresh_token'],
                'grant_type': 'refresh_token'
            }
        )
        if resp.status_code == 200:
            new_token = resp.json()
            creds['token'] = new_token['access_token']
            save_google_creds(creds)
            return new_token['access_token']
        else:
            # Try the existing token
            return creds.get('token')

# ============ GOOGLE CALENDAR ============

@router.get('/calendar/events')
async def get_calendar_events(
    days_ahead: int = 7,
    days_behind: int = 0,
    max_results: int = 50,
    calendar_id: str = 'primary'
):
    """Get calendar events for a date range"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated', 'configured': False}

    now = datetime.utcnow()
    time_min = (now - timedelta(days=days_behind)).isoformat() + 'Z'
    time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events',
            params={
                'timeMin': time_min,
                'timeMax': time_max,
                'maxResults': max_results,
                'singleEvents': 'true',
                'orderBy': 'startTime'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            data = resp.json()
            events = data.get('items', [])

            # Parse and enhance events
            enhanced = []
            for event in events:
                start = event.get('start', {})
                end = event.get('end', {})

                # Handle all-day vs timed events
                if 'dateTime' in start:
                    start_dt = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                    all_day = False
                else:
                    start_dt = datetime.fromisoformat(start.get('date', ''))
                    end_dt = datetime.fromisoformat(end.get('date', ''))
                    all_day = True

                # Check if event is happening now
                is_now = not all_day and start_dt <= now.replace(tzinfo=start_dt.tzinfo) <= end_dt

                # Check if event is today
                is_today = start_dt.date() == now.date()

                enhanced.append({
                    'id': event.get('id'),
                    'summary': event.get('summary', 'No Title'),
                    'description': event.get('description'),
                    'location': event.get('location'),
                    'start': start,
                    'end': end,
                    'start_dt': start_dt.isoformat(),
                    'end_dt': end_dt.isoformat(),
                    'all_day': all_day,
                    'is_now': is_now,
                    'is_today': is_today,
                    'attendees': event.get('attendees', []),
                    'organizer': event.get('organizer'),
                    'hangout_link': event.get('hangoutLink'),
                    'html_link': event.get('htmlLink'),
                    'status': event.get('status'),
                    'color_id': event.get('colorId')
                })

            return {
                'events': enhanced,
                'total': len(enhanced),
                'today_count': sum(1 for e in enhanced if e['is_today']),
                'calendar_id': calendar_id
            }
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/calendar/today')
async def get_today_events():
    """Get today's calendar events"""
    return await get_calendar_events(days_ahead=1, days_behind=0)

@router.get('/calendar/upcoming')
async def get_upcoming_events(hours: int = 4):
    """Get events starting in the next few hours"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    now = datetime.utcnow()
    time_min = now.isoformat() + 'Z'
    time_max = (now + timedelta(hours=hours)).isoformat() + 'Z'

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/calendar/v3/calendars/primary/events',
            params={
                'timeMin': time_min,
                'timeMax': time_max,
                'maxResults': 10,
                'singleEvents': 'true',
                'orderBy': 'startTime'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/calendar/list')
async def list_calendars():
    """List all calendars the user has access to"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/calendar/v3/users/me/calendarList',
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

class CalendarEvent(BaseModel):
    summary: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: str  # ISO format
    end_time: str    # ISO format
    attendees: Optional[List[str]] = None
    calendar_id: str = 'primary'

@router.post('/calendar/create')
async def create_calendar_event(event: CalendarEvent):
    """Create a new calendar event"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    event_body = {
        'summary': event.summary,
        'description': event.description,
        'location': event.location,
        'start': {'dateTime': event.start_time, 'timeZone': 'America/New_York'},
        'end': {'dateTime': event.end_time, 'timeZone': 'America/New_York'},
    }

    if event.attendees:
        event_body['attendees'] = [{'email': email} for email in event.attendees]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f'https://www.googleapis.com/calendar/v3/calendars/{event.calendar_id}/events',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json=event_body
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

# ============ GOOGLE DRIVE ============

@router.get('/drive/files')
async def list_drive_files(
    page_size: int = 25,
    order_by: str = 'modifiedTime desc',
    folder_id: Optional[str] = None,
    search: Optional[str] = None
):
    """List files in Google Drive"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated', 'configured': False}

    # Build query
    q_parts = ["trashed = false"]
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    if search:
        q_parts.append(f"name contains '{search}'")

    query = ' and '.join(q_parts)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/drive/v3/files',
            params={
                'pageSize': page_size,
                'orderBy': order_by,
                'q': query,
                'fields': 'nextPageToken, files(id, name, mimeType, modifiedTime, createdTime, size, webViewLink, iconLink, thumbnailLink, owners, shared, starred)'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            data = resp.json()
            files = data.get('files', [])

            # Categorize files
            categorized = {
                'documents': [],
                'spreadsheets': [],
                'presentations': [],
                'images': [],
                'folders': [],
                'other': []
            }

            for f in files:
                mime = f.get('mimeType', '')
                if 'folder' in mime:
                    categorized['folders'].append(f)
                elif 'document' in mime or 'text' in mime:
                    categorized['documents'].append(f)
                elif 'spreadsheet' in mime or 'excel' in mime:
                    categorized['spreadsheets'].append(f)
                elif 'presentation' in mime or 'powerpoint' in mime:
                    categorized['presentations'].append(f)
                elif 'image' in mime:
                    categorized['images'].append(f)
                else:
                    categorized['other'].append(f)

            return {
                'files': files,
                'categorized': categorized,
                'total': len(files),
                'nextPageToken': data.get('nextPageToken')
            }
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/drive/recent')
async def get_recent_drive_files(limit: int = 15):
    """Get recently modified Drive files"""
    return await list_drive_files(page_size=limit, order_by='modifiedTime desc')

@router.get('/drive/shared')
async def get_shared_files(limit: int = 20):
    """Get files shared with the user"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/drive/v3/files',
            params={
                'pageSize': limit,
                'orderBy': 'sharedWithMeTime desc',
                'q': "sharedWithMe = true",
                'fields': 'files(id, name, mimeType, modifiedTime, webViewLink, owners, sharingUser)'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/drive/starred')
async def get_starred_files():
    """Get starred files"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/drive/v3/files',
            params={
                'q': "starred = true and trashed = false",
                'fields': 'files(id, name, mimeType, modifiedTime, webViewLink)'
            },
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/drive/search')
async def search_drive(query: str, limit: int = 20):
    """Search Drive files by name"""
    return await list_drive_files(page_size=limit, search=query)

@router.get('/drive/storage')
async def get_drive_storage():
    """Get Drive storage quota"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/drive/v3/about',
            params={'fields': 'storageQuota, user'},
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            data = resp.json()
            quota = data.get('storageQuota', {})

            limit_bytes = int(quota.get('limit', 0))
            usage_bytes = int(quota.get('usage', 0))

            return {
                'limit': limit_bytes,
                'limit_gb': round(limit_bytes / (1024**3), 2),
                'usage': usage_bytes,
                'usage_gb': round(usage_bytes / (1024**3), 2),
                'percent_used': round((usage_bytes / limit_bytes) * 100, 1) if limit_bytes > 0 else 0,
                'user': data.get('user')
            }
        return {'error': resp.text}

# ============ GMAIL ============

@router.get('/gmail/messages')
async def list_gmail_messages(
    max_results: int = 25,
    label_ids: Optional[str] = 'INBOX',
    query: Optional[str] = None
):
    """List Gmail messages"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated', 'configured': False}

    params = {
        'maxResults': max_results,
        'labelIds': label_ids
    }
    if query:
        params['q'] = query

    async with httpx.AsyncClient() as client:
        # First get message IDs
        resp = await client.get(
            'https://www.googleapis.com/gmail/v1/users/me/messages',
            params=params,
            headers={'Authorization': f'Bearer {token}'}
        )

        if resp.status_code != 200:
            return {'error': resp.text, 'status': resp.status_code}

        message_list = resp.json()
        messages = message_list.get('messages', [])

        # Fetch details for each message
        detailed_messages = []
        for msg in messages[:max_results]:
            msg_resp = await client.get(
                f'https://www.googleapis.com/gmail/v1/users/me/messages/{msg["id"]}',
                params={'format': 'metadata', 'metadataHeaders': ['From', 'To', 'Subject', 'Date']},
                headers={'Authorization': f'Bearer {token}'}
            )
            if msg_resp.status_code == 200:
                msg_data = msg_resp.json()

                # Parse headers
                headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}

                detailed_messages.append({
                    'id': msg_data['id'],
                    'thread_id': msg_data['threadId'],
                    'from': headers.get('From', ''),
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', '(No Subject)'),
                    'date': headers.get('Date', ''),
                    'snippet': msg_data.get('snippet', ''),
                    'labels': msg_data.get('labelIds', []),
                    'is_unread': 'UNREAD' in msg_data.get('labelIds', []),
                    'is_starred': 'STARRED' in msg_data.get('labelIds', []),
                    'is_important': 'IMPORTANT' in msg_data.get('labelIds', [])
                })

        return {
            'messages': detailed_messages,
            'total': len(detailed_messages),
            'unread_count': sum(1 for m in detailed_messages if m['is_unread']),
            'next_page_token': message_list.get('nextPageToken')
        }

@router.get('/gmail/unread')
async def get_unread_emails(limit: int = 20):
    """Get unread emails"""
    return await list_gmail_messages(max_results=limit, query='is:unread')

@router.get('/gmail/important')
async def get_important_emails(limit: int = 20):
    """Get important emails"""
    return await list_gmail_messages(max_results=limit, label_ids='IMPORTANT')

@router.get('/gmail/message/{message_id}')
async def get_email_detail(message_id: str):
    """Get full email content"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f'https://www.googleapis.com/gmail/v1/users/me/messages/{message_id}',
            params={'format': 'full'},
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            msg_data = resp.json()

            # Parse headers
            headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}

            # Get body
            body = ''
            payload = msg_data.get('payload', {})

            # Handle multipart
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        break
            else:
                body_data = payload.get('body', {}).get('data', '')
                if body_data:
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')

            return {
                'id': msg_data['id'],
                'thread_id': msg_data['threadId'],
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'cc': headers.get('Cc', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'body': body,
                'labels': msg_data.get('labelIds', []),
                'snippet': msg_data.get('snippet', '')
            }
        return {'error': resp.text}

@router.get('/gmail/labels')
async def list_gmail_labels():
    """List all Gmail labels"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/gmail/v1/users/me/labels',
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.get('/gmail/profile')
async def get_gmail_profile():
    """Get Gmail profile info"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/gmail/v1/users/me/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

class EmailDraft(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = None

@router.post('/gmail/send')
async def send_email(email: EmailDraft):
    """Send an email"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    # Create email message
    message_lines = [
        f'To: {email.to}',
        f'Subject: {email.subject}',
        'Content-Type: text/plain; charset="UTF-8"',
        '',
        email.body
    ]
    if email.cc:
        message_lines.insert(1, f'Cc: {email.cc}')

    message = '\n'.join(message_lines)
    raw = base64.urlsafe_b64encode(message.encode()).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            'https://www.googleapis.com/gmail/v1/users/me/messages/send',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={'raw': raw}
        )
        if resp.status_code == 200:
            return {'success': True, 'message': resp.json()}
        return {'error': resp.text, 'status': resp.status_code}

@router.post('/gmail/reply/{message_id}')
async def reply_to_email(message_id: str, body: str):
    """Reply to an email"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    # Get original message
    original = await get_email_detail(message_id)
    if 'error' in original:
        return original

    # Build reply
    to = original['from']
    subject = original['subject']
    if not subject.lower().startswith('re:'):
        subject = f"Re: {subject}"

    message_lines = [
        f'To: {to}',
        f'Subject: {subject}',
        f'In-Reply-To: {message_id}',
        f'References: {message_id}',
        'Content-Type: text/plain; charset="UTF-8"',
        '',
        body
    ]

    message = '\n'.join(message_lines)
    raw = base64.urlsafe_b64encode(message.encode()).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            'https://www.googleapis.com/gmail/v1/users/me/messages/send',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={'raw': raw, 'threadId': original['thread_id']}
        )
        if resp.status_code == 200:
            return {'success': True, 'message': resp.json()}
        return {'error': resp.text}

# ============ GOOGLE TASKS ============

@router.get('/tasks/lists')
async def list_task_lists():
    """List all task lists"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated', 'configured': False}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            'https://www.googleapis.com/tasks/v1/users/@me/lists',
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text, 'status': resp.status_code}

@router.get('/tasks/items')
async def list_tasks(task_list_id: str = '@default', show_completed: bool = False):
    """List tasks from a task list"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    params = {
        'showCompleted': str(show_completed).lower(),
        'showHidden': 'false'
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f'https://www.googleapis.com/tasks/v1/lists/{task_list_id}/tasks',
            params=params,
            headers={'Authorization': f'Bearer {token}'}
        )
        if resp.status_code == 200:
            data = resp.json()
            tasks = data.get('items', [])

            # Parse and sort by due date
            for task in tasks:
                if task.get('due'):
                    task['due_date'] = task['due'][:10]  # Just the date part
                task['is_overdue'] = task.get('due') and task['due'][:10] < datetime.utcnow().strftime('%Y-%m-%d')

            tasks.sort(key=lambda x: (not x.get('due'), x.get('due', 'Z')))

            return {
                'tasks': tasks,
                'total': len(tasks),
                'overdue': sum(1 for t in tasks if t.get('is_overdue'))
            }
        return {'error': resp.text}

class TaskCreate(BaseModel):
    title: str
    notes: Optional[str] = None
    due: Optional[str] = None  # YYYY-MM-DD format

@router.post('/tasks/create')
async def create_task(task: TaskCreate, task_list_id: str = '@default'):
    """Create a new task"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    task_body = {'title': task.title}
    if task.notes:
        task_body['notes'] = task.notes
    if task.due:
        task_body['due'] = f"{task.due}T00:00:00.000Z"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f'https://www.googleapis.com/tasks/v1/lists/{task_list_id}/tasks',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json=task_body
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

@router.patch('/tasks/{task_id}/complete')
async def complete_task(task_id: str, task_list_id: str = '@default'):
    """Mark a task as completed"""
    token = await get_access_token()
    if not token:
        return {'error': 'Google not authenticated'}

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f'https://www.googleapis.com/tasks/v1/lists/{task_list_id}/tasks/{task_id}',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={'status': 'completed'}
        )
        if resp.status_code == 200:
            return resp.json()
        return {'error': resp.text}

# ============ AGGREGATED GOOGLE DASHBOARD ============

@router.get('/dashboard')
async def get_google_dashboard():
    """Get comprehensive Google services dashboard"""
    dashboard = {
        'calendar': None,
        'drive': None,
        'gmail': None,
        'tasks': None,
        'authenticated': False,
        'timestamp': datetime.utcnow().isoformat()
    }

    token = await get_access_token()
    if not token:
        return dashboard

    dashboard['authenticated'] = True

    # Calendar - Today's events
    try:
        cal = await get_calendar_events(days_ahead=1, days_behind=0, max_results=10)
        if 'events' in cal:
            dashboard['calendar'] = {
                'events': cal['events'][:5],
                'today_count': cal['today_count'],
                'next_event': cal['events'][0] if cal['events'] else None
            }
    except Exception as e:
        dashboard['calendar'] = {'error': str(e)}

    # Drive - Recent files
    try:
        drive = await list_drive_files(page_size=10)
        if 'files' in drive:
            dashboard['drive'] = {
                'recent': drive['files'][:5],
                'total': drive['total']
            }
    except Exception as e:
        dashboard['drive'] = {'error': str(e)}

    # Gmail - Unread count
    try:
        gmail = await list_gmail_messages(max_results=10, query='is:unread')
        if 'messages' in gmail:
            dashboard['gmail'] = {
                'unread': gmail['messages'][:5],
                'unread_count': gmail['unread_count']
            }
    except Exception as e:
        dashboard['gmail'] = {'error': str(e)}

    # Tasks - Due soon
    try:
        tasks = await list_tasks()
        if 'tasks' in tasks:
            dashboard['tasks'] = {
                'pending': tasks['tasks'][:5],
                'total': tasks['total'],
                'overdue': tasks['overdue']
            }
    except Exception as e:
        dashboard['tasks'] = {'error': str(e)}

    return dashboard

@router.get('/status')
async def check_google_status():
    """Check Google services authentication status"""
    creds = load_google_creds()
    if not creds:
        return {
            'authenticated': False,
            'message': 'No Google credentials found'
        }

    token = await get_access_token()
    if not token:
        return {
            'authenticated': False,
            'message': 'Could not refresh access token'
        }

    return {
        'authenticated': True,
        'scopes': creds.get('scopes', []),
        'message': 'Google services connected'
    }
