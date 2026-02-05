#!/usr/bin/env python3
"""
Email Newsletter Monitor v3 - Extract individual stories from Ben's AI/creator newsletters
Parses full newsletter content into separate stories with descriptions and article links
"""
import sqlite3
import json
import re
import requests
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
LOG_FILE = Path("/root/clawd/logs/email-newsletters.log")

MCP_URL = 'https://backend.composio.dev/tool_router/trs_r19DmEN65WU9/mcp'
API_KEY = 'REDACTED_COMPOSIO_MCP_KEY'
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/event-stream',
    'x-api-key': API_KEY
}

# AI/Creator newsletters we care about
NEWSLETTER_WHITELIST = {
    'therundown': 'The Rundown AI',
    'rundownai': 'The Rundown AI',
    'aiforwork': 'AI For Work',
    'deepview': 'AI For Work',
    'unwindai': 'Unwind AI',
    'whatsupinai': "What's Up in AI",
    'dailybite@mail.beehiiv': 'Snack Prompt',
    'snackprompt': 'Snack Prompt',
    'socialgrowthengineer': 'Social Growth Engineers',
    'wavy@mail.beehiiv': 'Kallaway',
    'kallaway': 'Kallaway',
    'unicorne@mail.beehiiv': 'Marc Lou',
    'marclou': 'Marc Lou',
    'hypefury': 'Hypefury',
    'lenny': "Lenny's Newsletter",
    'tinylaunch': 'TinyLaunch',
    'tinylog': 'TinyLaunch',
    'ideabrowser': 'Ideabrowser',
    'bensbites': "Ben's Bites",
    'superhuman': 'Superhuman AI',
    'tldr': 'TLDR',
    'theneuron': 'The Neuron',
    'producthunt': 'Product Hunt',
}

SENDER_BLACKLIST = [
    'dailybones', 'luckytrader', 'circleboom', 'noreply-apps-scripts',
]

# URLs to skip when extracting article links
SKIP_URL_PATTERNS = [
    'unsubscribe', 'beehiiv.com/cdn', 'tracking', 'click.', 'manage',
    'preferences', 'mailchimp', 'list-manage', 'mailto', 'beacon',
    'pixel', 'open.substack', 'cdn-cgi', 'fonts.', 'static.',
    '/subscribe', '/signup', '/sign-up', 'typeform.com', 'email-protection',
    'youtube.com/watch', 'podcasts.apple', 'spotify.com/show',
    'innovatingwithai.com', 'cal.com', 'forms.gle', 'google.com/forms',
    'viewform', 'concentrix', 'tally.so',
]

# Patterns that indicate sponsored/ad content to skip
AD_PATTERNS = [
    r'(?i)sponsored\s+by', r'(?i)presented\s+by', r'(?i)together\s+with',
    r'(?i)brought\s+to\s+you\s+by', r'(?i)partner\s+content',
]


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


def ensure_tables():
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    # Per-newsletter record (tracks which emails we've processed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            sender_name TEXT,
            sender_email TEXT,
            content TEXT,
            topics TEXT,
            links TEXT,
            relevance_score INTEGER,
            email_id TEXT UNIQUE,
            created_at TEXT
        )
    ''')
    # Individual stories extracted from newsletters
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS newsletter_stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT,
            description TEXT,
            article_url TEXT,
            source_name TEXT,
            source_subject TEXT,
            email_id TEXT,
            relevance_score INTEGER,
            created_at TEXT,
            UNIQUE(headline, email_id)
        )
    ''')
    conn.commit()
    conn.close()


def composio_call(tools):
    try:
        response = requests.post(MCP_URL, headers=HEADERS, json={
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'params': {
                'name': 'COMPOSIO_MULTI_EXECUTE_TOOL',
                'arguments': {'tools': tools}
            },
            'id': 1
        }, timeout=60)

        for line in response.text.split('\n'):
            if line.startswith('data:'):
                data = json.loads(line[5:])
                text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if text:
                    return json.loads(text)
        return None
    except Exception as e:
        log(f"Composio call error: {e}")
        return None


