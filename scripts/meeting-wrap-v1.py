#!/usr/bin/env python3
"""
Meeting Wrap v1 - Fathom meeting -> formatted Slack briefing
- Key Takeaways: Fathom summary sections used verbatim (no AI rewriting)
- Action Items: extracted and grouped from transcript via Gemini
Ben pastes the output into Slack himself -- this script never posts.
"""
import ast, json, re, subprocess, sys, urllib.request

ENV_FILE = '/root/.openclaw/.env'
BRIEFING_FILE = '/root/.openclaw/workspace/logs/meeting-wrap-briefing.txt'
FATHOM_CLIENT = '/root/.openclaw/workspace/core/fathom/client.py'
TELEGRAM_TOPIC = '2122'
TELEGRAM_CLIENT = '/root/.openclaw/workspace/core/integrations/telegram.py'

def load_env():
    env = {}
    for line in open(ENV_FILE).read().splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
    return env

def fathom(args, timeout=60):
    result = subprocess.run(
        ['python3', FATHOM_CLIENT] + args,
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        raise Exception(f'Fathom error: {result.stderr}')
    return result.stdout.strip()

def slack_dm(user_id, text, token):
    """Send a DM to a Slack user via the bot token."""
    # Open DM channel
    payload = json.dumps({'users': user_id}).encode()
    req = urllib.request.Request(
        'https://slack.com/api/conversations.open',
        data=payload,
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        channel_id = json.loads(r.read())['channel']['id']

    # Send in chunks (Slack text limit ~40000 chars, but DMs render better in pieces)
    chunk_size = 3000
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    for chunk in chunks:
        payload = json.dumps({'channel': channel_id, 'text': chunk}).encode()
        req = urllib.request.Request(
            'https://slack.com/api/chat.postMessage',
            data=payload,
            headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            json.loads(r.read())

def openrouter_complete(prompt, api_key):
    payload = json.dumps({
        'model': 'google/gemini-2.5-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 4000,
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

def parse_summary(summary_raw):
    """Parse Fathom summary output into structured sections."""
    # Fathom returns a Python dict repr -- eval it safely
    data = ast.literal_eval(summary_raw)
    markdown = data.get('markdown_formatted', '')

    sections = []
    # Split on ### headers
    parts = re.split(r'(###\s+\[.+?\]\(.+?\))', markdown)
    for i, part in enumerate(parts):
        if re.match(r'###\s+\[', part):
            title_link = part[4:].strip()  # strip '### '
            body = parts[i + 1].strip() if i + 1 < len(parts) else ''
            sections.append((title_link, body))
    return sections

def parse_meeting_header(meeting_raw):
    """Extract title, date, recording URL, share URL, duration from meeting output."""
    lines = meeting_raw.splitlines()
    info = {}
    for line in lines:
        if line.startswith('Title:'):
            info['title'] = line.split(':', 1)[1].strip()
        elif line.startswith('Date:'):
            info['date'] = line.split(':', 1)[1].strip()
        elif line.startswith('URL:'):
            info['url'] = line.split(':', 1)[1].strip()
        elif line.startswith('Share URL:'):
            info['share_url'] = line.split(':', 1)[1].strip()
    return info

def format_date(date_str):
    """Convert 2026-04-16 to April 16, 2026."""
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%B %-d, %Y')
    except Exception:
        return date_str

def extract_duration(today_output, meeting_id):
    """Pull duration from today's meeting list output."""
    m = re.search(rf'\[{meeting_id}\].*?\((\d+) min\)', today_output)
    return m.group(1) if m else '?'

def main():
    env = load_env()
    or_key = env['OPENROUTER_API_KEY']

    # Get meeting ID from arg or use today's latest
    today_output = ''
    if len(sys.argv) > 1:
        meeting_id = sys.argv[1]
        print(f'Using meeting ID: {meeting_id}', flush=True)
    else:
        print("Finding today's meeting...", flush=True)
        today_output = fathom(['today'])
        matches = re.findall(r'\[(\d+)\]', today_output)
        if not matches:
            print('No meetings found today. Pass a meeting ID as an argument.')
            return
        meeting_id = matches[-1]
        print(today_output, flush=True)

    print(f'Pulling summary for {meeting_id}...', flush=True)
    summary_raw = fathom(['summary', meeting_id])

    print('Pulling transcript...', flush=True)
    meeting_raw = fathom(['meeting', meeting_id], timeout=90)

    # Parse summary sections verbatim
    sections = parse_summary(summary_raw)
    header = parse_meeting_header(meeting_raw)

    if not today_output:
        # Need duration -- pull from meeting list for the given date
        today_output = fathom(['today'])
    duration = extract_duration(today_output, meeting_id)

    date_formatted = format_date(header.get('date', ''))
    recording_url = header.get('url', '')
    share_url = header.get('share_url', '')

    # Build Key Takeaways block verbatim from Fathom summary
    # Normalize **bold** -> *bold* for Slack mrkdwn compatibility
    takeaways_lines = []
    for title_link, body in sections:
        body = re.sub(r'\*\*(.+?)\*\*', r'*\1*', body)
        takeaways_lines.append(title_link)
        takeaways_lines.append(body)
        takeaways_lines.append('')

    # Extract action items from transcript via AI
    action_items_prompt = f"""Extract and group all action items from this meeting transcript.

TRANSCRIPT:
{meeting_raw}

Rules:
- Extract explicit commitments and next steps only -- things someone said they would do
- Group by person, then by category within each person (e.g. Bug Fixes:, Backend:, Animations:, Testing:)
- Rewrite each item as a clean, professional third-person action item. Do NOT copy spoken language verbatim -- rephrase "I'm going to..." / "you should..." / "send you..." into proper action items (e.g. "Send Ben the updated avatar preview files")
- Person order: Steven -> Bilal -> Ben -> Cassandra
- Tram (Tram Lee) works under Steven -- her action items go under Steven's section. Do NOT create a Tram section.
- Only create sections for active team members. New hires not yet started (Ian, Chris Miller, Parry) go inside other people's items if relevant (e.g. "Add Ian to GitHub repos" under Steven), not their own section.
- No emojis. No markdown ## or ### headers. No em dashes. Professional tone.
- Use *Person Name* for bold person names (Slack mrkdwn). Never use **double asterisks**.
- Action items use - bullets

Output format (no intro, no outro -- just the action items):

*[Person Name]*
[Category]:
- [action item]
- [action item]

[Category]:
- [action item]

*[Next Person]*
[Category]:
- [action item]"""

    print('Extracting action items from transcript...', flush=True)
    action_items = openrouter_complete(action_items_prompt, or_key)
    # Normalize any **bold** that slipped through
    action_items = re.sub(r'\*\*(.+?)\*\*', r'*\1*', action_items)
    # Remove any person sections with no real items (e.g. "N/A" or empty)
    action_items = re.sub(
        r'\*[^*]+\*\s*\n+N/A[^\n]*\n*',
        '',
        action_items
    ).strip()

    # Assemble final briefing
    lines = [
        f'{header.get("title", "FAM POC Standup")} - {date_formatted}',
        '',
        f'[VIEW RECORDING - {duration} mins]({recording_url}) · [Share Link]({share_url})',
        '',
        'Key Takeaways',
        '',
    ]
    lines.extend(takeaways_lines)
    lines.append('Action Items @channel')
    lines.append('')
    lines.append(action_items)

    briefing = '\n'.join(lines)

    with open(BRIEFING_FILE, 'w') as f:
        f.write(briefing)

    print('\n' + '=' * 60, flush=True)
    print(briefing, flush=True)
    print('=' * 60, flush=True)
    print(f'\nSaved to {BRIEFING_FILE}', flush=True)
    print('Sending to Telegram...', flush=True)

    # Send full briefing to Telegram topic 2122 for Ben to review before posting
    subprocess.run([
        'python3', TELEGRAM_CLIENT,
        '--topic', TELEGRAM_TOPIC,
        f'*Meeting wrap ready -- review below, then paste into #meeting-notes*'
    ], capture_output=True)
    subprocess.run([
        'python3', TELEGRAM_CLIENT,
        '--topic', TELEGRAM_TOPIC,
        briefing
    ], capture_output=True)

    print('Done. Briefing sent to Telegram topic 2122.', flush=True)

if __name__ == '__main__':
    main()
