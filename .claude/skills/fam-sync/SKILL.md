---
name: fam-sync
description: Run the FAM project sync — pulls Slack (#meeting-notes, #updates, #testing), Notion, and QA Sheet, generates a delta of changes, presents to Ben for approval, then writes on approval. Two-phase: analyze first, write second. Use when Ben says "run the fam sync", "sync the board", "update Notion", "update the QA sheet", or any variation asking for the project sync.
---

# FAM Sync Skill

Two-phase interactive sync that keeps Notion and the QA Sheet aligned with Slack activity.

## IMPORTANT: This is a CONVERSATION, not a fire-and-forget script

1. Run analyze → present delta to Ben
2. Ben approves or gives corrections
3. Run write (or update delta and re-present)
4. Never write without explicit approval

---

## Phase 1 — Analyze

```bash
ssh cortana "python3 $CORTANA_WORKSPACE/scripts/fam-sync-analyze.py"
```

Timeout: 5 minutes. The script:
- Pulls Slack messages from #meeting-notes (5 msgs), #updates (30), #testing (30)
- Pulls all Notion tasks (In Progress, In Testing, Not Started)
- Pulls QA Sheet "In Progress" tab
- Sends to Gemini to generate a structured delta
- Saves delta to `$CORTANA_WORKSPACE/logs/fam-sync-delta.json`
- Sends formatted summary to Telegram topic 2122

After running, relay the delta output to Ben and wait for his response.

## Phase 2 — Write (only after Ben approves)

```bash
ssh cortana "python3 $CORTANA_WORKSPACE/scripts/fam-sync-write.py"
```

Reads the saved delta and executes:
- Creates new Notion tasks (direct API)
- Updates Notion task statuses (direct API)
- Updates QA Sheet (GOOGLESHEETS_BATCH_UPDATE_VALUES_BY_DATA_FILTER)
- Updates last-run timestamp
- Sends completion report to Telegram topic 2122

## Handling Ben's response

**"approved" / "looks good" / "run it"** → run Phase 2 immediately

**Corrections (e.g. "change X to In Testing", "remove item 2", "add Y"):**
1. Read the delta file: `ssh cortana "cat $CORTANA_WORKSPACE/logs/fam-sync-delta.json"`
2. Apply the correction to the JSON in-place on the server
3. Re-present the updated delta to Ben for final confirmation
4. Then run Phase 2

**"skip item X"** → remove that item from the delta JSON before running Phase 2

## What gets synced where

| Task type | Notion | QA Sheet |
|-----------|--------|----------|
| Steven/Bilal dev tasks | ✓ | ✓ |
| Ben tasks | ✓ | ✗ |
| Cassandra tasks | ✓ | ✗ |
| Low priority items | ✓ | ✗ |

## Key facts
- Direct Notion API (not Composio) — Composio Notion actions are broken
- GOOGLESHEETS_BATCH_UPDATE_VALUES_BY_DATA_FILTER for Sheets (regular BATCH_UPDATE is broken)
- Notion DB: `26c4666bd1ca807b930dca5ffff9c8e9`
- QA Sheet: `1TfblNSRCTqkKJFIxPpIlb8b-iE9cSeR16Lu4gMZ0Qio`
- Full credentials and team IDs in `$CORTANA_WORKSPACE/context/fam-sync-process.md`

## Don't
- Never skip the approval gate — even if Ben seems to want it fast
- Never run Phase 2 without an explicit go-ahead
- Never run both phases in one shot without showing Ben the delta
