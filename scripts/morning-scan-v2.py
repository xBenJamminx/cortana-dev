#!/usr/bin/env python3
"""
Morning Scan v2 - Direct Slack pull + OpenRouter summarization + Slack post
No agent framework needed. Fast, reliable, correct attribution.
"""
import urllib.request, json, time, subprocess, sys

ENV_FILE = '/root/.openclaw/.env'
LAST_RUN_FILE = '/root/.openclaw/workspace/logs/morning-scan-last-run.txt'
BRIEFING_FILE = '/root/.openclaw/workspace/logs/morning-scan-briefing.txt'
UPDATES_CHANNEL = 'C0AL8LLGULQ'
CHANNELS = {
    'meeting-notes': 'C09J78SH2FM',
    'updates': 'C0AL8LLGULQ',
    'testing': 'C08MV404LVD',
}

def load_env():
    env = {}
    for line in open(ENV_FILE).read().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env

def slack_get(endpoint, params, token):
    url = f'https://slack.com/api/{endpoint}?{params}'
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def slack_post(channel, text, token):
    payload = json.dumps({'channel': channel, 'text': text}).encode()
    req = urllib.request.Request(
        'https://slack.com/api/chat.postMessage',
        data=payload,
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        result = json.loads(r.read())
        if not result.get('ok'):
            raise Exception('Slack post failed: ' + result.get('error', 'unknown'))
        return result

def openrouter_complete(prompt, api_key):
    payload = json.dumps({
        'model': 'google/gemini-2.5-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 2000,
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

def get_cutoff():
    try:
        with open(LAST_RUN_FILE) as f:
            ts = float(f.read().strip())
        age_days = (time.time() - ts) / 86400
        if age_days > 2:
            return time.time() - (3 * 86400), 'LAST 3 DAYS'
        elif age_days > 1:
            return time.time() - (2 * 86400), 'LAST 2 DAYS'
        else:
            return ts, 'LAST 24H'
    except:
        return time.time() - 86400, 'LAST 24H'

def resolve_mentions(text, user_map):
    for uid, name in user_map.items():
        text = text.replace(f'<@{uid}>', f'@{name.split()[0]}')
    return text

def main():
    env = load_env()
    slack_token = env['SLACK_BOT_TOKEN']
    or_key = env['OPENROUTER_API_KEY']

    cutoff, period_label = get_cutoff()
    print(f'Pulling since {time.ctime(cutoff)} ({period_label})', flush=True)

    users_resp = slack_get('users.list', '', slack_token)
    user_map = {
        u['id']: u.get('real_name') or u.get('name')
        for u in users_resp.get('members', [])
        if not u.get('is_bot') and not u.get('deleted')
    }

    raw_msgs = []
    for ch_name, cid in CHANNELS.items():
        resp = slack_get('conversations.history', f'channel={cid}&limit=100', slack_token)
        msgs = resp.get('messages', [])
        for m in msgs:
            if float(m.get('ts', 0)) > cutoff and m.get('user') and not m.get('bot_id'):
                sender = user_map.get(m['user'], m['user'])
                text = resolve_mentions(m.get('text', ''), user_map)
                raw_msgs.append(f'[#{ch_name}] [{sender}]: {text}')
        print(f'  #{ch_name}: {len([m for m in msgs if float(m.get("ts",0)) > cutoff and m.get("user") and not m.get("bot_id")])} msgs', flush=True)

    if not raw_msgs:
        print('No new activity. Skipping.')
        with open(LAST_RUN_FILE, 'w') as f:
            f.write(str(time.time()))
        return

    messages_block = '\n'.join(raw_msgs)

    prompt = f"""You are building a Slack morning briefing for the FAM Smart Companion team.

PERIOD: {period_label}

RAW SLACK MESSAGES (sender is always correct -- do not change attribution):
{messages_block}

Format a concise team briefing using ONLY Slack-native formatting:
- *bold* for section headers and person names
- flat bullet list with - (no nested bullets, Slack mobile renders them poorly)
- No markdown ##, no **, no em dashes

Output format:
Good morning team -- here's where we stand.

*{period_label}*

*[Person Name]*
- [what they did/reported, specific and concrete]
- [next item]

*[Next Person]*
- ...

*NEEDS ATTENTION*
- [unresolved issue with specifics]

*TODAY'S FOCUS*
1. [Person] -- [most important thing]
2. [Person] -- [second priority]  
3. [Person] -- [third priority]

Rules:
- Only include people who have messages. Do not invent activity.
- Attribution is exact: use the sender name from [brackets] only.
- Include ALL bugs reported. Don't summarize away specifics.
- Needs Attention = blocked or unresolved. List every open issue.
- Today's Focus = max 3 items based on evidence.
- No emojis. Professional."""

    print('Calling OpenRouter for summarization...', flush=True)
    briefing = openrouter_complete(prompt, or_key)

    with open(BRIEFING_FILE, 'w') as f:
        f.write(briefing)

    slack_post(UPDATES_CHANNEL, briefing, slack_token)
    print('Posted to #updates', flush=True)

    with open(LAST_RUN_FILE, 'w') as f:
        f.write(str(time.time()))

    subprocess.run([
        'python3', '/root/.openclaw/workspace/core/integrations/telegram.py',
        '--topic', '31', 'Morning scan posted to #updates.'
    ], capture_output=True)
    print('Done.', flush=True)

if __name__ == '__main__':
    main()
