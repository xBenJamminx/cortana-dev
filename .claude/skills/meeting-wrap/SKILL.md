---
name: meeting-wrap
description: Generate a formatted meeting wrap-up from today's FAM POC Standup and send it to Ben via Telegram topic 2122 for review before posting to Slack. Pulls Key Takeaways verbatim from Fathom summary (with timestamped links), extracts and groups action items from the transcript via Gemini. Ben posts it to Slack himself. Use when the user says "/meeting-wrap", "run the meeting wrap", "format the standup", "generate meeting notes", or any variation asking for the post-meeting Slack summary.
---

# Meeting Wrap Skill

Generates the FAM POC Standup wrap-up after each meeting and sends it to Ben via Telegram for review.

## Architecture

Pipeline:
1. Finds today's meeting via Fathom (`fathom today`) or accepts a meeting ID argument
2. Pulls structured summary from Fathom (verbatim Key Takeaways with timestamped share links)
3. Pulls full transcript from Fathom (for action item extraction)
4. Sends transcript to Gemini 2.5 Flash via OpenRouter to extract and group action items
5. Assembles final briefing and sends to Ben via Telegram topic 2122
6. Ben reviews and pastes into Slack himself -- this script NEVER posts to Slack

## How to run it

```bash
# Today's meeting (auto-detected)
ssh cortana "python3 /root/.openclaw/workspace/scripts/meeting-wrap-v1.py"

# Specific meeting ID
ssh cortana "python3 /root/.openclaw/workspace/scripts/meeting-wrap-v1.py 138608865"
```

Use a 5-minute timeout (300000 ms) -- transcript pull + OpenRouter call can take 60-90 seconds.

## Output format

```
FAM POC Standup - April 16, 2026

[VIEW RECORDING - 75 mins](url) · [Share Link](url)

Key Takeaways

[Section title @ timestamp](timestamped_share_url)
[Full paragraph verbatim from Fathom summary]

...

Action Items @channel

*Steven Cao*
Category:
- action item

*Muhammad Bilal Akram*
...

*Ben Jammin*
...
```

## Format rules
- Key Takeaways: verbatim from Fathom summary -- never rewritten or shortened
- Action items: extracted from transcript, rewritten as clean third-person professional items
- Person order: Steven -> Bilal -> Ben -> Cassandra
- Tram's items go under Steven's section -- no separate Tram section
- New hires not yet started (Ian, Chris Miller, Parry) appear inside other people's items if relevant
- Bold person names use *Name* (Slack mrkdwn)
- No emojis, no em dashes

## Reporting back
- Script sends full briefing to Telegram topic 2122 automatically
- Confirm it was sent, note the meeting title and date
- "Done -- FAM standup wrap sent to Telegram. Review and paste into #meeting-notes."

## Don't
- Never post to Slack -- Ben always posts himself
- Never confuse this with the morning scan (morning-scan-v2.py) -- different script, different purpose
- Never run the FAM sync process when asked for meeting notes
