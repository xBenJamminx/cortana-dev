#!/usr/bin/env python3
"""
FAM Sync Write — Phase 2 of 2
Reads the approved delta from fam-sync-delta.json and executes all writes.
Run only after Ben approves the delta from fam-sync-analyze.py.
"""
import json, subprocess, sys, time, urllib.request

ENV_FILE = '/root/.openclaw/.env'
DELTA_FILE = '/root/.openclaw/workspace/logs/fam-sync-delta.json'
LAST_RUN_FILE = '/root/.openclaw/workspace/logs/fam-sync-last-run.txt'
TELEGRAM_TOPIC = '2122'
TELEGRAM_CLIENT = '/root/.openclaw/workspace/core/integrations/telegram.py'

NOTION_TOKEN_KEY = 'NOTION_API_KEY_WORK'
NOTION_DB = '26c4666bd1ca807b930dca5ffff9c8e9'
NOTION_PROJECT_ID = '26c4666b-d1ca-80e5-a4cd-fc007ab84486'
COMPOSIO_ACCOUNT_SHEETS = 'c42f121c-9abe-406e-a4f7-b1dd3a6c1314'
SHEETS_ID = '1TfblNSRCTqkKJFIxPpIlb8b-iE9cSeR16Lu4gMZ0Qio'

def load_env():
    env = {}
    for line in open(ENV_FILE).read().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env

