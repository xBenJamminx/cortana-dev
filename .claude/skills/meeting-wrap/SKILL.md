---
name: meeting-wrap
description: Generate a formatted meeting wrap-up from today's FAM POC Standup and send it to Ben via Telegram topic 2122 for review before posting to Slack. Pulls Key Takeaways verbatim from Fathom summary (with timestamped links), extracts and groups action items from the transcript via Gemini. Use when the user says "/meeting-wrap", "run the meeting wrap", "format the standup", "generate meeting notes", or any variation asking for the post-meeting Slack summary.
---

# Meeting Wrap Skill

Generates the FAM POC Standup wrap-up after each meeting, sends to Telegram for Ben's review, then posts to Slack on approval.

## The script does everything — run it, do not draft manually

`/root/.openclaw/workspace/scripts/meeting-wrap-v1.py`

Doing it manually = wrong channel, wrong account, wrong format. The script handles Fathom, Gemini, Telegram, and Slack. Your job is to run it and wait.

---

## Phase 1 — Generate and send to Telegram for review

```bash
cd /root/.openclaw/workspace && python3 scripts/meeting-wrap-v1.py
```

For a specific meeting ID:

```bash
cd /root/.openclaw/workspace && python3 scripts/meeting-wrap-v1.py 138608865
```

Use a 5-minute timeout (300000 ms) — transcript pull + OpenRouter call takes 60-90 seconds.

What it does:

1. Finds today's meeting via Fathom
2. Pulls full transcript + summary
3. Sends transcript to Gemini to extract action items
4. Saves briefing to `logs/meeting-wrap-briefing.txt`
5. Sends briefing to Telegram topic 2122 for Ben to review
6. Ends with: "Review the wrap above. Reply 'post it' or 'approved' and I'll post to #meeting-notes as you."

After running: tell Ben "Done — FAM standup wrap sent to Telegram topic 2122. Review it there."

**IMPORTANT: You MUST run Phase 1 before Phase 2. `--post` reads the saved briefing from `logs/meeting-wrap-briefing.txt` and will refuse to post if it was not generated today.**

---

## Phase 2 — Post to Slack (ONLY after Ben approves)

```bash
cd /root/.openclaw/workspace && python3 scripts/meeting-wrap-v1.py --post
```

What it does:
- Reads saved briefing from `logs/meeting-wrap-briefing.txt`
- Posts to **#meeting-notes** (`C09J78SH2FM`) as Ben via Composio (connected account `b02db1f4`)
- Posts as **two messages** (Key Takeaways, then Action Items) — Slack has a 50-block limit
- Notifies Ben on Telegram when done

After running: "Posted to #meeting-notes."

**Wait for Ben to say "approved", "post it", "looks good", or similar before running Phase 2.**

---

## Handling Ben's response after Phase 1

- **"approved" / "post it" / "looks good"** → run Phase 2 (`--post`) immediately
- **Corrections (e.g. "fix X", "remove Y")** → edit `logs/meeting-wrap-briefing.txt` on the server, re-send the updated section to Telegram, wait for re-approval
- **"skip it" / no response** → do nothing

---

## Output format

```text
*FAM POC Standup - April 27, 2026*

[VIEW RECORDING - 52 mins](url) · [Share Link](url)

*Key Takeaways*

[Section title @ timestamp](timestamped_share_url)
Full paragraph verbatim from Fathom summary

...

*Action Items* @channel

*Steven Cao*
Category:
- action item

*Muhammad Bilal Akram*
...

*Ben Jammin*
...
```

## Format rules
- Key Takeaways: verbatim from Fathom summary — never rewritten or shortened
- Action items: extracted from transcript, rewritten as clean third-person professional items
- Only include people who were actually in the meeting — do NOT fabricate sections for absent team members
- Person order: Steven → Bilal → Ben → Cassandra
- Tram's items go under Steven's section — no separate Tram section
- New hires not yet started (Ian, Chris Miller, Parry) appear inside other people's items if relevant
- Bold person names use *Name* (Slack mrkdwn)
- No emojis, no em dashes

---

## Don't

- Never post to Slack without Ben's explicit approval first
- Never run `--post` without having run Phase 1 first today — `--post` will error on a stale briefing
- Never draft the briefing manually in chat — always run the script
- Never use the bot token to post to Slack — the script uses Ben's Composio account
- Never post to #updates — always #meeting-notes (C09J78SH2FM)
- Never include action items for people who weren't in the meeting
- Never confuse this with the morning scan (morning-scan-v2.py) or FAM sync — different scripts, different purposes
