# FAM POC — Sync Process

## For Cortana to execute autonomously

This process keeps Notion, the QA Sheet, and Slack channels in sync. Run after every standup, or any time updates/testing channels have new activity.

---

## When to Run

- After every standup (meeting notes posted in #meeting-notes)
- When Tram or Steven posts updates in #updates
- When new bugs or test results appear in #testing
- When Ben asks for a sync

---

## API Credentials

- **Slack** — connectedAccountId: `b02db1f4-9d22-416c-bb78-bdb8c1bc6bb4`
- **Notion** — connectedAccountId: `95a40153-5972-4b4c-851c-0632d1e0d816` | Database: `26c4666bd1ca807b930dca5ffff9c8e9` | FAM POC Project ID: `26c4666b-d1ca-80e5-a4cd-fc007ab84486`
- **Google Sheets** — connectedAccountId: `c42f121c-9abe-406e-a4f7-b1dd3a6c1314` | Sheet ID: `1TfblNSRCTqkKJFIxPpIlb8b-iE9cSeR16Lu4gMZ0Qio`
- **Composio API key:** `ak_UjBg3sflMbHRQgr_qzwr`

---

## Slack Channels

These are the only channels relevant to this sync. Pull from each one every run.

| Channel | ID | What to pull from it |
|---------|-----|---------------------|
| #meeting-notes | `C09J78SH2FM` | Fathom standup summaries — action items, decisions, priorities. This is the primary source of truth for new tasks. |
| #updates | `C0AL8LLGULQ` | Build changelogs (what shipped), Tram's backend status updates, Steven's weekly updates. Use to determine In Testing status. |
| #testing | `C08MV404LVD` | Bug reports, regression findings, test pass/fail results from Cassandra and Tram. Use to identify new bugs and confirm what's broken. |
| #poc | `C08K8GH4ZGU` | General POC discussion — context on decisions, ad-hoc requests, clarifications. |
| #apis | `C08KFS565NV` | API docs, endpoint changes, integration notes from Steven's team. |
| #design | `C09JBLC6V3Q` | Design assets, wireframes, UI feedback from Joel. Tasks for Bilal often reference files here. |
| #all-smartcompanionpoc | `C08K8GFRYTE` | General team channel — catch-all for anything not in the above. |

---

## Team — Notion User IDs

| Person | Role | Notion User ID |
|--------|------|---------------|
| Steven (Cao Tan Luc) | Backend Developer — owns ALL backend work (APIs, sub-agents, voice, sentiment, Hume, computer vision, calendar, memory, LLMs) | `9b822e2d-467a-421f-b17f-af78b6e3bdd1` |
| Bilal (Muhammad Bilal Akram) | Frontend Developer — Unity, AR, avatar rendering, UI, animations | `9d54ac97-30c7-4e0d-a2bf-aa46796e4c79` |
| Ben | Product / Owner | `2ddd48a3-d87a-417a-9e5c-c41b8d8b3d90` |

---

## The Process (execute in this exact order)

### STEP 1 — Pull raw data from all sources in parallel

Pull the latest messages from each channel simultaneously using `SLACK_FETCH_CONVERSATION_HISTORY`:

- **#meeting-notes** (`C09J78SH2FM`) — limit: 5 (captures the last 2–3 standups)
- **#updates** (`C0AL8LLGULQ`) — limit: 30 (build changelogs and backend status posts)
- **#testing** (`C08MV404LVD`) — limit: 30 (bug reports and test results)
- **#poc** (`C08K8GH4ZGU`) — limit: 20 (ad-hoc decisions and context)

At the same time, pull current task state from Notion:

- `NOTION_QUERY_DATABASE` — filter Status: "In Progress", page_size: 50
- `NOTION_QUERY_DATABASE` — filter Status: "In Testing", page_size: 50
- `NOTION_QUERY_DATABASE` — filter Status: "Not Started", page_size: 50

And from the QA Sheet:

- `GOOGLESHEETS_BATCH_GET` on `"In Progress!A1:I60"`

**Save all raw data before processing. Do not summarize yet.**

---

### STEP 2 — Parse action items from meeting notes

From the most recent standup post in **#meeting-notes**:

1. Find the **Action Items** section — Fathom always places it at the bottom of each standup post
2. Extract every bullet point listed under each person's name (Steven, Bilal, Ben, Cassandra, Team/Shared)
3. Write out each item **in full** — do not shorten, abbreviate, or paraphrase. Use the exact wording from the meeting notes.
4. Note which standup date the item came from

From **#updates**, extract:

- Build changelogs — list every feature mentioned as shipped or updated
- Status updates from Tram or Steven — any explicit "X is done" or "X is now in testing" statements
- Backend architecture updates that imply task completion

From **#testing**, extract:

- Bug reports — feature name, what's broken, which build, who reported it
- Test results — what passed, what failed, what needs re-testing

---

### STEP 3 — Build the master delta list

Compare every extracted item against the current Notion tasks and QA Sheet rows.

For each item, determine the correct action:

| Scenario | Action |
|----------|--------|
| Item exists in neither Notion nor QA Sheet | CREATE in both |
| Item exists in Notion but not QA Sheet | ADD to QA Sheet |
| Item exists in QA Sheet but not Notion | CREATE in Notion |
| Item exists in both but status is outdated | UPDATE both |
| Item is marked complete in channels but still In Progress in tracking | UPDATE both to Done or In Testing |

When checking for duplicates, match by **semantic meaning** — not exact string. "Fix auto-spawn" and "Implement automatic avatar spawn on app launch" are the same task.

**Status mapping rules — use channel evidence:**

| Channel evidence | Status to set |
| ---------------- | ------------- |
| "X is done / completed / merged / finished" | Done |
| "X is in testing / being tested / testing now" | In Testing |
| Build changelog lists feature X as shipped | In Testing (shipped ≠ done — it now needs testing) |
| Bug reported in #testing against feature X | In Progress (add bug detail to Comments) |
| Regression found — feature that was working is now broken | In Progress (note which build broke it) |
| "Continue working on X" / "X is in progress" | In Progress (no change) |
| No channel evidence of any progress | Not Started (no change) |

**Priority mapping:**

| Situation | Priority |
| --------- | -------- |
| Blocks other work / broken in active build / critical path | Top |
| Important feature / active bug affecting usability | High |
| Enhancement / UX improvement / non-blocking issue | Medium |
| Nice-to-have / low impact / future consideration | Low |

---

### STEP 4 — Update Notion first

For every item in the delta list, update Notion before touching the QA Sheet.

**Creating new tasks** — use `NOTION_INSERT_ROW_DATABASE`:

```text
database_id: 26c4666bd1ca807b930dca5ffff9c8e9
Properties:
  - Name:     [FULL task name — exact wording from meeting notes, no abbreviation]
  - Status:   [correct status from mapping rules above]
  - Priority: [Top / High / Medium / Low]
  - Assigned: [person user ID from team table]
  - Project:  [relation — FAM POC project ID: 26c4666b-d1ca-80e5-a4cd-fc007ab84486]
```

Every new task MUST have all five fields set before moving on. A task missing any of these is incomplete.

**Updating existing tasks** — use `NOTION_UPDATE_PAGE`:

```text
page_id: [existing page ID]
Properties to update:
  - Status:   [new status]
  - Comments: [add evidence — e.g. "Gemini migration complete (Tram, Mar 11 update)"]
```

---

### STEP 5 — Update QA Sheet second

After Notion is updated, mirror all changes to the **"In Progress"** tab of the QA Sheet.

**Sheet column layout:**

```text
A: Feature  |  B: Condition  |  C: Expectation  |  D: Example 1  |  E: Example 2  |  F: Priority  |  G: Status  |  H: Comments  |  I: Assigned
```

**Adding new rows:**

- Use `GOOGLESHEETS_BATCH_UPDATE` with `first_cell_location` parameter pointing to the first empty row (e.g. `"In Progress!A38"`)
- The `range` parameter is ignored by Composio — always use `first_cell_location`
- Feature name in column A must match the Notion task name exactly
- Comments column (H): always include the evidence source and date (e.g. "Build 5(22) changelog Mar 12", "Tram Mar 11 update", "Mar 12 standup")
- Assigned column (I): use first name only (Steven, Bilal, Ben, Tram, Cassandra)

**Updating existing rows:**

- Find the row by matching the Feature name in column A
- Update only the changed columns using `first_cell_location` (e.g. `"In Progress!G7"` to update just the Status cell)

---

### STEP 6 — Full status sweep

After all new items are added, do a pass over the entire QA Sheet to catch anything that got missed.

1. Read the full "In Progress" tab (`GOOGLESHEETS_BATCH_GET` on `"In Progress!A1:I60"`)
2. For every row, verify the status is consistent with all channel evidence collected in Step 2
3. Any corrections → update QA Sheet cell first, then update matching Notion page

Specifically check for:

- "In Progress" items that channels show are now "In Testing" or "Done"
- "Not Started" items that channels show have been picked up
- "In Testing" items that have regressions — move back to "In Progress" with build number in comments
- Duplicate rows — consolidate if two rows describe the same task

---

### STEP 7 — Quality check before finishing

Do not report to Ben until every box is checked:

- [ ] Every action item from the most recent standup is tracked in Notion
- [ ] Every bug reported in #testing is tracked in Notion and QA Sheet
- [ ] No task names were shortened or abbreviated
- [ ] All new Notion tasks have: Name, Status, Priority, Assigned, Project
- [ ] QA Sheet statuses match Notion statuses for all shared items
- [ ] Evidence source is in the Comments column for every status change
- [ ] No item was added to QA Sheet without a matching Notion task

---

### STEP 8 — Report to Ben

Summarize what changed in this format:

1. **New tasks created** — total count, broken down by person (Steven / Bilal / Ben / other)
2. **Status changes** — what moved, from what to what, and why (cite channel + date)
3. **New bugs tracked** — source channel, assigned to whom
4. **Ambiguous items** — anything where status is unclear or ownership is unknown; ask Ben to clarify
5. **Blockers** — broken builds, absent team members, unresolved dependencies

Keep it tight. Ben reads this to understand what changed, not to re-read the meeting notes.

---

## Common Mistakes to Avoid

1. **Never shorten task names.** Use the exact wording from the meeting notes, every time.
2. **Never update only one system.** QA Sheet change = Notion change. Always both.
3. **Never create a task without all five fields.** Name + Status + Priority + Assigned + Project.
4. **Don't re-add items that already exist.** Check for semantic duplicates before creating.
5. **Shipped ≠ Done.** A feature appearing in a build changelog moves to In Testing, not Done.
6. **Don't summarize Slack data before extracting action items.** Read the raw text first.
7. **Composio BATCH_UPDATE quirk:** The `range` parameter is ignored. Always use `first_cell_location`.
8. **Steven = Cao Tan Luc** in Notion. All backend work belongs to him. Do not create a new user.
9. **Bilal owns all frontend/Unity work.** If it's a UI, animation, AR, or build issue — it's Bilal.
10. **Ben owns product tasks** — naming conventions, QA sheet updates, descriptions, clarifications with the team.