def notion_create(name, status, priority, assigned_id, evidence, token):
    """Create a new Notion task via direct API."""
    body = {
        'parent': {'database_id': NOTION_DB},
        'properties': {
            'Name': {'title': [{'text': {'content': name}}]},
            'Status': {'status': {'name': status}},
            'Priority': {'select': {'name': priority}},
            'Assigned': {'people': [{'object': 'user', 'id': assigned_id}]},
            'Project': {'relation': [{'id': NOTION_PROJECT_ID}]},
        }
    }
    req = urllib.request.Request(
        'https://api.notion.com/v1/pages',
        data=json.dumps(body).encode(),
        headers={
            'Authorization': 'Bearer ' + token,
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        result = json.loads(r.read())
    return result.get('id')

def notion_update(page_id, status, evidence, token):
    """Update an existing Notion task status via direct API."""
    body = {'properties': {'Status': {'status': {'name': status}}}}
    req = urllib.request.Request(
        f'https://api.notion.com/v1/pages/{page_id}',
        data=json.dumps(body).encode(),
        method='PATCH',
        headers={
            'Authorization': 'Bearer ' + token,
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json'
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def sheets_update_cell(row, col_letter, value, env):
    """Update a single cell in the QA Sheet In Progress tab."""
    payload = json.dumps({
        'connectedAccountId': COMPOSIO_ACCOUNT_SHEETS,
        'input': {
            'spreadsheet_id': SHEETS_ID,
            'valueInputOption': 'USER_ENTERED',
            'data': [{
                'dataFilter': {'a1Range': f'In Progress!{col_letter}{row}'},
                'values': [[value]]
            }]
        }
    }).encode()
    req = urllib.request.Request(
        'https://backend.composio.dev/api/v2/actions/GOOGLESHEETS_BATCH_UPDATE_VALUES_BY_DATA_FILTER/execute',
        data=payload,
        headers={
            'x-api-key': env['COMPOSIO_API_KEY'],
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://app.composio.dev',
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def sheets_append_row(row_data, env):
    """Append a new row to the QA Sheet In Progress tab."""
    # Find next empty row by reading current data first
    read_payload = json.dumps({
        'connectedAccountId': COMPOSIO_ACCOUNT_SHEETS,
        'input': {
            'spreadsheet_id': SHEETS_ID,
            'ranges': ['In Progress!A1:A100']
        }
    }).encode()
    req = urllib.request.Request(
        'https://backend.composio.dev/api/v2/actions/GOOGLESHEETS_BATCH_GET/execute',
        data=read_payload,
        headers={
            'x-api-key': env['COMPOSIO_API_KEY'],
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://app.composio.dev',
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        result = json.loads(r.read())
    rows = result.get('data', {}).get('valueRanges', [{}])[0].get('values', [])
    next_row = len(rows) + 1

    # Write the new row
    payload = json.dumps({
        'connectedAccountId': COMPOSIO_ACCOUNT_SHEETS,
        'input': {
            'spreadsheet_id': SHEETS_ID,
            'valueInputOption': 'USER_ENTERED',
            'data': [{
                'dataFilter': {'a1Range': f'In Progress!A{next_row}'},
                'values': [row_data]
            }]
        }
    }).encode()
    req = urllib.request.Request(
        'https://backend.composio.dev/api/v2/actions/GOOGLESHEETS_BATCH_UPDATE_VALUES_BY_DATA_FILTER/execute',
        data=payload,
        headers={
            'x-api-key': env['COMPOSIO_API_KEY'],
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://app.composio.dev',
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read()), next_row

def main():
    env = load_env()

    try:
        with open(DELTA_FILE) as f:
            delta = json.load(f)
    except FileNotFoundError:
        print('ERROR: No delta file found. Run fam-sync-analyze.py first.')
        sys.exit(1)

    token = env[NOTION_TOKEN_KEY]
    today = time.strftime('%b %-d')

    created = []
    updated = []
    errors = []

    # STEP 1: Create new Notion tasks
    new_tasks = delta.get('new_tasks', [])
    print(f'Creating {len(new_tasks)} new Notion tasks...', flush=True)
    for task in new_tasks:
        try:
            page_id = notion_create(
                name=task['name'],
                status=task.get('status', 'Not Started'),
                priority=task.get('priority', 'Medium'),
                assigned_id=task['assigned_notion_id'],
                evidence=task.get('evidence', ''),
                token=token
            )
            print(f'  Created: {task["name"][:60]}', flush=True)
            created.append(task['name'])

            # Add to QA Sheet if dev-priority task
            if task.get('add_to_qa_sheet'):
                assigned_first = task['assigned_name'].split()[0]
                row_data = [
                    task['name'],   # A: Feature
                    '',             # B: Condition
                    '',             # C: Expectation
                    '',             # D: Example 1
                    '',             # E: Example 2
                    task.get('priority', 'Medium'),  # F: Priority
                    task.get('status', 'Not Started'),  # G: Status
                    f'{task.get("evidence", "")} ({today})',  # H: Comments
                    assigned_first  # I: Assigned
                ]
                _, row_num = sheets_append_row(row_data, env)
                print(f'  Added to QA Sheet row {row_num}', flush=True)
        except Exception as e:
            print(f'  ERROR creating {task["name"][:40]}: {e}', flush=True)
            errors.append(f'Create failed: {task["name"][:40]} — {e}')

    # STEP 2: Update status in Notion + QA Sheet
    status_updates = delta.get('status_updates', [])
    print(f'\nApplying {len(status_updates)} status updates...', flush=True)
    for u in status_updates:
        try:
            notion_update(u['notion_id'], u['new_status'], u.get('evidence', ''), token)
            print(f'  Notion: {u["notion_name"][:50]} → {u["new_status"]}', flush=True)
            updated.append(f'{u["notion_name"]} → {u["new_status"]}')

            # Update QA Sheet if row is known
            if u.get('qa_sheet_row'):
                row = u['qa_sheet_row']
                sheets_update_cell(row, 'G', u['new_status'], env)
                comment = f'{u.get("evidence", "")} ({today})'
                sheets_update_cell(row, 'H', comment, env)
                print(f'  QA Sheet row {row}: Status → {u["new_status"]}', flush=True)
        except Exception as e:
            print(f'  ERROR updating {u["notion_name"][:40]}: {e}', flush=True)
            errors.append(f'Update failed: {u["notion_name"][:40]} — {e}')

    # Update last-run timestamp
    with open(LAST_RUN_FILE, 'w') as f:
        f.write(str(time.time()))

    # Build report
    lines = ['FAM SYNC COMPLETE', '']
    lines.append(f'Created ({len(created)}):')
    for c in created:
        lines.append(f'  + {c}')
    lines.append('')
    lines.append(f'Updated ({len(updated)}):')
    for u in updated:
        lines.append(f'  ~ {u}')
    if errors:
        lines.append('')
        lines.append(f'Errors ({len(errors)}):')
        for e in errors:
            lines.append(f'  ! {e}')
    report = '\n'.join(lines)

    print('\n' + '=' * 60, flush=True)
    print(report, flush=True)
    print('=' * 60, flush=True)

    subprocess.run([
        'python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC, report
    ], capture_output=True)
    print('Report sent to Telegram topic 2122.', flush=True)

if __name__ == '__main__':
    main()
