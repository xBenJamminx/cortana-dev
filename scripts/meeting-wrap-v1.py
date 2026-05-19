#!/usr/bin/env python3
"""
Meeting Wrap v1 - Fathom meeting -> Telegram review for Ben
- Key Takeaways: Fathom summary sections used verbatim (no AI rewriting)
- Action Items: extracted and grouped from transcript via Gemini
- Sends full briefing to Telegram topic 2122 for Ben to review and paste into Slack himself.
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
    """Parse *bold*, [text](url), and @channel/@here into rich_text elements."""
    elements = []
    pattern = r'(\*[^*]+\*|\[[^\]]+\]\([^)]+\)|@channel|@here)'
    parts = re.split(pattern, text)
    for part in parts:
        if not part:
            continue
        bold_m = re.match(r'^\*([^*]+)\*$', part)
        link_m = re.match(r'^\[([^\]]+)\]\(([^)]+)\)$', part)
        if part == '@channel':
            elements.append({'type': 'broadcast', 'range': 'channel'})
        elif part == '@here':
            elements.append({'type': 'broadcast', 'range': 'here'})
        elif bold_m:
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

def md_link_to_slack(text):
    """Convert [text](url) markdown links to Slack mrkdwn <url|text> format."""
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', text)

def takeaways_to_blocks(title, recording_url, share_url, duration, sections):
    """Build Key Takeaways as compact mrkdwn section blocks (1 block per section)."""
    blocks = []
    spacer = {'type': 'section', 'text': {'type': 'mrkdwn', 'text': ' '}}

    # Header
    blocks.append({
        'type': 'section',
        'text': {'type': 'mrkdwn', 'text': f'*{title}*'}
    })
    blocks.append({
        'type': 'section',
        'text': {'type': 'mrkdwn', 'text': f'<{recording_url}|VIEW RECORDING - {duration} mins> · <{share_url}|Share Link> <!channel>'}
    })
    blocks.append(spacer)
    blocks.append({
        'type': 'section',
        'text': {'type': 'mrkdwn', 'text': '*Key Takeaways*'}
    })
    blocks.append(spacer)

    for title_link, body in sections:
        # Convert [text](url) to <url|text> for mrkdwn
        title_mrkdwn = md_link_to_slack(title_link)
        body_mrkdwn = re.sub(r'\*\*(.+?)\*\*', r'*\1*', body)  # normalize bold
        # Replace indented bullets "  - " with Slack mrkdwn bullets
        body_mrkdwn = re.sub(r'^  - ', '• ', body_mrkdwn, flags=re.MULTILINE)
        blocks.append({
            'type': 'section',
            'text': {'type': 'mrkdwn', 'text': f'{title_mrkdwn}\n{body_mrkdwn}'}
        })
        blocks.append(spacer)

    return blocks

def slack_post(channel, text, env, blocks=None, retries=2):
    """Post to Slack as Ben via Composio. Retries on transient failure."""
    import time
    api_key = env['COMPOSIO_API_KEY']
    if blocks is None:
        blocks = text_to_blocks(text)
    payload = json.dumps({
        'connectedAccountId': COMPOSIO_ACCOUNT_ID,
        'input': {
            'channel': channel,
            'text': text,
            'blocks': json.dumps(blocks)
        }
    }).encode()
    for attempt in range(retries + 1):
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
        data = result.get('data', {})
        ok = data.get('ok') if data else result.get('successful')
        print(f'Composio response (attempt {attempt+1}): successful={result.get("successful")}, ok={ok}, ts={data.get("ts") if data else None}', flush=True)
        if result.get('successful') and ok:
            return result
        if attempt < retries:
            print(f'  Retrying in 3s... error={data.get("error") if data else result.get("error")}', flush=True)
            time.sleep(3)
    raise Exception(f'Composio post failed after {retries+1} attempts: ' + str(result))

def parse_summary(summary_raw):
    """Parse Fathom summary output into structured sections.
    Handles old format (### [title @ ts](url) + body) and Enhanced format (## Key Takeaways bullets)."""
    data = ast.literal_eval(summary_raw)
    markdown = data.get('markdown_formatted', '')
    sections = []

    # Old format: ### [title](url) + body paragraphs
    parts = re.split(r'(###\s+\[.+?\]\(.+?\))', markdown)
    for i, part in enumerate(parts):
        if re.match(r'###\s+\[', part):
            title_link = part[4:].strip()
            body = parts[i + 1].strip() if i + 1 < len(parts) else ''
            body = re.split(r'\n##', body)[0].strip()
            sections.append((title_link, body))
    if sections:
        return sections

    # Enhanced format: use ## Topics sections for rich Key Takeaways
    topics_match = re.search(r'##\s+Topics\s*\n(.*?)(?=\n##\s|\Z)', markdown, re.DOTALL)
    if topics_match:
        for m in re.finditer(r'###\s+(.+?)\n(.*?)(?=\n###\s|\Z)', topics_match.group(1), re.DOTALL):
            topic_name = m.group(1).strip()
            body_raw = m.group(2)
            # Use first timestamp URL as the section link
            first_link = re.search(r'\[.+?\]\((https?://[^)]+)\)', body_raw)
            title_link = f'[{topic_name}]({first_link.group(1)})' if first_link else f'[{topic_name}]'
            # All bullet levels: strip link markup and bold, normalize indent for text_to_blocks
            # Fathom: 2-space=top-level, 6-space=sub, 10-space=sub-sub → map to "- " and "  - "
            body_lines = []
            for line in body_raw.splitlines():
                bm = re.match(r'^( *)-\s', line)
                if bm:
                    indent = len(bm.group(1))
                    text = line.strip()[2:].strip()
                    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
                    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
                    # normalize: base indent is 2, anything deeper → sub-bullet
                    prefix = '  - ' if indent > 2 else '- '
                    body_lines.append(f'{prefix}{text}')
            sections.append((title_link, '\n'.join(body_lines)))
        if sections:
            return sections

    # Fall back: ## Key Takeaways bullets (Enhanced format without Topics)
    kt_match = re.search(r'##\s+Key Takeaways\s*\n(.*?)(?=\n##\s|\Z)', markdown, re.DOTALL)
    if kt_match:
        for m in re.finditer(r'^\s+-\s+(\[.+?\]\(.+?\))\s*$', kt_match.group(1), re.MULTILINE):
            title_link = re.sub(r'\*\*(.+?)\*\*', r'\1', m.group(1).strip())
            sections.append((title_link, ''))

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

def post_to_slack():
    """Phase 2: Post saved briefing to #meeting-notes as Ben after approval.
    Splits into two messages at Action Items to stay under Slack's 50-block limit."""
    import os
    from datetime import date
    env = load_env()
    try:
        with open(BRIEFING_FILE) as f:
            briefing = f.read().strip()
    except FileNotFoundError:
        print(f'Error: No saved briefing at {BRIEFING_FILE}. Run Phase 1 first.')
        return

    # Stale-post guard: briefing must be from today
    today_str = date.today().strftime('%B %-d, %Y')
    if today_str not in briefing[:120]:
        print(f'Error: Saved briefing is not from today ({today_str}). Run Phase 1 first to generate a fresh briefing.')
        subprocess.run([
            'python3', TELEGRAM_CLIENT,
            '--topic', TELEGRAM_TOPIC,
            f'Cannot post: saved briefing is stale (not from today). Run Phase 1 first.'
        ], capture_output=True)
        return

    # Split briefing into Key Takeaways and Action Items sections
    split_marker = '\n*Action Items*'
    if split_marker in briefing:
        part1 = briefing[:briefing.index(split_marker)].strip()
        part2 = briefing[briefing.index(split_marker) + 1:].strip()  # keep the *Action Items* line
    else:
        part1 = briefing
        part2 = None

    print('Posting Key Takeaways to #meeting-notes...', flush=True)
    slack_post(MEETING_NOTES_CHANNEL, part1, env)

    if part2:
        print('Posting Action Items to #meeting-notes...', flush=True)
        slack_post(MEETING_NOTES_CHANNEL, part2, env)

    print('Posted to #meeting-notes.', flush=True)

    subprocess.run([
        'python3', TELEGRAM_CLIENT,
        '--topic', TELEGRAM_TOPIC,
        'Posted to #meeting-notes. Done.'
    ], capture_output=True)


def main():
    # Phase 2: post saved briefing after Ben approves
    if len(sys.argv) > 1 and sys.argv[1] == '--post':
        post_to_slack()
        return

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
        print(today_output, flush=True)
        # Parse all meetings: extract (id, title) pairs
        meeting_entries = re.findall(r'\[(\d+)\]\s+\S+\s+—\s+(.+?)\s+\(', today_output)
        if not meeting_entries:
            # Fallback: just grab IDs
            ids = re.findall(r'\[(\d+)\]', today_output)
            if not ids:
                print('No meetings found today. Pass a meeting ID as an argument.')
                return
            meeting_id = ids[-1]
        else:
            # Prefer FAM POC STANDUP; fall back to last meeting
            fam = [(mid, title) for mid, title in meeting_entries
                   if re.search(r'fam|standup|stand.?up', title, re.IGNORECASE)]
            chosen = fam[0] if fam else meeting_entries[-1]
            meeting_id, chosen_title = chosen
            print(f'Selected meeting: [{meeting_id}] {chosen_title}', flush=True)

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
        if body:
            takeaways_lines.append(body)
        takeaways_lines.append('')

    # Extract action items from transcript via AI
    action_items_prompt = f"""Extract and group all action items from this meeting transcript.

TRANSCRIPT:
{meeting_raw}

Rules:
- Extract explicit commitments and next steps only -- things someone said they would do
- CONSOLIDATE: if multiple mentions refer to the same task, merge them into one item. No duplicates.
- Aim for 3-6 items per person total. Prefer fewer, clearer items over a long redundant list.
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

    title = f'{header.get("title", "FAM POC Standup")} - {date_formatted}'
    action_items_section = '*Action Items*\n\n' + action_items

    # Send briefing to Telegram for Ben's review — NEVER post to Slack directly
    print('Sending briefing to Telegram topic 2122 for review...', flush=True)

    def tg_send(text):
        """Send to Telegram, splitting only if truly over 4096 chars."""
        if len(text) <= 3900:
            subprocess.run(['python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC, text], capture_output=True)
            return
        # Only split at section boundaries if over limit
        chunks, current = [], ''
        for line in text.splitlines():
            if len(current) + len(line) + 1 > 3900:
                if current:
                    subprocess.run(['python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC, current], capture_output=True)
                current = line
            else:
                current = current + '\n' + line if current else line
        if current:
            subprocess.run(['python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC, current], capture_output=True)

    # Split at Action Items boundary — Key Takeaways first, then Action Items
    split_marker = '\n*Action Items*'
    if split_marker in briefing and len(briefing) > 3900:
        tg_send(briefing[:briefing.index(split_marker)].strip())
        tg_send(briefing[briefing.index(split_marker) + 1:].strip())
    else:
        tg_send(briefing)

    subprocess.run([
        'python3', TELEGRAM_CLIENT, '--topic', TELEGRAM_TOPIC,
        "Review the wrap above. Reply 'post it' or 'approved' and I'll post to #meeting-notes as you."
    ], capture_output=True)
    print('Sent to Telegram for review. NOT posted to Slack.', flush=True)

if __name__ == '__main__':
    main()
