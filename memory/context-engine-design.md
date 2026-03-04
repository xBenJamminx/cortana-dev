# Context Engine Design
## "Everything is Context" Applied to OpenClaw/Cortana

> The paper: treat context like a file system. Mount what you need, skip what you don't.
> The goal: Cortana loads 200 lines per session, not 1,200. And the RIGHT 200 lines.

---

## 1. THE PROBLEM

### Current state: 1,171 lines always loaded

| File | Lines | Load frequency | Actually needed |
|------|-------|---------------|----------------|
| CLAUDE.md | 109 | Every turn | ~30 lines (rules) |
| CORTANA-OS.md | 330 | Every turn | ~15 lines (rarely) |
| SOUL.md | 164 | Every turn | ~30 lines (voice) |
| IDENTITY.md | 77 | Every turn | ~0 lines |
| LEARNINGS.md | 142 | Every turn | ~15 lines (relevant ones) |
| BRAIN.md | 94 | Every turn | ~60 lines (good) |
| SESSION-STATE.md | 39 | Every turn | 0 lines (empty) |
| MEMORY.md | 216 | Every turn | ~50 lines |

**Total loaded: ~1,171 lines. Total useful per average turn: ~200 lines.**

That's 83% waste. Every turn. And this is before the actual conversation even starts.

### Other problems
- 64 files in `memory/` with no index, no search path, no promotion logic
- QMD memory configured but opaque (no visibility into what it stores/retrieves)
- Daily memory files (`2026-MM-DD.md`) are write-only. Nobody reads them unless manually triggered.
- SESSION-STATE.md is empty. It was designed but never wired up.
- BRAIN.md is the only file that actually works as intended. Everything else is either bloated or abandoned.

---

## 2. THE ARCHITECTURE

Four layers, matching the paper's model. Each layer has a clear purpose, retention policy, and promotion/demotion rules.

```
Layer 4: SYSTEM PROMPT (always loaded, <200 lines)
    |
Layer 3: TASK CONTEXT (loaded on-demand per task type)
    |
Layer 2: INDEXED MEMORY (searchable, never auto-loaded)
    |
Layer 1: RAW LOGS (append-only, auto-pruned)
```

### Layer 4: System Prompt (the "mount table")

**What lives here:** Identity, voice rules, current state, routing table.
**Target:** Under 200 lines. Hard limit.
**File:** `CORTANA.md` (replaces CLAUDE.md, SOUL.md, IDENTITY.md, CORTANA-OS.md, SESSION-STATE.md)

This is a SINGLE file. Not eight. One file that contains:

```markdown
# CORTANA.md (~180 lines max)

## Who I Am (10 lines)
- Name, role, emoji, one-liner personality summary
- No D&D stats. No character sheet. No backstory novel.

## Voice Rules (15 lines)
- The 8 rules from SOUL.md, compressed
- No examples (I know what sarcasm sounds like)

## Operating Rules (20 lines)
- Orchestrator pattern (acknowledge -> spawn -> stay available)
- Context discipline (read BRAIN.md, load only what task needs)
- Never go silent, always confirm completion
- No em dashes, no fabricated stats, no tech jargon for Ben

## Current State (20 lines)
- Active project + status (from BRAIN.md)
- Waiting on / blockers
- Recent decisions (last 3)
- Today's date and day of week

## Task Router (30 lines)
- "If task involves X, load context/X.md"
- Maps task types to context files (Layer 3)
- This is the MOUNT TABLE from the paper

## Auth Quick-Ref (20 lines)
- Telegram, Airtable, Gemini, AgentMail
- Just the IDs and commands, not the backstory

## Active Mistakes (15 lines)
- Top 5 most relevant learnings from LEARNINGS.md
- Rotated based on recent error frequency
- Not all 14 entries, just the ones that keep biting

## Flags (10 lines)
- Twitter suspended, Bird CLI banned
- Any time-sensitive blockers
```

**What got cut:**
- IDENTITY.md (D&D stats, appearance, abilities section) -> deleted
- CORTANA-OS.md (330 lines of content pipeline docs) -> moved to context/content-pipeline.md
- SOUL.md examples and override sections -> compressed into voice rules
- MEMORY.md schedule, community section, decision rules -> moved to context/ files
- SESSION-STATE.md -> replaced by "Current State" section that actually gets updated

### Layer 3: Task Context (on-demand mounting)

**What lives here:** Domain-specific knowledge loaded only when relevant.
**Location:** `context/` directory (new)
**Rule:** NEVER auto-loaded. Only loaded when the task router says to.

