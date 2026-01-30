#!/usr/bin/env python3
"""
Google Calendar integration
Supports CalDAV (with app password) or Browser automation
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class GoogleCalendar:
    """Google Calendar access via CalDAV or Browser"""
    
    def __init__(self, email: str = None, app_password: str = None):
        self.email = email or os.getenv('GMAIL_EMAIL', 'benjoselson@gmail.com')
        self.app_password = app_password or os.getenv('GMAIL_APP_PASSWORD')
        
    def read_caldav(self, days: int = 7) -> List[Dict]:
        """
        Read calendar events via CalDAV
        Uses same credentials as Gmail IMAP
        """
        try:
            import caldav
            
            # Google Calendar CalDAV URL
            url = "https://apidata.googleusercontent.com/caldav/v2/"
            
            # Connect using app password
            client = caldav.DAVClient(
                url=url,
                username=self.email,
                password=self.app_password
            )
            
            # Get principal (user's calendars)
            principal = client.principal()
            calendars = principal.calendars()
            
            if not calendars:
                return [{'note': 'No calendars found'}]
            
            # Get primary calendar (usually first)
            calendar = calendars[0]
            
            # Date range
            start = datetime.now()
            end = start + timedelta(days=days)
            
            # Fetch events
            events = calendar.date_search(start=start, end=end)
            
            results = []
            for event in events:
                vevent = event.vobject_instance.vevent
                results.append({
                    'summary': str(vevent.summary.value) if hasattr(vevent, 'summary') else 'No title',
                    'start': vevent.dtstart.value.isoformat() if hasattr(vevent, 'dtstart') else None,
                    'end': vevent.dtend.value.isoformat() if hasattr(vevent, 'dtend') else None,
                    'location': str(vevent.location.value) if hasattr(vevent, 'location') else None,
                    'description': str(vevent.description.value) if hasattr(vevent, 'description') else None
                })
            
            return results
            
        except ImportError:
            return [{'error': 'caldav library not installed. Run: pip install caldav'}]
        except Exception as e:
            return [{'error': str(e), 'note': 'CalDAV may not work with app passwords. Try browser automation.'}]
    
    def list_events_simple(self, days: int = 7) -> List[Dict]:
        """Simple wrapper to get upcoming events"""
        return self.read_caldav(days)

# Browser-based alternative (if CalDAV fails)
class CalendarBrowser:
    """Access Calendar via browser automation"""
    
    def check_calendar(self, days: int = 7) -> List[Dict]:
        """
        Check calendar via browser
        Requires being logged into Google in browser profile
        """
        return [{
            'note': 'Calendar browser automation',
            'steps': [
                '1. Log into calendar.google.com in browser',
                '2. I can navigate and extract events',
                '3. Or use Google Calendar API with OAuth2'
            ]
        }]

# Quick test function
def test_calendar():
    """Test calendar connection"""
    cal = GoogleCalendar()
    events = cal.list_events_simple(days=7)
    return events

if __name__ == "__main__":
    print("Testing Calendar...")
    events = test_calendar()
    print(f"Found {len(events)} events")
    for e in events[:5]:
        if 'error' not in e and 'note' not in e:
            print(f"  - {e.get('summary')} at {e.get('start')}")
        else:
            print(f"  {e}")