def is_whitelisted(sender_email):
    sender_lower = sender_email.lower()
    for fragment in NEWSLETTER_WHITELIST:
        if fragment in sender_lower:
            return True
    return False


def is_blacklisted(sender_email):
    sender_lower = sender_email.lower()
    for fragment in SENDER_BLACKLIST:
        if fragment in sender_lower:
            return True
    return False


def get_sender_name(sender_email):
    sender_lower = sender_email.lower()
    for fragment, name in NEWSLETTER_WHITELIST.items():
        if fragment in sender_lower:
            return name
    return sender_email.split('<')[0].strip().strip('"')


def is_good_url(url):
    """Check if a URL is a real article link, not tracking/nav/ad"""
    url_lower = url.lower()
    if any(skip in url_lower for skip in SKIP_URL_PATTERNS):
        return False
    if len(url) < 15:
        return False
    return True


def clean_url(url):
    """Strip tracking params from URL"""
    url = url.rstrip('.,;:)>')
    # Remove common tracking params but keep the base URL
    if '?' in url:
        base = url.split('?')[0]
        params = url.split('?')[1]
        # Keep params that look like content identifiers
        keep_params = []
        for p in params.split('&'):
            key = p.split('=')[0].lower()
            if key in ('id', 'v', 'p', 'page', 'slug', 'ref'):
                keep_params.append(p)
        if keep_params:
            return base + '?' + '&'.join(keep_params)
        return base
    return url


def is_ad_section(text):
    """Check if text block is a sponsored/ad section"""
    for pattern in AD_PATTERNS:
        if re.search(pattern, text[:200]):
            return True
    return False