```
context/
  auth.md              # Full auth details, connection IDs, API bases
  content-pipeline.md  # Airtable fields, content formats, pipeline workflow
  sleep-video.md       # Sleep video pipeline, voice defaults, FFmpeg notes
  parker-taylor.md     # P&T strategy, outreach templates, ICP
  mimoo.md             # OpenConcierge/Mimoo PRD, architecture, pricing
  content-engine.md    # Content strategy, channels, weekly cadence
  five-points.md       # Client work, OEM dashboard
  server-ops.md        # Hetzner config, SSH, systemd, OpenClaw config
  learnings-full.md    # All 14+ learnings with full detail
  community.md         # EverydayAI, Discord, Whop (parked)
  schedule.md          # Ben's weekly schedule, decision rules
```

**How mounting works:**

The Task Router in CORTANA.md maps intent to files:

```markdown
## Task Router

| If the task involves... | Load these context files |
|------------------------|------------------------|
| Sleep/meditation video | context/sleep-video.md |
| Content drafting/posting | context/content-pipeline.md + context/content-engine.md |
| P&T outreach/sales | context/parker-taylor.md |
| Mimoo/OpenConcierge | context/mimoo.md |
| Server/infra/debugging | context/server-ops.md |
| Auth/API issues | context/auth.md |
| Client work (Five Points) | context/five-points.md |
| Scheduling/calendar | context/schedule.md |
| Error investigation | context/learnings-full.md |
| General conversation | Nothing extra needed |
```

The agent reads CORTANA.md, identifies the task type, loads 1-2 context files max, then works. Instead of 1,171 lines, it's 180 + ~100 = ~280 lines.

### Layer 2: Indexed Memory (searchable archive)

**What lives here:** Facts, research, completed work, reference material.
**Location:** `memory/` (existing, but restructured)
**Rule:** Never loaded unless explicitly searched. Indexed by a manifest.

```
memory/
  index.md             # NEW: manifest of what's in memory, with tags and dates
  daily/               # Daily logs (2026-MM-DD.md)
  research/            # Research outputs (business ideas, competitive analysis, etc.)
  drafts/              # Content drafts (prompt packs, guides, templates)
  clients/             # Client-specific notes
  decisions/           # Key decisions with rationale
```

**The Index (memory/index.md):**

```markdown
# Memory Index
Last updated: 2026-03-02

## Daily Logs
| Date | Key topics | File |
|------|-----------|------|
| 2026-03-02 | 50 business ideas, session persistence fix | daily/2026-03-02.md |
| 2026-02-28 | Context loss investigation | daily/2026-02-28.md |
| ... | ... | ... |

## Research
| Topic | Date | File | Tags |
|-------|------|------|------|
| 50 Cortana business ideas | Mar 2 | research/50-business-ideas-brainstorm.md | business, autonomous, cortana |
| Bookmarks deep analysis | Feb | research/BOOKMARKS_DEEP_ANALYSIS.md | bookmarks, market |
| ... | ... | ... | ... |

## Drafts
| Title | Status | File |
|-------|--------|------|
| Prompt pack - business ops | Ready | drafts/prompt-pack-business-operations.md |
| ... | ... | ... |
```

**How search works:**
1. Agent reads `memory/index.md` (lightweight, just filenames + tags + dates)
2. Finds relevant entries by tag/topic match
3. Reads only the specific file needed
4. Never bulk-loads memory/

### Layer 1: Raw Logs (append-only, auto-pruned)

**What lives here:** Session transcripts, cron output, API logs.
**Location:** `logs/` (existing) + QMD sessions
**Rule:** Never read unless debugging. Auto-pruned after 7 days for logs, 30 days for QMD.
**No changes needed here.** This layer already works.

---

## 3. PROMOTION AND DEMOTION RULES

### Upward promotion (Layer 1 -> 2 -> 3 -> 4)

| From | To | Trigger | Example |
|------|-----|---------|---------|
| Raw log -> Indexed memory | After task completion | Write summary to daily/YYYY-MM-DD.md, add to index |
| Indexed memory -> Task context | When a fact is referenced 3+ times across sessions | Move from memory/ to context/ |
| Task context -> System prompt | When it's needed EVERY session | Add to CORTANA.md current state or flags |

### Downward demotion (Layer 4 -> 3 -> 2 -> 1)

| From | To | Trigger | Example |
|------|-----|---------|---------|
| System prompt -> Task context | When something hasn't been relevant for 2+ weeks | Move parked projects out of CORTANA.md |
| Task context -> Indexed memory | When a project is completed or paused | Archive context/five-points.md to memory/clients/ |
| Indexed memory -> Pruned | After 90 days with no references | Delete or archive to cold storage |

