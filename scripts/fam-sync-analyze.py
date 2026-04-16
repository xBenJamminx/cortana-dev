#!/usr/bin/env python3
"""
FAM Sync Analyze — Phase 1 of 2
Pulls Slack + Notion + QA Sheet, generates a delta list, and sends to Ben for approval.
Does NOT write anything. Run fam-sync-write.py after Ben approves.
"""
import json, re, subprocess, sys, time, urllib.request, urllib.parse

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

CHANNELS = {
    'meeting-notes': 'C09J78SH2FM',
    'updates': 'C0AL8LLGULQ',
    'testing': 'C08MV404LVD',
}
CHANNEL_LIMITS = {
    'meeting-notes': 5,
    'updates': 30,
    'testing': 30,
}

TEAM = {
    'Steven': '9b822e2d-467a-421f-b17f-af78b6e3bdd1',
    'Cao Tan Luc': '9b822e2d-467a-421f-b17f-af78b6e3bdd1',
    'Bilal': '9d54ac97-30c7-4e0d-a2bf-aa46796e4c79',
    'Muhammad Bilal Akram': '9d54ac97-30c7-4e0d-a2bf-aa46796e4c79',
    'Ben': '2ddd48a3-d87a-417a-9e5c-c41b8d8b3d90',
    'Ben Jammin': '2ddd48a3-d87a-417a-9e5c-c41b8d8b3d90',
    'Cassandra': '1edfb9ea-81ea-4798-80c8-7993279a85c8',
    'Cassandra Rosenthal': '1edfb9ea-81ea-4798-80c8-7993279a85c8',
    'Tram': 'd25c4e21-99fe-4abe-a646-077105f11e5d',
    'Tram Lee': 'd25c4e21-99fe-4abe-a646-077105f11e5d',
}

def load_env():
    env = {}
    for line in open(ENV_FILE).read().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env

def get_cutoff():
    try:
        ts = float(open(LAST_RUN_FILE).read().strip())
        age_days = (time.time() - ts) / 86400
        if age_days > 7:
            return time.time() - (7 * 86400), 'LAST 7 DAYS'
        return ts, f'SINCE LAST SYNC ({int(age_days * 24)}h ago)'
    except:
        return time.time() - (7 * 86400), 'LAST 7 DAYS'

def slack_get(endpoint, params, token):
    url = f'https://slack.com/api/{endpoint}?{params}'
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def resolve_mentions(text, user_map):
    for uid, name in user_map.items():
        text = text.replace(f'<@{uid}>', f'@{name.split()[0]}')
    return text

def pull_slack(env, cutoff):
    token = env['SLACK_BOT_TOKEN']
    users_resp = slack_get('users.list', '', token)
    user_map = {
        u['id']: u.get('real_name') or u.get('name')
        for u in users_resp.get('members', [])
        if not u.get('is_bot') and not u.get('deleted')
    }

    messages = {}
    for ch_name, cid in CHANNELS.items():
        limit = CHANNEL_LIMITS[ch_name]
        resp = slack_get('conversations.history', f'channel={cid}&limit={limit}', token)
        msgs = resp.get('messages', [])
        channel_msgs = []
        for m in msgs:
            if float(m.get('ts', 0)) > cutoff and not m.get('bot_id'):
                sender = user_map.get(m.get('user', ''), m.get('user', 'unknown'))
                text = resolve_mentions(m.get('text', ''), user_map)
                ts = time.strftime('%Y-%m-%d %H:%M', time.localtime(float(m.get('ts', 0))))
                channel_msgs.append(f'[{ts}] {sender}: {text}')
        messages[ch_name] = channel_msgs
        print(f'  #{ch_name}: {len(channel_msgs)} msgs', flush=True)

    return messages