def extract_stories_from_newsletter(sender_name, subject, message_text):
    """Parse a newsletter's full text into individual stories with headlines, descriptions, and links"""
    stories = []

    if not message_text or len(message_text) < 100:
        return stories

    # Normalize line endings (Composio returns \r\n)
    message_text = message_text.replace('\r\n', '\n')

    # Split on horizontal rules (----------)
    sections = re.split(r'\n-{3,}\n', message_text)

    for section in sections:
        section = section.strip()
        if len(section) < 80:
            continue

        # Skip ad/sponsored sections
        if is_ad_section(section):
            continue

        # Skip sections that are just nav/footer
        section_lower = section.lower()
        if any(skip in section_lower[:100] for skip in [
            'read online', 'sign up', 'advertise', 'unsubscribe',
            'view this post', 'manage preferences', 'you are reading'
        ]):
            continue

        headline = None
        description = None
        article_url = None

        # Pattern 1: #### **[_Title_](url)** (Rundown AI style)
        title_link = re.search(
            r'#{3,6}\s*[\*_]*\[([^\]]+)\]\((https?://[^\)]+)\)',
            section
        )
        if title_link:
            headline = title_link.group(1).strip('_* ')
            candidate_url = title_link.group(2)
            if is_good_url(candidate_url):
                article_url = clean_url(candidate_url)

        # Pattern 2: **[Title](url)** without header
        if not headline:
            bold_link = re.search(
                r'\*\*\[([^\]]{10,80})\]\((https?://[^\)]+)\)\*\*',
                section
            )
            if bold_link:
                headline = bold_link.group(1).strip('_* ')
                candidate_url = bold_link.group(2)
                if is_good_url(candidate_url):
                    article_url = clean_url(candidate_url)

        # Pattern 3: **Bold headline** (no link)
        if not headline:
            bold_match = re.search(r'\*\*([^*]{10,100})\*\*', section)
            if bold_match:
                candidate = bold_match.group(1).strip()
                skip_phrases = ['the rundown:', 'the details:', 'why it matters:',
                                'good morning', 'step-by-step:', 'pro tip:',
                                'read online', 'sign up', 'advertise',
                                'in today', 'the deep view:']
                if candidate.lower() not in skip_phrases and not candidate.lower().startswith('in today'):
                    headline = candidate

        if not headline:
            continue

        # Clean headline
        headline = re.sub(r'[_*#\[\]]', '', headline).strip()
        headline = re.sub(r'^[\s\-:]+', '', headline).strip()
        # Remove emoji at start
        headline = re.sub(r'^[\U0001f000-\U0001ffff\u2600-\u27ff\ufe0f\s]+', '', headline).strip()
        if len(headline) < 8 or len(headline) > 150:
            continue

        # Skip generic/nav headlines and non-headline text
        skip_headlines = ['trending ai tools', 'everything else in ai', 'community ai workflows',
                         'highlights:', 'news, guides', 'share the rundown', 'in today',
                         'good morning', 'welcome back', 'growth tips', 'growth notes',
                         'growth news', 'biggest takeaways', 'detailed workflow', 'whats cookin',
                         'latest developments', 'top ai highlights', 'key takeaway',
                         'how i ai:', 'this week on', 'workflow walkthrough',
                         'view in browser', 'view online']
        if any(skip in headline.lower() for skip in skip_headlines):
            continue
        # Skip if headline looks like a broken URL fragment
        if headline.startswith('http') or headline.startswith('vas(') or '://' in headline:
            continue

        # Extract article URL if not found yet
        if not article_url:
            links = re.findall(r'\[([^\]]*)\]\((https?://[^\)]+)\)', section)
            for link_text, url in links:
                if is_good_url(url):
                    article_url = clean_url(url)
                    break

        # Extract description
        # Pattern: "The Rundown:" or "The Deep View:" style
        desc_match = re.search(
            r'\*\*(?:The )?(?:Rundown|Deep View|Details):\s*\*\*(.*?)(?:\n\n|\*\*(?:The )?(?:details|why it matters))',
            section, re.DOTALL | re.IGNORECASE
        )
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            # Find first substantial paragraph that's not an image/header/link
            paragraphs = section.split('\n\n')
            for p in paragraphs:
                p_stripped = p.strip()
                if any(skip in p_stripped.lower() for skip in [
                    'view image:', 'caption:', 'follow image', '###', '######',
                    'read online', '---'
                ]):
                    continue
                # Clean it
                p_clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', p_stripped)
                p_clean = re.sub(r'\*{1,2}', '', p_clean)
                p_clean = re.sub(r'https?://\S+', '', p_clean)
                p_clean = re.sub(r'\s+', ' ', p_clean).strip()
                if len(p_clean) > 50 and not p_clean.startswith('#'):
                    description = p_clean
                    break

        # Clean description
        if description:
            description = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', description)
            description = re.sub(r'\*{1,2}', '', description)
            description = re.sub(r'https?://\S+', '', description)
            description = re.sub(r'\s+', ' ', description).strip()
            description = description[:350]

        stories.append({
            'headline': headline,
            'description': description or '',
            'article_url': article_url or '',
            'source_name': sender_name,
            'source_subject': subject,
        })

    # Fallback for newsletters that don't split on --- (Unwind AI, Snack Prompt, etc.)
    if len(stories) < 2:
        fallback = extract_stories_list_format(sender_name, subject, message_text)
        if len(fallback) > len(stories):
            stories = fallback

    return stories


