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
    'meeting-notes': 20,
    'updates': 60,
    'testing': 60,
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
        if age_days > 14:
            return time.time() - (14 * 86400), 'LAST 14 DAYS'
        label = f'LAST {int(age_days)} DAYS' if age_days >= 1 else f'SINCE LAST SYNC ({int(age_days * 24)}h ago)'
        return ts, label
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
            msg_ts = float(m.get('ts', 0))
            # Skip pure bot messages (no user = automated noise)
            # Keep messages with both user+bot_id — those are Composio-proxied user posts (meeting notes, etc.)
            if m.get('bot_id') and not m.get('user'):
                continue

            # Include top-level message if after cutoff
            if msg_ts > cutoff:
                sender = user_map.get(m.get('user', ''), m.get('user', 'unknown'))
                text = resolve_mentions(m.get('text', ''), user_map)
                ts_fmt = time.strftime('%Y-%m-%d %H:%M', time.localtime(msg_ts))
                channel_msgs.append(f'[{ts_fmt}] {sender}: {text}')

            # Fetch thread replies if thread has activity after cutoff
            latest_reply = float(m.get('latest_reply', 0))
            if m.get('reply_count', 0) > 0 and latest_reply > cutoff:
                thread_resp = slack_get(
                    'conversations.replies',
                    f'channel={cid}&ts={m["ts"]}&limit=10',
                    token
                )
                thread_replies = []
                for tm in thread_resp.get('messages', [])[1:]:  # skip parent
                    t_ts = float(tm.get('ts', 0))
                    if t_ts > cutoff and not tm.get('bot_id'):
                        t_sender = user_map.get(tm.get('user', ''), tm.get('user', 'unknown'))
                        t_text = resolve_mentions(tm.get('text', ''), user_map)
                        t_ts_fmt = time.strftime('%Y-%m-%d %H:%M', time.localtime(t_ts))
                        thread_replies.append(f'[{t_ts_fmt}] {t_sender} [thread]: {t_text}')
                # Limit to last 5 replies to reduce context bloat
                channel_msgs.extend(thread_replies[-5:])

        messages[ch_name] = channel_msgs
        print(f'  #{ch_name}: {len(channel_msgs)} msgs (incl. threads)', flush=True)

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
        'max_tokens': 65000,
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

--- TEAM (use exact notion_id values below) ---
Steven (Cao Tan Luc) = backend, APIs, voice, sentiment, memory, LLMs | notion_id: 9b822e2d-467a-421f-b17f-af78b6e3bdd1
Bilal (Muhammad Bilal Akram) = frontend, Unity, AR, avatar, animations, UI | notion_id: 9d54ac97-30c7-4e0d-a2bf-aa46796e4c79
Ben (Ben Jammin) = product, admin, web, onboarding, research | notion_id: 2ddd48a3-d87a-417a-9e5c-c41b8d8b3d90
Cassandra (Cassandra Rosenthal) = business, strategy | notion_id: 1edfb9ea-81ea-4798-80c8-7993279a85c8
Tram (Tram Lee) = QA testing — her items go under Steven in Notion, not her own section | notion_id: d25c4e21-99fe-4abe-a646-077105f11e5d

--- VALID STATUSES ---
Not Started, In Progress, In Testing, Done
(No other values. "Fixed", "Resolved", "Complete" etc. all map to Done.)

