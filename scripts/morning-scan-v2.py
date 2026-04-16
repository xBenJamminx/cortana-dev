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

def slack_post(channel, text, env):
    # Post via Composio using Ben's connected account (posts as Ben, not as bot)
    api_key = env['COMPOSIO_API_KEY']
    payload = json.dumps({
        'connectedAccountId': 'b02db1f4-9d22-416c-bb78-bdb8c1bc6bb4',
        'input': {'channel': channel, 'text': text}
    }).encode()
    req = urllib.request.Request(
        'https://backend.composio.dev/api/v2/actions/SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL/execute',
        data=payload,
        headers={
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://app.composio.dev',
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        result = json.loads(r.read())
        if not result.get('data'):
            raise Exception('Composio post failed: ' + str(result))
        return result

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

    prompt = f"""You are writing a morning briefing for the FAM Smart Companion team to post in Slack.

PERIOD: {period_label}

RAW SLACK MESSAGES (sender names in [brackets] are the actual authors -- never change attribution):
{messages_block}

Write a synthesized team briefing. Your job is to summarize and consolidate -- not quote verbatim or bullet-point every line. Group related items. Merge related bugs into themes. Keep the key specifics (exact bug names, feature names, build numbers) but write it as a human summary, not a message dump.

Rules:
- NEVER include @mentions or tag anyone. Strip all @name references from your output.
- NEVER quote messages verbatim. Summarize what happened.
- Keep technical specifics (function names, build numbers, specific bugs) -- just don't repeat them multiple times.
- Drop pure conversational back-and-forth ("Yes", "Thank you", "Got it") -- only include substantive updates.
- Each person gets 2-6 bullets covering their meaningful activity. Not one vague bullet, not 30 bullets.
- Every distinct unresolved bug gets its own line in Needs Attention.
- No emojis. No markdown ##. No em dashes. Professional tone.

Format using Slack-native formatting only:
- *bold* for section headers and names
- Flat - bullets only (no nested bullets, no indentation)

Output:
Good morning team -- here's where we stand.

*{period_label}*

*[Person Name]*
- [synthesized summary of what they did, specific but not verbatim]
- [next distinct area of work]

*NEEDS ATTENTION*
- [specific unresolved issue -- build/feature/what breaks]

*TODAY'S FOCUS*
1. [Person] -- [most important thing]
2. [Person] -- [second priority]
3. [Person] -- [third priority]"""

    print('Calling OpenRouter for summarization...', flush=True)
    briefing = openrouter_complete(prompt, or_key)

    with open(BRIEFING_FILE, 'w') as f:
        f.write(briefing)

    slack_post(UPDATES_CHANNEL, briefing, env)
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
