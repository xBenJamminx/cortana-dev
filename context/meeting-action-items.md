# Meeting Action Items Workflow

> **Full sync process (Slack → Notion → QA Sheet):** see `context/fam-sync-process.md`
> This file covers just the action item generation + Slack posting piece.

## Trigger
Ben says "process the meeting" (or similar)

## Source
Fathom transcript + summary from the most recent meeting. Pull via Fathom API or Ben provides the link.

## Slack Channel
#meeting-notes (C09J78SH2FM)

## Format
The Fathom summary gets posted first (Fathom bot or Ben does this), then action items follow.

### Action Items Structure
```
*Action Items*

*Person Name* (or *Person Name (Role)*)
• Top-level task with **bold key terms**
• Another task
*Area sub-header:*
• Task grouped under area
    ◦ Sub-detail
    ◦ Sub-detail
*Another area:*
• Task
```

### Formatting Rules
- Group by person/team first
- Within each person, use bold italic area sub-headers to categorize (e.g. *UI fixes:*, *Bug fixes to investigate:*, *Build management:*, *Proactivity:*)
- Top-level tasks that don't fit a category go before the area sub-headers
- Bold key terms/features/objects within each task line
- Sub-bullets (◦) for nested details, edge cases, partial behavior
- Actionable language — what to DO, not what was discussed
- Specific enough to be trackable
- When a bug has partial behavior, describe what works AND what doesn't

### Team Members (FAM POC)
- **Ben** — PM, coordination, QA sheet, Notion updates, follow-ups
- **Bilal** — Frontend / Unity (avatars, AR, UI, builds, TestFlight)
- **Steven, Tram, Khan** — Backend team (LLM, sentiment, sub-agents, proactivity, voice)
- **Joel** — UI/UX Design
- **Cassandra** — Strategy, investor relations, product direction
- **Team** — items that apply to everyone

### Process
1. Pull Fathom transcript for the meeting
2. Read through transcript identifying decisions, assignments, requests, and action items
3. Attribute each action to the right person based on who it was assigned to or who owns that area
4. Group by person, then by functional area within that person
5. Bold the key objects/features being acted on
6. Add sub-bullets for specifics or edge cases
7. Draft and send to Ben for review before posting to Slack

## Notes
- Fathom free tier generates action items ~first few meetings per month, then runs out
- The transcript is the primary source — summary alone misses detail
- Previous meetings' action items provide context for what's ongoing vs new