def extract_stories_list_format(sender_name, subject, message_text):
    """Extract stories from list-format newsletters (numbered items, bullet points)"""
    stories = []

    # Pattern: "1. Title" or "* Title" or "- Title" followed by description
    # Also handles: "Headline\nDescription\nURL" blocks
    lines = message_text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for numbered list items or bold headlines
        match = re.match(r'^(?:\d+[\.\)]\s*|\*\s+|\-\s+)?\*?\*?(.{15,100})\*?\*?\s*$', line)
        if match and not any(skip in line.lower() for skip in ['view image', 'caption:', 'follow image',
                                                                 'unsubscribe', 'read online']):
            headline = match.group(1).strip('*_- ')
            headline = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', headline)

            # Gather description from following lines
            desc_lines = []
            url = None
            j = i + 1
            while j < min(i + 8, len(lines)):
                next_line = lines[j].strip()
                if not next_line or next_line.startswith('---'):
                    break
                # Extract URL
                url_match = re.search(r'(https?://[^\s\)>\]]+)', next_line)
                if url_match and not url and is_good_url(url_match.group(1)):
                    url = clean_url(url_match.group(1))
                # Add to description
                clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', next_line)
                clean_line = re.sub(r'\*{1,2}', '', clean_line)
                clean_line = re.sub(r'https?://\S+', '', clean_line).strip()
                if len(clean_line) > 10:
                    desc_lines.append(clean_line)
                j += 1

            # Also check for URL in headline itself
            if not url:
                url_match = re.search(r'\((https?://[^\)]+)\)', line)
                if url_match and is_good_url(url_match.group(1)):
                    url = clean_url(url_match.group(1))

            description = ' '.join(desc_lines)[:300]

            # Apply same skip filters as main extractor
            skip_headlines = ['trending ai tools', 'everything else in ai', 'community ai workflows',
                             'highlights:', 'news, guides', 'share the rundown', 'in today',
                             'good morning', 'welcome back', 'growth tips', 'growth notes',
                             'growth news', 'biggest takeaways', 'detailed workflow', 'whats cookin',
                             'latest developments', 'top ai highlights', 'key takeaway',
                             'how i ai:', 'this week on', 'workflow walkthrough',
                             'view in browser', 'view online']
            headline_lower = headline.lower()
            if any(skip in headline_lower for skip in skip_headlines):
                i += 1
                continue
            if headline.startswith('http') or '://' in headline:
                i += 1
                continue

            if len(headline) >= 10 and not is_ad_section(headline + ' ' + description):
                stories.append({
                    'headline': headline,
                    'description': description,
                    'article_url': url or '',
                    'source_name': sender_name,
                    'source_subject': subject,
                })

        i += 1

    return stories[:10]  # Cap at 10 stories per newsletter


def score_story_relevance(headline, description):
    """Score a story's relevance to Ben's niche"""
    text = f"{headline} {description}".lower()
    score = 0

    high_value = ['ai', 'automation', 'agent', 'vibecod', 'no-code', 'nocode',
                  'claude', 'mcp', 'cursor', 'build', 'ship', 'launch', 'tool',
                  'anthropic', 'openai', 'xcode', 'codex', 'creator', 'content']
    for kw in high_value:
        if kw in text:
            score += 15

    medium_value = ['llm', 'gpt', 'gemini', 'deepseek', 'saas', 'startup',
                    'founder', 'indie', 'solopreneur', 'developer', 'software',
                    'api', 'app', 'product', 'revenue', 'growth', 'video',
                    'elevenlabs', 'copilot', 'midjourney', 'model']
    for kw in medium_value:
        if kw in text:
            score += 8

    return min(score, 100)


def fetch_newsletter_emails():
    """Fetch recent newsletter emails with full content, using multiple targeted queries for reliability"""
    # Multiple smaller queries are more reliable than one huge OR query
    queries = [
        'newer_than:2d from:therundown',
        'newer_than:2d from:unwindai',
        'newer_than:2d from:aiforwork',
        'newer_than:2d from:deepview',
        'newer_than:2d (from:beehiiv OR from:substack)',
        'newer_than:2d (from:newsletter OR from:hypefury OR from:lenny)',
    ]

    all_messages = []
    seen_ids = set()

    for query in queries:
        result = composio_call([{
            'tool_slug': 'GMAIL_FETCH_EMAILS',
            'arguments': {
                'max_results': 10,
                'query': query,
                'include_payload': True,
                'verbose': True
            }
        }])

        if not result or not result.get('successful'):
            continue

        results = result.get('data', {}).get('results', [])
        if not results:
            continue

        resp = results[0].get('response', {})
        messages = resp.get('data', {}).get('messages', resp.get('data_preview', {}).get('messages', []))

        for m in messages:
            if not isinstance(m, dict):
                continue
            mid = m.get('messageId', m.get('id', ''))
            if mid and mid not in seen_ids:
                seen_ids.add(mid)
                all_messages.append(m)

    log(f"Fetched {len(all_messages)} unique newsletter emails across {len(queries)} queries")
    return all_messages