def notion_query(status, token):
    """Query Notion database for tasks with a given status (handles pagination)."""
    tasks = []
    cursor = None
    while True:
        body = {
            'filter': {'property': 'Status', 'status': {'equals': status}},
            'page_size': 100,
        }
        if cursor:
            body['start_cursor'] = cursor
        req = urllib.request.Request(
            f'https://api.notion.com/v1/databases/{NOTION_DB}/query',
            data=json.dumps(body).encode(),
            headers={
                'Authorization': 'Bearer ' + token,
                'Notion-Version': '2022-06-28',
                'Content-Type': 'application/json'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        for page in data.get('results', []):
            props = page['properties']
            name_arr = props.get('Name', {}).get('title', [])
            name = name_arr[0]['text']['content'] if name_arr else ''
            assigned = props.get('Assigned', {}).get('people', [])
            assignee = assigned[0].get('name', '') if assigned else ''
            priority = props.get('Priority', {}).get('select') or {}
            tasks.append({
                'id': page['id'],
                'name': name,
                'status': status,
                'priority': priority.get('name', ''),
                'assigned': assignee,
            })
        if not data.get('has_more'):
            break
        cursor = data.get('next_cursor')
    return tasks

def pull_notion(env):
    token = env[NOTION_TOKEN_KEY]
    tasks = []
    for status in ['In Progress', 'In Testing', 'Not Started']:
        batch = notion_query(status, token)
        print(f'  Notion {status}: {len(batch)} tasks', flush=True)
        tasks.extend(batch)
    return tasks

def pull_qa_sheet(env):
    payload = json.dumps({
        'connectedAccountId': COMPOSIO_ACCOUNT_SHEETS,
        'input': {
            'spreadsheet_id': SHEETS_ID,
            'ranges': ['In Progress!A1:I60']
        }
    }).encode()
    req = urllib.request.Request(
        'https://backend.composio.dev/api/v2/actions/GOOGLESHEETS_BATCH_GET/execute',
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
        result = json.loads(r.read())
    rows = result.get('data', {}).get('valueRanges', [{}])[0].get('values', [])
    # Parse rows into dicts using header
    if not rows:
        return []
    header = rows[0]
    sheet_data = []
    for i, row in enumerate(rows[1:], start=2):  # row 2 = spreadsheet row 2
        padded = row + [''] * (len(header) - len(row))
        entry = dict(zip(header, padded))
        entry['_row'] = i
        sheet_data.append(entry)
    return sheet_data

def openrouter_complete(prompt, api_key):
    payload = json.dumps({
        'model': 'google/gemini-2.5-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 8000,
    }).encode()
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': 'Bearer ' + api_key,
            'Content-Type': 'application/json',
        }
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read())
        return result['choices'][0]['message']['content']

def main():
    env = load_env()
    cutoff, period_label = get_cutoff()
    print(f'FAM Sync Analyze — {period_label}', flush=True)

    print('Pulling Slack...', flush=True)
    slack_msgs = pull_slack(env, cutoff)

    print('Pulling Notion...', flush=True)
    notion_tasks = pull_notion(env)

    print('Pulling QA Sheet...', flush=True)
    qa_rows = pull_qa_sheet(env)
    print(f'  QA Sheet: {len(qa_rows)} rows', flush=True)

    # Compress Notion tasks for prompt
    notion_summary = '\n'.join(
        f'  [{t["status"]}] [{t["priority"]}] {t["name"]} — {t["assigned"]} (id: {t["id"]})'
        for t in notion_tasks
    )

    # Compress QA sheet for prompt
    qa_summary = '\n'.join(
        f'  [row {r["_row"]}] [{r.get("Status","")}] {r.get("Feature","")} — {r.get("Assigned","")} | {r.get("Comments","")}'
        for r in qa_rows
    )

    # Slack messages block
    slack_block = ''
    for ch, msgs in slack_msgs.items():
        if msgs:
            slack_block += f'\n##{ch}##\n' + '\n'.join(msgs) + '\n'

    total_slack = sum(len(v) for v in slack_msgs.values())
    if not total_slack:
        print('No new Slack activity. Nothing to sync.')
        return

    prompt = f"""You are analyzing Slack activity to generate a FAM project sync delta.

PERIOD: {period_label}

--- SLACK MESSAGES ---
{slack_block}

--- CURRENT NOTION TASKS ---
{notion_summary}

--- CURRENT QA SHEET (In Progress tab) ---
{qa_summary}

--- TEAM ---
Steven (Cao Tan Luc) = backend, APIs, voice, sentiment, memory, LLMs
Bilal (Muhammad Bilal Akram) = frontend, Unity, AR, avatar, animations, UI
Ben = product, admin, web, onboarding, research
Cassandra = business, strategy
Tram = QA testing (her items go under Steven in Notion, not her own section)

--- STATUS MAPPING ---
"done / completed / merged / finished" → Done
"in testing / being tested / shipped in build" → In Testing (shipped ≠ done)
Bug reported → In Progress (add detail to comments)
"continue working / in progress" → In Progress (no change)
No evidence → no change

--- PRIORITY ---
Blocking other work / critical path → Top
Active bug affecting usability / important feature → High
Enhancement / non-blocking → Medium
Nice to have → Low

--- RULES ---
1. Extract ONLY explicit action items and status changes from Slack. Do not invent tasks.
2. Match against existing Notion tasks by SEMANTIC MEANING (not exact string). "Fix auto-spawn" and "Implement automatic avatar spawn" are the same task.
3. New tasks = items mentioned in Slack that do NOT exist in Notion (after semantic matching).
4. Status updates = existing Notion tasks whose status should change based on Slack evidence.
5. Dev-priority tasks (Steven/Bilal work) should also be added/updated in QA Sheet. Ben/Cassandra tasks stay in Notion only.
6. Be conservative: if it's ambiguous, put it in the ambiguous list rather than creating/updating.

Output a JSON object only — no commentary before or after:

{{
  "period": "{period_label}",
  "new_tasks": [
    {{
      "name": "exact task name, full wording",
      "status": "Not Started",
      "priority": "High",
      "assigned_name": "Steven",
      "assigned_notion_id": "9b822e2d-467a-421f-b17f-af78b6e3bdd1",
      "evidence": "Apr 16 standup: Steven to fix X",
      "add_to_qa_sheet": true
    }}
  ],
  "status_updates": [
    {{
      "notion_id": "existing page id",
      "notion_name": "existing task name",
      "current_status": "In Progress",
      "new_status": "In Testing",
      "evidence": "Bilal: merged Build 49 (#updates Apr 16)",
      "qa_sheet_row": 4,
      "qa_sheet_feature": "exact feature name from QA sheet if present, else null"
    }}
  ],
  "ambiguous": [
    {{
      "item": "description of unclear item",
      "reason": "why it's ambiguous"
    }}
  ]
}}"""

    print('Analyzing with Gemini...', flush=True)
    raw = openrouter_complete(prompt, env['OPENROUTER_API_KEY'])

    # Extract JSON from response
    json_match = re.search(r'\{[\s\S]+\}', raw)
    if not json_match:
        print('ERROR: Could not parse JSON from Gemini response')
        print(raw[:500])
        return
    delta = json.loads(json_match.group(0))

    # Save delta
    with open(DELTA_FILE, 'w') as f:
        json.dump(delta, f, indent=2)
    print(f'Delta saved to {DELTA_FILE}', flush=True)

    # Format human-readable summary
    lines = [f'FAM SYNC DELTA -- {period_label}', '']

    new_tasks = delta.get('new_tasks', [])
    lines.append(f'NEW TASKS ({len(new_tasks)})')
    if new_tasks:
        for i, t in enumerate(new_tasks, 1):
            qa = ' + QA Sheet' if t.get('add_to_qa_sheet') else ' (Notion only)'
            lines.append(f'{i}. {t["name"]}')
            lines.append(f'   → {t["assigned_name"]} | {t["priority"]}{qa}')
            lines.append(f'   Source: {t["evidence"]}')
    else:
        lines.append('  None')
    lines.append('')

    status_updates = delta.get('status_updates', [])
    lines.append(f'STATUS CHANGES ({len(status_updates)})')
    if status_updates:
        for i, u in enumerate(status_updates, 1):
            qa_note = f' | QA row {u["qa_sheet_row"]}' if u.get('qa_sheet_row') else ''
            lines.append(f'{i}. {u["notion_name"]}')
            lines.append(f'   {u["current_status"]} → {u["new_status"]}{qa_note}')
            lines.append(f'   Evidence: {u["evidence"]}')
    else:
        lines.append('  None')
    lines.append('')

    ambiguous = delta.get('ambiguous', [])
    if ambiguous:
        lines.append(f'AMBIGUOUS -- needs your call ({len(ambiguous)})')
        for i, a in enumerate(ambiguous, 1):
            lines.append(f'{i}. {a["item"]}')
            lines.append(f'   Reason: {a["reason"]}')
        lines.append('')

    lines.append('Reply "approved" to write all changes, or tell me what to adjust.')
    summary = '\n'.join(lines)

    print('\n' + '=' * 60, flush=True)
    print(summary, flush=True)
    print('=' * 60, flush=True)

    # Send to Telegram
    subprocess.run([
        'python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC, summary
    ], capture_output=True)
    print('Delta sent to Telegram topic 2122.', flush=True)

if __name__ == '__main__':
    main()
