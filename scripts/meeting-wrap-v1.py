#!/usr/bin/env python3
"""
Meeting Wrap v1 - Fathom meeting -> Slack post as Ben via Composio
- Key Takeaways: Fathom summary sections used verbatim (no AI rewriting)
- Action Items: extracted and grouped from transcript via Gemini
- Posts to #meeting-notes as Ben. Ben can edit/delete in Slack if needed.
"""
import ast, json, re, subprocess, sys, urllib.request

ENV_FILE = '/root/.openclaw/.env'
BRIEFING_FILE = '/root/.openclaw/workspace/logs/meeting-wrap-briefing.txt'
FATHOM_CLIENT = '/root/.openclaw/workspace/core/fathom/client.py'
TELEGRAM_TOPIC = '2122'
TELEGRAM_CLIENT = '/root/.openclaw/workspace/core/integrations/telegram.py'
MEETING_NOTES_CHANNEL = 'C09J78SH2FM'
COMPOSIO_ACCOUNT_ID = 'b02db1f4-9d22-416c-bb78-bdb8c1bc6bb4'

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

def openrouter_complete(prompt, api_key):
    payload = json.dumps({
        'model': 'google/gemini-2.5-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 4000,
    }).encode()
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read())
        return result['choices'][0]['message']['content']

def parse_inline(text):
    """Parse *bold* and [text](url) into rich_text elements."""
    elements = []
    # Tokenize: split on bold markers and markdown links
    pattern = r'(\*[^*]+\*|\[[^\]]+\]\([^)]+\))'
    parts = re.split(pattern, text)
    for part in parts:
        if not part:
            continue
        bold_m = re.match(r'^\*([^*]+)\*$', part)
        link_m = re.match(r'^\[([^\]]+)\]\(([^)]+)\)$', part)
        if bold_m:
            elements.append({'type': 'text', 'text': bold_m.group(1), 'style': {'bold': True}})
        elif link_m:
            elements.append({'type': 'link', 'url': link_m.group(2), 'text': link_m.group(1)})
        else:
            elements.append({'type': 'text', 'text': part})
    return elements if elements else [{'type': 'text', 'text': text}]

def text_to_blocks(text):
    """Convert meeting briefing text to Slack Block Kit blocks."""
    blocks = []
    lines = text.strip().splitlines()
    i = 0
    spacer = {'type': 'section', 'text': {'type': 'mrkdwn', 'text': ' '}}

    def is_bullet(line):
        return re.match(r'^- ', line)

    def is_sub_bullet(line):
        return re.match(r'^  - ', line)

    def add_spacer():
        if blocks and blocks[-1] != spacer:
            blocks.append(spacer)

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            add_spacer()
            i += 1
            continue

        # Bullet list (top-level and sub-bullets)
        if is_bullet(raw) and not is_sub_bullet(raw):
            rt_elements = []
            current_group = []
            current_indent = 0

            while i < len(lines):
                raw_l = lines[i]
                if is_sub_bullet(raw_l):
                    if current_group and current_indent == 0:
                        rt_elements.append({
                            'type': 'rich_text_list', 'style': 'bullet', 'indent': 0,
                            'elements': current_group
                        })
                        current_group = []
                    current_indent = 1
                    current_group.append({
                        'type': 'rich_text_section',
                        'elements': parse_inline(raw_l.strip()[2:])
                    })
                    i += 1
                elif is_bullet(raw_l) and not is_sub_bullet(raw_l):
                    if current_group and current_indent == 1:
                        rt_elements.append({
                            'type': 'rich_text_list', 'style': 'bullet', 'indent': 1,
                            'elements': current_group
                        })
                        current_group = []
                    current_indent = 0
                    current_group.append({
                        'type': 'rich_text_section',
                        'elements': parse_inline(raw_l.strip()[2:])
                    })
                    i += 1
                else:
                    break

            if current_group:
                rt_elements.append({
                    'type': 'rich_text_list', 'style': 'bullet', 'indent': current_indent,
                    'elements': current_group
                })
            blocks.append({'type': 'rich_text', 'elements': rt_elements})
            continue

        # Plain text / section header (handles inline links and bold)
        elements = parse_inline(line)
        blocks.append({
            'type': 'rich_text',
            'elements': [{'type': 'rich_text_section', 'elements': elements}]
        })
        i += 1

    return blocks