### The "Recency Bias" Fix

Right now, BRAIN.md says "Last Task Completed: Server migration" which is a week old. The Current State section should auto-update (or be updated by the post-task write rule) with:
- What was the last thing done THIS session
- What's the most recent pending item
- What's the freshest blocker

---

## 4. SESSION LIFECYCLE

### Session Start (boot sequence)
```
1. Load CORTANA.md (system prompt, ~180 lines)
2. Read CORTANA.md Task Router
3. Identify task type from incoming message
4. Load relevant context/ file(s) (0-2 files, ~50-100 lines each)
5. If needed, search memory/index.md for specific facts
6. Work
```

### During Session
```
- If you need a fact, search memory/index.md first
- If you learn something new, note it for post-task write
- If a context file is missing info, update it after the task
- NEVER hold large file contents in the context window
```

### Session End (flush sequence)
```
1. Write task summary to memory/daily/YYYY-MM-DD.md
2. Update memory/index.md if new research/drafts were created
3. Update CORTANA.md "Current State" section
4. If a new mistake was made, add to context/learnings-full.md
5. If the mistake is critical (keeps happening), promote to CORTANA.md "Active Mistakes"
```

---

## 5. IMPLEMENTATION PLAN

### Phase 1: Restructure (do now)
1. Create `context/` directory
2. Create `CORTANA.md` by compressing the 8 current files into one
3. Move domain knowledge from MEMORY.md/CORTANA-OS.md into `context/` files
4. Create `memory/index.md` manifest
5. Reorganize `memory/` into subdirectories (daily/, research/, drafts/, clients/)

### Phase 2: Wire up the lifecycle (do next)
1. Update CLAUDE.md to point at CORTANA.md instead of loading everything
2. Add post-task flush instructions to CORTANA.md
3. Update spawn_task.sh to include context loading instructions for sub-agents
4. Test: send a message, verify only ~280 lines loaded instead of 1,171

### Phase 3: Automation (do later)
1. Script to auto-generate memory/index.md from file contents
2. Script to rotate "Active Mistakes" based on error frequency
3. Script to demote stale context/ files to memory/ after 2 weeks of no use
4. QMD integration: surface QMD search results in the memory index

---

## 6. WHAT GETS DELETED

These files become OBSOLETE after migration:
- `IDENTITY.md` - absorbed into CORTANA.md (10 lines, not 77)
- `SOUL.md` - absorbed into CORTANA.md (15 lines, not 164)
- `SESSION-STATE.md` - replaced by CORTANA.md Current State (actually updated)
- `CORTANA-OS.md` - split into context/content-pipeline.md + context/schedule.md
- `MEMORY.md` (Claude Code's copy) - compressed into CORTANA.md + context/auth.md

CLAUDE.md stays but gets slimmed down to just point at CORTANA.md.
BRAIN.md merges into CORTANA.md (it was already doing the right thing, just in a separate file).
LEARNINGS.md moves to context/learnings-full.md, top 5 promoted to CORTANA.md.

---

## 7. THE MATH

**Before:**
- System prompt: ~1,171 lines (8 files, all loaded every turn)
- Useful per turn: ~200 lines (83% waste)
- Memory search: manual, no index, grep-and-pray

**After:**
- System prompt: ~180 lines (1 file: CORTANA.md)
- Task context: ~100-200 lines (1-2 files from context/, loaded on demand)
- Memory search: indexed, tagged, searchable via memory/index.md
- Total per turn: ~280-380 lines (67-76% reduction)

**Net effect:** More relevant context, less noise, faster responses, fewer token burns.

---

## 8. OPEN QUESTIONS FOR BEN

1. **QMD integration:** OpenClaw's QMD memory backend is configured but I can't see what it stores or retrieves. Should we investigate what it's doing and wire it into Layer 2, or ignore it and use our own index?

2. **Auto-update frequency:** Should CORTANA.md's Current State section update after every task, or only after "significant" tasks? Every task means more writes. Significant only means risk of stale state.

3. **Sub-agent context:** When spawn_task.sh fires a sub-agent, should it auto-load the relevant context/ file based on the task description? Or should the sub-agent prompt always include full context inline?

4. **Retention policy:** 90-day prune for memory/ files. Too aggressive? Too lenient? Some of the research files (competitive analysis, market research) might be useful long-term.

5. **CORTANA.md ownership:** Should this file be the system prompt (CLAUDE.md replacement) or a file that CLAUDE.md points to? The difference is whether OpenClaw/Claude Code loads it automatically or whether I need to read it manually at session start.
