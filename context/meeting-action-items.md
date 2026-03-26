# Meeting Wrap-Up Workflow

> **Full sync process (Slack -> Notion -> QA Sheet):** see `context/fam-sync-process.md`

## Trigger
Ben says "meeting wrap up" or similar: "process the meeting", "summarize the meeting", "run the meeting sync", etc.

## Process

### 1. Pull the meeting
- Run `python3 core/fathom/client.py meetings --limit 5` to list recent meetings
- Confirm which meeting -- usually the most recent
- Pull full data: `python3 core/fathom/client.py meeting <recording_id>`
- Pull summary: `python3 core/fathom/client.py summary <recording_id>`

### 2. Draft the Summary Message
Format matches previous #meeting-notes posts. Plain text, clean, no over-formatting:
```
Companion POC - Month DD

VIEW RECORDING - X mins (No highlights) (FATHOM_SHARE_URL) @channel

Section title @ M:SS (FATHOM_SHARE_URL?tab=summary&timestamp=XXX)
Description paragraph. Plain text. No bold, no italic, no markdown formatting in the body.

Another section @ M:SS (FATHOM_SHARE_URL?tab=summary&timestamp=XXX)
Description paragraph.
```
- Use the Fathom chronological summary sections with timestamped links
- Each section has a linked header and a plain text paragraph description
- Keep descriptions factual and concise -- what was discussed and decided, not editorial

### 3. Draft the Action Items Message
Separate message from summary. Clean format:
```
Companion POC - Month DD

Action Items @channel

Steven
Bug fixes:
• Action item -- brief context using double dashes
• Another action item
Testing:
• Action item

Bilal
UI fixes:
• Action item
Maps:
• Action item

Ben
• Action item
• Another action item

Cassandra
• Action item
```

#### Formatting Rules
- Group by person first -- just the name, no role in parentheses
- Section sub-headers within a person are fine like Bug fixes:, UI fixes:, Testing: -- plain text with colon
- Simple bullet points only -- NO sub-bullets, NO nested bullets
- NO bold anywhere in action items
- NO italic anywhere in action items
- Use double dashes -- to add context to an item, not parentheses
- Actionable language -- what to DO, not what was discussed
- Specific enough to be trackable
- When a bug has partial behavior, describe what works AND what does not
- NO editorializing -- no PRIORITY, no Decision needed ASAP, etc. Just the action items.
- NO role descriptions in parentheses after names
- Keep it clean and copy-pasteable -- Ben posts these directly to Slack

### 4. Send BOTH drafts to Ben in Telegram
- Post the summary draft and action items draft in the current Telegram topic
- Ben reviews and posts them to Slack himself
- NEVER post directly to Slack without explicit confirmation

## Slack Channel
#meeting-notes -- C09J78SH2FM

## Team Members -- FAM POC
- Ben -- PM, coordination, QA sheet, Notion updates, follow-ups
- Bilal -- Frontend / Unity -- avatars, AR, UI, builds, TestFlight
- Steven -- Backend lead -- LLM, sentiment, sub-agents, proactivity, voice
- Tram, Khan -- Backend team
- Joel -- UI/UX Design
- Cassandra -- Strategy, investor relations, product direction
- Team -- items that apply to everyone

## Reference: Approved Format -- March 24
This was the format Ben approved and posted. Match this exactly:

```
Companion POC - March 24

Action Items @channel

Steven
Bug fixes:
• Fix UTC time parsing -- calendar events off by 1 hour
• Fix voice prompt leaking -- AI reading system/voice instruction prompts aloud to user
Testing:
• Retest all basic functionality before next build
• Deliver updated build for testing by Wednesday

Bilal
UI fixes:
• Selected avatar needs to be noticeably taller than unselected ones
• Fix Mocha text color -- white instead of inverted
Mapbox:
• Fix Mapbox or revert to Google Maps -- has never worked across ~20 builds

Ben
• Continue testing all features and document bugs
• Post testing notes in #testing channel

Cassandra
• Available Wednesday to help test new build
```

## Notes
- Fathom free tier generates action items first few meetings per month, then runs out
- The transcript is the primary source -- summary alone misses detail
- Previous meetings action items provide context for what is ongoing vs new