def slack_post(channel, text, env):
    """Post to Slack as Ben via Composio."""
    api_key = env['COMPOSIO_API_KEY']
    blocks = text_to_blocks(text)
    payload = json.dumps({
        'connectedAccountId': COMPOSIO_ACCOUNT_ID,
        'input': {
            'channel': channel,
            'text': text,
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
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read())
        if not result.get('data'):
            raise Exception('Composio post failed: ' + str(result))
        return result

def parse_summary(summary_raw):
    """Parse Fathom summary output into structured sections."""
    data = ast.literal_eval(summary_raw)
    markdown = data.get('markdown_formatted', '')
    sections = []
    parts = re.split(r'(###\s+\[.+?\]\(.+?\))', markdown)
    for i, part in enumerate(parts):
        if re.match(r'###\s+\[', part):
            title_link = part[4:].strip()  # strip '### '
            body = parts[i + 1].strip() if i + 1 < len(parts) else ''
            sections.append((title_link, body))
    return sections

def parse_meeting_header(meeting_raw):
    """Extract title, date, recording URL, share URL from meeting output."""
    info = {}
    for line in meeting_raw.splitlines():
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
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%B %-d, %Y')
    except Exception:
        return date_str

def extract_duration(today_output, meeting_id):
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

    sections = parse_summary(summary_raw)
    header = parse_meeting_header(meeting_raw)

    if not today_output:
        today_output = fathom(['today'])
    duration = extract_duration(today_output, meeting_id)

    date_formatted = format_date(header.get('date', ''))
    recording_url = header.get('url', '')
    share_url = header.get('share_url', '')

    # Build Key Takeaways verbatim from Fathom summary
    # Strip **double** bold (from Fathom markdown) -- *single* bold is handled by parse_inline
    takeaways_lines = []
    for title_link, body in sections:
        body = re.sub(r'\*\*(.+?)\*\*', r'\1', body)
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
- Rewrite each item as a clean, professional third-person action item. Do NOT copy spoken language verbatim.
- Person order: Steven -> Bilal -> Ben -> Cassandra
- Tram (Tram Lee) works under Steven -- her action items go under Steven's section. Do NOT create a Tram section.
- Only create sections for active team members. New hires not yet started (Ian, Chris Miller, Parry) appear inside other people's items if relevant, not their own section.
- No emojis. No markdown ## or ### headers. No em dashes. No asterisks or bold markers of any kind.
- Action items use - bullets
- *Person Name* for person name headers (single asterisks for Slack bold)

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
    # Normalize **double** to *single* bold
    action_items = re.sub(r'\*\*(.+?)\*\*', r'*\1*', action_items)
    # Remove N/A sections
    action_items = re.sub(r'\*[^*\n]+\*\s*\nN/A[^\n]*\n*', '', action_items).strip()

    # Assemble final briefing
    lines = [
        f'*{header.get("title", "FAM POC Standup")} - {date_formatted}*',
        '',
        f'[VIEW RECORDING - {duration} mins]({recording_url}) · [Share Link]({share_url})',
        '',
        '*Key Takeaways*',
        '',
    ]
    lines.extend(takeaways_lines)
    lines.append('*Action Items* @channel')
    lines.append('')
    lines.append(action_items)

    briefing = '\n'.join(lines)

    with open(BRIEFING_FILE, 'w') as f:
        f.write(briefing)

    print('Posting to #meeting-notes...', flush=True)
    slack_post(MEETING_NOTES_CHANNEL, briefing, env)
    print('Posted.', flush=True)

    subprocess.run([
        'python3', TELEGRAM_CLIENT,
        '--topic', TELEGRAM_TOPIC,
        f'Meeting wrap posted to #meeting-notes. Edit there if anything needs adjusting.'
    ], capture_output=True)

if __name__ == '__main__':
    main()
