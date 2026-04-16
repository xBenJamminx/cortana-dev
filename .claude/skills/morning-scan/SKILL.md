---
name: morning-scan
description: Trigger the FAM Smart Companion morning Slack briefing. Runs the morning-scan-v2.py script on the cortana server via SSH, which pulls the last 24h (or longer) of Slack messages, summarizes them via OpenRouter, and posts to the FAM #updates channel. Use when the user says "/morning-scan", "run the morning scan", "trigger the morning briefing", "fire the FAM scan", or any variation asking for the morning team update.
---

# Morning Scan

Triggers the FAM Smart Companion daily Slack briefing on demand.

## What it does

1. SSHes to the `cortana` server
2. Runs `/root/.openclaw/workspace/scripts/morning-scan-v2.py`
3. The script:
   - Pulls Slack messages from the last 24h (or longer if the last successful run was more than a day ago)
   - Sends the messages to OpenRouter for summarization
   - Posts the summary to the FAM `#updates` Slack channel
4. Reports back to the user with the script's output and exit status

## How to run it

Execute exactly this command via the Bash tool:

```bash
ssh cortana "python3 /root/.openclaw/workspace/scripts/morning-scan-v2.py"
```

Use a generous timeout (300000 ms / 5 minutes) — the script summarizes via OpenRouter and posts to Slack, so it can take a minute or two.

## Reporting back

After the command finishes:

- If exit code is 0: confirm the briefing was posted, and surface any noteworthy lines from stdout (channel posted to, message count summarized, link if present).
- If exit code is non-zero: surface the error output, identify the failure mode (SSH connection failure, Python error, Slack API error, OpenRouter error), and suggest the next step.

Keep the confirmation tight — Cortana voice. Example shapes:

- Done — briefing posted to FAM #updates, summarized N messages from the last 24h.
- Briefing posted. Covered yesterday + this morning since the last run was 2 days ago.
- Scan failed — OpenRouter returned 429. Try again in a minute.

## Don't

- Don't `cat` the script, edit it locally, or try to reimplement it in this session. The script lives on the server and is the source of truth.
- Don't spawn it as a background task — wait for it inline so you can confirm success.
- Don't post to Slack yourself. The script handles all Slack writes.
