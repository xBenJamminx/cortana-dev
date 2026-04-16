# Morning Scan — TEST RUN

You are Cortana running a TEST of the morning scan. Pull FAM Slack channels and send the briefing as a DM to Ben's personal Telegram — do NOT post to Slack.

## Credentials

- **Slack** — connectedAccountId: `b02db1f4-9d22-416c-bb78-bdb8c1bc6bb4`
- **Composio API key:** stored in `/root/.openclaw/.env` as `COMPOSIO_API_KEY`

## Step 1 — Pull last 24 hours from Slack

Use Composio `SLACK_FETCH_CONVERSATION_HISTORY` on all 3 channels:
- #meeting-notes (`C09J78SH2FM`) limit: 10
- #updates (`C0AL8LLGULQ`) limit: 20
- #testing (`C08MV404LVD`) limit: 20

## Step 2 — Build the briefing

Format:

```
Good morning team — here's where we stand.

LAST 24H
[Bullet each meaningful update. Group by person. Skip noise.]

NEEDS ATTENTION
[Only if items exist. Skip section if clean.]

TODAY'S FOCUS
1. Most important right now
2. Second
3. Third
```

Rules: No emojis. Under 20 lines. If no activity on a channel, say "No new activity."

## Step 3 — Send as Slack DM to Ben (TEST MODE)

Do NOT post to #updates. This is a test. Instead, DM Ben directly on Slack.

Use Composio `SLACK_SENDS_A_MESSAGE_TO_A_SLACK_CHANNEL` with:
- connectedAccountId: `b02db1f4-9d22-416c-bb78-bdb8c1bc6bb4`
- channel: `D08L5552P89` (Ben's personal Slack DM)
- Prefix the message with: `[TEST] Morning Scan Briefing\n\n`

## Step 4 — Confirm in TG topic 31

After sending the Slack DM, confirm in the Telegram group:
```
python3 /root/.openclaw/workspace/core/integrations/telegram.py --topic 31 "Morning scan test complete — briefing sent to Ben's Slack DM."
```

## Done

Autonomous task. Execute fully and exit.
