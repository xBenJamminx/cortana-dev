#!/usr/bin/env python3
"""
Composio Tool - Execute actions on 500+ connected apps
Usage: composio-tool.py <ACTION_NAME> [params_json]
"""

import sys
import os
import json

# Add venv to path
venv_path = os.path.expanduser('~/clawd/composio_venv')
sys.path.insert(0, os.path.join(venv_path, 'lib', 'python3.12', 'site-packages'))

os.environ['COMPOSIO_API_KEY'] = 'ak_UjBg3sflMbHRQgr_qzwr'

from composio import ComposioToolSet, Action, App

# Connection IDs from your account
CONNECTIONS = {
    'twitter': 'be615c7e-91d0-4e04-8c83-af36dd5289ec',
    'gmail': '69fa6250-83ab-4091-becd-39bb5308b108',
    'airtable': 'f2dfacfe-536c-4c0b-aa15-4dc9c8953934',
    'googlesheets': 'c5de2782-8407-42a6-9f9b-30594f20b0f8',
    'googlecalendar': '781ec8e3-088a-445d-bab4-575968b1fcfb',
    'googlemaps': '1ad783e2-9dec-4284-a4a4-1fe2cdd38871',
    'googledocs': 'ffa787ce-e81a-48ef-9ecf-d3558d25019e',
    'googledrive': '67811d19-f59c-464c-b418-ad2cdf0f3f53',
    'slack': 'b49d568c-5258-472a-a22d-340b43c52911',
    'notion': '95a40153-5972-4b4c-851c-0632d1e0d816',
}

def get_app_from_action(action_name):
    """Extract app name from action name"""
    parts = action_name.upper().split('_')
    if len(parts) > 1:
        app = parts[0].lower()
        # Handle variations
        if app == 'google':
            if 'SHEETS' in action_name.upper():
                return 'googlesheets'
            elif 'CALENDAR' in action_name.upper():
                return 'googlecalendar'
            elif 'DOCS' in action_name.upper():
                return 'googledocs'
            elif 'DRIVE' in action_name.upper():
                return 'googledrive'
            elif 'MAPS' in action_name.upper():
                return 'googlemaps'
        return app
    return None

def execute_action(action_name, params=None):
    """Execute a Composio action"""
    toolset = ComposioToolSet()
    
    # Get the action enum
    try:
        action = getattr(Action, action_name.upper())
    except AttributeError:
        print(f"Error: Unknown action '{action_name}'")
        sys.exit(1)
    
    # Get connection ID for this app
    app = get_app_from_action(action_name)
    conn_id = CONNECTIONS.get(app)
    
    print(f"Executing {action_name} (app: {app}, connection: {conn_id})", file=sys.stderr)
    
    # Execute with connection ID
    try:
        result = toolset.execute_action(
            action=action,
            params=params or {},
            connected_account_id=conn_id
        )
        
        if isinstance(result, dict):
            print(json.dumps(result, indent=2, default=str))
        else:
            print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: composio-tool.py <ACTION_NAME> [params_json]")
        print("\nExamples:")
        print("  composio-tool.py TWITTER_USER_LOOKUP_ME")
        print("  composio-tool.py TWITTER_CREATION_OF_A_POST '{\"text\": \"Hello!\"}'")
        sys.exit(1)
    
    action_name = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    execute_action(action_name, params)

if __name__ == '__main__':
    main()
