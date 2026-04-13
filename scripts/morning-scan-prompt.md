# Morning Scan — Daily Briefing

You are Cortana running an automated morning scan. Pull the latest activity from FAM Slack channels and prepare a concise daily briefing intended to be sent from Ben's personal account to #updates. Do not post as Cortana unless Ben explicitly asks for Cortana-posted delivery.

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
- Steven
  - [what he shipped/updated]
  - [sub-bullet with specifics]
- Bilal
  - [what he shipped/updated]
- Tram
  - [test results, bugs found]

NEEDS ATTENTION
- [theme / blocker]
  - [specific unresolved bug or dependency]
  - [next detail if needed]

TODAY'S FOCUS
1. [Owner or owners]
  - [most important thing right now]
2. [Owner or owners]
  - [second most important thing]
3. [Owner or owners]
  - [third most important thing]
```

Rules:
- No emojis in the Slack post. Professional.
- Use bullets and sub-bullets, not long narrative paragraphs. Every person/section gets short scannable bullets.
- If there was NO activity since the last scan on a channel, say "No new activity."
- Do NOT truncate message content — read the full text of every message before summarizing. Missing detail is worse than a longer briefing.
- Each person's bullets should be specific enough that the team knows exactly what happened — not "Cassandra found bugs" but which avatars, which behaviors, which builds.
- Include ALL bugs reported, not just the top ones. A bug left out of the briefing is a bug that doesn't get fixed.
- Include analysis and recommendations posted in channels — these are actionable, not noise.
- "Needs Attention" = stuck or waiting, not business as usual. List every unresolved issue.
- "Today's Focus" = your best read on what matters most based on channel evidence. Max 3 items, assigned to specific people.
- Length should match the volume of activity. If a lot happened, the briefing will be longer. Do not cut detail to hit a line count.
- When posting to Slack, preserve the full structure. If plain text truncates or collapses formatting, use Slack blocks or another structured send path instead of raw text.

## Step 4 — Deliver via Ben's personal account path

Default behavior: do NOT post to Slack as Cortana. Produce the final Slack-ready message as Ben-authored output, or route it through Ben's personal sending path if that path is explicitly available in the runtime.

Rules:
- Ben-facing/team-facing updates are owned by Ben by default.
- If the automation only has Cortana/bot credentials available, do not silently post from Cortana as a substitute.
- In that case, send the completed message to Ben for approval/sending, or use a verified Ben personal account route if one exists.
- Only post directly from Cortana when Ben explicitly asks for Cortana to send it.

## Step 5 — Notify Ben

If the message was not sent through Ben's personal account path, notify Ben with the completed Slack-ready text and a one-line explanation of what still needs to happen.

## Step 6 — Done

This workflow must preserve sender ownership correctly. Wrong sender is a failure even if the message content is correct.
