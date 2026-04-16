---
name: morning-scan
description: Trigger the FAM Smart Companion morning Slack briefing. Pulls the last 24h (or longer) of Slack messages from #updates, #testing, and #meeting-notes, summarizes via Gemini 2.5 Flash on OpenRouter, and posts to FAM #updates as Ben. Use when the user says "/morning-scan", "run the morning scan", "trigger the morning briefing", "post the FAM update", or any variation asking for the morning team update.
---

# Morning Scan Skill

Triggers the FAM Smart Companion daily Slack briefing on demand.

## Architecture

This is a skill that orchestrates a Python script on the `cortana` server. The script (`morning-scan-v2.py`) is the execution engine — this skill is the interface layer.

The pipeline:

1. Pulls Slack messages from `#updates`, `#testing`, `#meeting-notes` since the last run
2. Resolves Slack user IDs to real names (correct attribution, no guessing)
3. Sends raw messages to Gemini 2.5 Flash via OpenRouter for synthesized summarization
4. Converts the briefing to Slack Block Kit (proper bullet lists, sub-lists, bold headers)
5. Posts to FAM `#updates` as Ben via Composio connected account (`b02db1f4`)
6. Updates the last-run timestamp and notifies Ben on Telegram topic 31

## How to run it

```bash
ssh cortana "python3 /root/.openclaw/workspace/scripts/morning-scan-v2.py"
```

Use a 5-minute timeout (300000 ms) — the OpenRouter call can take 30-60 seconds.

## Optional: override the time window

To force a specific lookback window, reset the last-run timestamp first:

```bash
# Force 3-day window
ssh cortana "python3 -c \"import time; open('/root/.openclaw/workspace/logs/morning-scan-last-run.txt','w').write(str(time.time()-3*86400))\""
# Then run normally
ssh cortana "python3 /root/.openclaw/workspace/scripts/morning-scan-v2.py"
```

## Reporting back

- Exit 0: confirm posted to #updates, mention the message count and time window from stdout.
- Non-zero: surface the error, identify the failure (SSH, OpenRouter, Composio/Slack, Python).

Keep it tight — Cortana voice:
- "Done — briefing posted to #updates, 17 messages across 3 days."
- "Scan failed — Composio returned 403. Cloudflare user-agent issue. Check the script."

## Don't

- Don't edit or reimplement the script in this session — it lives on the server.
- Don't post to Slack yourself — the script owns all Slack writes.
- Don't run it in the background — wait inline so you can confirm success.
