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

def parse_inline(text):
    """Parse a line with *bold* markers into rich_text elements."""
    import re
    elements = []
    parts = re.split(r'(\*[^*]+\*)', text)
    for part in parts:
        if part.startswith('*') and part.endswith('*') and len(part) > 2:
            elements.append({'type': 'text', 'text': part[1:-1], 'style': {'bold': True}})
        elif part:
            elements.append({'type': 'text', 'text': part})
    return elements if elements else [{'type': 'text', 'text': text}]


def text_to_blocks(text):
    """Convert briefing text to Slack Block Kit blocks.
    Supports:
      - *bold* for headers
      - '- ' for top-level bullets
      '  - ' (2-space indent) for sub-bullets
      - '1. ' for numbered lists
    """
    import re
    blocks = []
    lines = text.strip().splitlines()
    i = 0

    def is_bullet(line):
        return re.match(r'^- ', line)

    def is_sub_bullet(line):
        return re.match(r'^  - ', line)

    def is_numbered(line):
        return re.match(r'^\d+\. ', line)

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        # Top-level bullet (possibly followed by sub-bullets)
        if is_bullet(raw) and not is_sub_bullet(raw):
            rt_elements = []
            current_group = []
            current_indent = 0

            while i < len(lines):
                raw_l = lines[i]
                if is_sub_bullet(raw_l):
                    # Flush any pending top-level group
                    if current_group and current_indent == 0:
                        rt_elements.append({
                            'type': 'rich_text_list',
                            'style': 'bullet',
                            'indent': 0,
                            'elements': current_group
                        })
                        current_group = []
                    current_indent = 1
                    bullet_text = raw_l.strip()[2:]
                    current_group.append({
                        'type': 'rich_text_section',
                        'elements': parse_inline(bullet_text)
                    })
                    i += 1
                elif is_bullet(raw_l) and not is_sub_bullet(raw_l):
                    # Flush any pending sub-level group
                    if current_group and current_indent == 1:
                        rt_elements.append({
                            'type': 'rich_text_list',
                            'style': 'bullet',
                            'indent': 1,
                            'elements': current_group
                        })
                        current_group = []
                    current_indent = 0
                    bullet_text = raw_l.strip()[2:]
                    current_group.append({
                        'type': 'rich_text_section',
                        'elements': parse_inline(bullet_text)
                    })
                    i += 1
                else:
                    break

            # Flush remaining group
            if current_group:
                rt_elements.append({
                    'type': 'rich_text_list',
                    'style': 'bullet',
                    'indent': current_indent,
                    'elements': current_group
                })

            blocks.append({'type': 'rich_text', 'elements': rt_elements})
            continue

        # Numbered list (Today's Focus)
        if is_numbered(raw):
            ordered_items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                m = re.match(r'^\d+\. (.*)', lines[i])
                ordered_items.append({
                    'type': 'rich_text_section',
                    'elements': parse_inline(m.group(1))
                })
                i += 1
            blocks.append({
                'type': 'rich_text',
                'elements': [{
                    'type': 'rich_text_list',
                    'style': 'ordered',
                    'indent': 0,
                    'elements': ordered_items
                }]
            })
            continue

        # Section header or plain text
        elements = parse_inline(line)
        blocks.append({
            'type': 'rich_text',
            'elements': [{'type': 'rich_text_section', 'elements': elements}]
        })
        i += 1

    return blocks


def slack_post(channel, text, env):
    # Post via Composio using Ben's connected account (posts as Ben, not as bot)
    api_key = env['COMPOSIO_API_KEY']
    blocks = text_to_blocks(text)
    payload = json.dumps({
        'connectedAccountId': 'b02db1f4-9d22-416c-bb78-bdb8c1bc6bb4',
        'input': {
            'channel': channel,
            'text': text,  # fallback for notifications
            'blocks': json.dumps(blocks)
        }
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

Format using this exact syntax (it gets converted to Slack Block Kit):
- *bold* for section headers and person names only
- Top-level bullets: "- item"
- Sub-bullets for grouping related details: "  - sub-item" (exactly 2 spaces then dash)
- Numbered list for Today's Focus only

Output:
Good morning team -- here's where we stand.

[2-4 sentence executive summary. A punchy paragraph that captures the overall state of the project right now -- what's the momentum, what's the biggest outstanding concern, what's the theme of today. Should read like something a founder would say to kick off a standup. No bullets here, just prose. Write it like a human, not a bot.]

*{period_label}*

*[Person Name]*
- [top-level area of work or theme]
  - [specific detail or sub-item]
  - [another detail]
- [next area of work]

*NEEDS ATTENTION*
- [unresolved issue]
  - [specific detail: build number, what fails, what's blocked]

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