--- STATUS MAPPING ---
"done / completed / merged / finished / fixed / resolved / closed / pushed / deployed / shipped / submitted / sent / confirmed working" → Done
"in testing / being tested / shipped in build / build X is out / added to build / available in build / ready to test / can test now" → In Testing (shipped ≠ done — it just moved to testing)
Bug reported / issue identified / broken / not working / regressed → In Progress (if currently Not Started or Done, this is a regression)
"continue working / in progress / working on" → no change, do NOT emit a status update
No evidence → no change, do NOT emit a status update
If new_status == current_status → OMIT from status_updates entirely

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
6. NEW TASK criteria: (a) someone commits to doing something, OR a specific bug/feature/deliverable is named; (b) there is a clear owner; (c) it does NOT already exist in Notion semantically. Be INCLUSIVE — if someone says "I'll do X", "I need to fix X", "working on X", "I'm adding X" and X is not in Notion, create the task. Do NOT create tasks from: vague complaints with no owner, general questions, acknowledgements, praise, or meeting scheduling.
7. THREAD REPLIES ARE AUTHORITATIVE: If a bug or issue is raised in a message, but a [thread] reply on that same conversation marks it as fixed/done/resolved — do NOT create a new task. Instead treat it as a Done status update to the matching existing Notion task (or ignore it entirely if it doesn't exist in Notion yet and was resolved immediately). The final state of a thread is what matters, not the initial report.
8. SILENTLY IGNORE: scheduling updates, meeting times, attendance, pure acknowledgements ("great!", "thanks!"), praise with no action, general observations with no owner and no commitment.
9. MEETING NOTES (#meeting-notes) ARE HIGH PRIORITY: If action items appear in meeting notes, extract ALL of them as new tasks unless they already exist in Notion semantically. Meeting note action items always have clear owners and are explicit commitments — treat them as the most reliable source.
9. AMBIGUOUS = only items where you genuinely cannot decide: (a) is this a new task or an update to an existing one? (b) who owns it? (c) does Slack evidence clearly say done/testing but you're not sure which Notion task it maps to? Aim for 0–5 ambiguous items max. When in doubt, make the call rather than surfacing it.

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

    # Save raw for debugging
    raw_file = DELTA_FILE.replace('fam-sync-delta.json', 'fam-sync-raw-last.txt')
    with open(raw_file, 'w') as f:
        f.write(raw)

    def fix_json_strings(s):
        """Repair common JSON generation issues from LLMs."""
        # First pass: escape literal whitespace in strings
        result = []
        in_string = False
        escaped = False
        for ch in s:
            if escaped:
                result.append(ch)
                escaped = False
            elif ch == '\\':
                result.append(ch)
                escaped = True
            elif ch == '"':
                in_string = not in_string
                result.append(ch)
            elif in_string and ch == '\n':
                result.append('\\n')
            elif in_string and ch == '\r':
                result.append('\\r')
            elif in_string and ch == '\t':
                result.append('\\t')
            else:
                result.append(ch)
        s = ''.join(result)

        # Second pass: fix common trailing issues (truncated arrays/objects)
        s = re.sub(r',\s*\]\s*$', ']', s)  # trailing comma before ]
        s = re.sub(r',\s*\}\s*$', '}', s)  # trailing comma before }

        return s

    # Extract JSON — handle optional ```json code fence wrapper
    fence_match = re.search(r'```(?:json)?\s*(\{[\s\S]+?\})\s*```', raw)
    json_match = fence_match or re.search(r'\{[\s\S]+\}', raw)
    if not json_match:
        print('ERROR: Could not parse JSON from Gemini response')
        print(raw[:500])
        return
    json_str = fence_match.group(1) if fence_match else json_match.group(0)
    try:
        delta = json.loads(fix_json_strings(json_str))
    except json.JSONDecodeError as e:
        print(f'ERROR: JSON parse failed at char {e.pos}: {e.msg}')
        snippet = raw[max(0, e.pos - 150):e.pos + 150]
        print(f'Context:\n{snippet}')
        return

    # Save delta
    with open(DELTA_FILE, 'w') as f:
        json.dump(delta, f, indent=2)
    print(f'Delta saved to {DELTA_FILE}', flush=True)

    def h(text):
        """HTML-escape user content."""
        if not text:
            return ''
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    new_tasks = delta.get('new_tasks', [])
    status_updates = delta.get('status_updates', [])
    ambiguous = delta.get('ambiguous', [])

    STATUS_ICON = {
        'Done': '✅',
        'In Testing': '🧪',
        'In Progress': '🔙',
        'Not Started': '⏸',
    }

    parts = [f'<b>FAM SYNC — {period_label}</b>']
    counts = []
    if new_tasks: counts.append(f'{len(new_tasks)} new')
    if status_updates: counts.append(f'{len(status_updates)} updates')
    if ambiguous: counts.append(f'{len(ambiguous)} needs your call')
    parts.append('  ·  '.join(counts) if counts else 'No changes detected')

    if new_tasks:
        parts.append('')
        parts.append('<b>NEW TASKS</b>')
        for i, t in enumerate(new_tasks, 1):
            qa = '+QA' if t.get('add_to_qa_sheet') else ''
            meta = '  ·  '.join(filter(None, [
                h(t.get('assigned_name', '')),
                h(t.get('priority', '')),
                qa,
            ]))
            parts.append(f'{i}.  {h(t["name"])}')
            parts.append(f'    <i>{meta}</i>')

    if status_updates:
        parts.append('')
        parts.append('<b>STATUS CHANGES</b>')
        # Sort: Done first, then In Testing, then regressions
        order = {'Done': 0, 'In Testing': 1, 'In Progress': 2, 'Not Started': 3}
        sorted_updates = sorted(status_updates, key=lambda u: order.get(u.get('new_status', ''), 9))
        for u in sorted_updates:
            # Skip no-ops
            if u.get('current_status') == u.get('new_status'):
                continue
            icon = STATUS_ICON.get(u.get('new_status', ''), '→')
            qa_note = f' [QA {u["qa_sheet_row"]}]' if u.get('qa_sheet_row') else ''
            parts.append(f'{icon}  {h(u["notion_name"])}{qa_note}')

    if ambiguous:
        parts.append('')
        parts.append('<b>NEEDS YOUR CALL</b>')
        for i, a in enumerate(ambiguous, 1):
            parts.append(f'{i}.  {h(a["item"])}')
            parts.append(f'    <i>{h(a["reason"])}</i>')

    parts.append('')
    parts.append('<i>"approved" to write  ·  or tell me what to adjust</i>')
    summary = '\n'.join(parts)

    print('\n' + '=' * 60, flush=True)
    print(summary, flush=True)
    print('=' * 60, flush=True)

    # Send to Telegram (HTML formatted)
    result = subprocess.run([
        'python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC, '--parse-mode', 'HTML', summary
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f'WARNING: Telegram send failed (exit {result.returncode}): {result.stderr.strip()}', flush=True)
        # Fallback: send without HTML parse mode
        subprocess.run([
            'python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC, summary
        ], capture_output=True)
        print('Delta sent to Telegram topic 2122 (plain text fallback).', flush=True)
    else:
        print('Delta sent to Telegram topic 2122.', flush=True)

if __name__ == '__main__':
    main()