def process_messages(messages):
    """Process emails: extract stories from each newsletter and save"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    saved_emails = 0
    saved_stories = 0
    skipped_blacklist = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    for msg in messages:
        try:
            email_id = msg.get('messageId', msg.get('id', ''))
            subject = msg.get('subject', '')
            sender_raw = msg.get('sender', msg.get('from', ''))
            message_text = msg.get('messageText', '')

            if is_blacklisted(sender_raw):
                skipped_blacklist += 1
                continue

            sender_name = get_sender_name(sender_raw)

            # Save the newsletter record (tracks what we've processed)
            all_links = re.findall(r'https?://[^\s\)>\]\*]+', message_text or '')
            good_links = [clean_url(u) for u in all_links if is_good_url(u)][:10]

            cursor.execute('''
                INSERT OR IGNORE INTO newsletter_topics
                (subject, sender_name, sender_email, content, topics, links, relevance_score, email_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (subject, sender_name, sender_raw,
                  (message_text or '')[:5000],  # Store more content for reference
                  '[]', json.dumps(good_links), 50, email_id, now))

            if cursor.rowcount > 0:
                saved_emails += 1

            # Extract individual stories
            stories = extract_stories_from_newsletter(sender_name, subject, message_text or '')

            for story in stories:
                relevance = score_story_relevance(story['headline'], story['description'])
                if relevance >= 15:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO newsletter_stories
                            (headline, description, article_url, source_name, source_subject,
                             email_id, relevance_score, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (story['headline'], story['description'], story['article_url'],
                              story['source_name'], story['source_subject'],
                              email_id, relevance, now))
                        if cursor.rowcount > 0:
                            saved_stories += 1
                    except Exception:
                        pass

            log(f"  {sender_name}: {subject[:50]} -> {len(stories)} stories")

        except Exception as e:
            log(f"Process error: {e}")

    conn.commit()
    conn.close()
    log(f"Saved {saved_emails} emails, {saved_stories} new stories | Skipped: {skipped_blacklist} blacklisted")
    return saved_stories


def get_stories_for_briefing(limit=12):
    """Get top stories for the morning briefing"""
    conn = sqlite3.connect(MEMORY_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT headline, description, article_url, source_name, relevance_score
        FROM newsletter_stories
        WHERE created_at > datetime('now', '-36 hours')
        ORDER BY relevance_score DESC, created_at DESC
        LIMIT ?
    ''', (limit,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def main():
    log("Newsletter Monitor v3 starting...")
    ensure_tables()

    messages = fetch_newsletter_emails()

    if messages:
        saved = process_messages(messages)
    else:
        log("No newsletter messages found")

    # Show extracted stories
    stories = get_stories_for_briefing(15)
    if stories:
        print(f"\n{'='*70}")
        print(f"NEWSLETTER STORIES ({len(stories)} stories)")
        print(f"{'='*70}")
        for s in stories:
            print(f"\n>> {s['headline']}")
            print(f"   Source: {s['source_name']}")
            if s['description']:
                # Show a meaningful chunk of the description
                print(f"   {s['description'][:300]}")
            if s['article_url']:
                print(f"   {s['article_url']}")
            else:
                print(f"   (no direct link)")
    else:
        print("\nNo stories extracted yet")

    log("Done")


if __name__ == "__main__":
    main()
