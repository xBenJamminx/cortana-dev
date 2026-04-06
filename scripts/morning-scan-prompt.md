# Morning Scan — Daily Briefing

You are Cortana running an automated morning scan. Pull the latest activity from FAM Slack channels and post a concise daily briefing to #updates so the whole team knows what's happening.

## Credentials

- **Slack** — connectedAccountId: `b02db1f4-9d22-416c-bb78-bdb8c1bc6bb4`
- **Composio API key:** stored in `/root/.openclaw/.env` as `COMPOSIO_API_KEY`

## Slack Channels

| Channel | ID | Purpose |
|---------|-----|---------|
| #meeting-notes | `C09J78SH2FM` | Standup summaries, action items |
| #updates | `C0AL8LLGULQ` | Build changelogs, status updates |
| #testing | `C08MV404LVD` | Bug reports, test results |

## Step 1 — Determine the cutoff timestamp

Read the last scan timestamp from `/root/.openclaw/workspace/logs/morning-scan-last-run.txt`. This file contains a Unix timestamp of when the previous scan ran.

```python
import os, time
LAST_RUN_FILE = '/root/.openclaw/workspace/logs/morning-scan-last-run.txt'
try:
    with open(LAST_RUN_FILE) as f:
        cutoff = float(f.read().strip())
except:
    cutoff = time.time() - 86400  # fallback: 24h ago if file missing
```

This ensures you only pull messages posted SINCE the last scan — no repeats, no gaps.

After the scan completes successfully (Step 3), write the current timestamp to that file:

```python
with open(LAST_RUN_FILE, 'w') as f:
    f.write(str(time.time()))
```

## Step 2 — Pull new messages from all 3 channels

Pull in parallel using `SLACK_FETCH_CONVERSATION_HISTORY`:
- #meeting-notes (limit: 10)
- #updates (limit: 30)
- #testing (limit: 30)

Filter each channel's messages to only include those with `ts > cutoff`. Label the period in the briefing header based on how long ago the cutoff was (e.g. "LAST 24H", "LAST 3 DAYS").

## Step 3 — Build the briefing

Analyze the channel data and format the briefing. Concise — this is a team-facing daily snapshot, not a report.

### Briefing Format

```
Good morning team — here's where we stand.

LAST 24H
[Bullet each meaningful update from channels. Skip noise. Group by person.]
- Steven: [what he shipped/updated]
- Bilal: [what he shipped/updated]
- Tram: [test results, bugs found]

NEEDS ATTENTION
[Only if there ARE items. Skip section entirely if clean.]
- [Unresolved bugs from #testing]
- [Decisions waiting on someone]
- [Anything flagged but not picked up]

TODAY'S FOCUS
1. [Most important thing right now]
2. [Second most important]
3. [Third]
```

Rules:
- No emojis in the Slack post. Professional.
- If there was NO activity in the last 72h on a channel, say "No new activity."
- Keep the whole briefing under 20 lines.
- "Needs Attention" = stuck or waiting, not business as usual.
- "Today's Focus" = your best read on what matters most based on channel evidence. Max 3 items.

## Step 4 — Post to Slack

Use the Slack bot token to post directly via the API (Composio Slack actions are unreliable for posting):

```python
import os, requests
from dotenv import load_dotenv
load_dotenv('/root/.openclaw/.env')
TOKEN = os.getenv('SLACK_BOT_TOKEN')
requests.post('https://slack.com/api/chat.postMessage',
    headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'},
    json={'channel': 'C0AL8LLGULQ', 'text': briefing},
    timeout=30)
```

## Step 5 — Notify Ben via Telegram

After posting to Slack, send Ben a short TG ping:

```
python3 /root/.openclaw/workspace/core/integrations/telegram.py --topic 31 "Morning scan posted to #updates. [1 sentence: anything needing Ben's attention, or 'Nothing urgent.']"
```

## Step 6 — Done

This is autonomous. Execute fully and exit. No confirmation needed.
