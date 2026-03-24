# Meeting Wrap-Up Workflow

> **Full sync process (Slack → Notion → QA Sheet):** see `context/fam-sync-process.md`

## Trigger
Ben says "meeting wrap up" (or similar: "process the meeting", "summarize the meeting", etc.)

## Process

### 1. Pull the meeting
- Run `python3 core/fathom/client.py meetings --limit 5` to list recent meetings
- Confirm which meeting (usually the most recent)
- Pull full data: `python3 core/fathom/client.py meeting <recording_id>`
- Pull summary: `python3 core/fathom/client.py summary <recording_id>`

### 2. Draft the Summary Message
Format matches previous #meeting-notes posts:
```
*Meeting Title - Month DD*

*<FATHOM_SHARE_URL|VIEW RECORDING - X mins (No highlights)>* *<!channel>*
<FATHOM_SHARE_URL?tab=summary&timestamp=0|Section title @ 0:00>
Description paragraph.
<FATHOM_SHARE_URL?tab=summary&timestamp=XXX|Section title @ MM:SS>
Description paragraph.
...
```
- Use the Fathom chronological summary sections with timestamped links
- Each section has a linked header and a paragraph description

### 3. Draft the Action Items Message
Separate message from summary. Format:
```
Meeting Title - Month DD

*Action Items <!channel>*

*Person Name*
*Area sub-header:*
• Action item with **bold key terms**
• Another action item
    ◦ Sub-detail
*Another area:*
• Action item
```

#### Formatting Rules
- Group by person first
- Within each person, use italic area sub-headers to categorize (e.g. *Bug fixes:*, *UI fixes:*, *Testing:*)
- Top-level tasks that don't fit a category go before the area sub-headers
- Bold key terms/features/objects within each task line
- Sub-bullets (◦) for nested details, edge cases, partial behavior
- Actionable language — what to DO, not what was discussed
- Specific enough to be trackable
- When a bug has partial behavior, describe what works AND what doesn't
- NO editorializing (no "PRIORITY", "Decision needed ASAP", etc.) — just the action items
- NO role descriptions in parentheses after names

### 4. Send BOTH drafts to Ben in Telegram
- Post the summary draft and action items draft in the current Telegram topic
- Ben reviews and posts them to Slack himself
- NEVER post directly to Slack without explicit confirmation

## Slack Channel
#meeting-notes (C09J78SH2FM)

## Team Members (FAM POC)
- **Ben** — PM, coordination, QA sheet, Notion updates, follow-ups
- **Bilal** — Frontend / Unity (avatars, AR, UI, builds, TestFlight)
- **Steven** — Backend lead (LLM, sentiment, sub-agents, proactivity, voice)
- **Tram, Khan** — Backend team
- **Joel** — UI/UX Design
- **Cassandra** — Strategy, investor relations, product direction
- **Team** — items that apply to everyone

## Notes
- Fathom free tier generates action items ~first few meetings per month, then runs out
- The transcript is the primary source — summary alone misses detail
- Previous meetings' action items provide context for what's ongoing vs new
