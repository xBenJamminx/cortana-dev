# LEARNINGS.md
> Every mistake logged. Every correction applied. An agent that gets smarter every day.

---

## Rules from Mistakes

### 1. Don't hallucinate diagnoses — check the simple explanation first
- **Date:** Feb 2026
- **What happened:** VAPI call returned Call ID: None. Instead of checking whether I called the wrong number (I did — used a made-up number instead of Ben's), I diagnosed it as an "Invalid API Key" and spiraled into a multi-step debugging session that was completely wrong.
- **Root cause:** Jumped to a complex diagnosis without verifying the basics first.
- **Rule:** When something fails, check the simplest explanation first. Wrong input > bad config > broken API. Always verify your own inputs before blaming the system.

### 2. Never guess phone numbers or identifiers
- **Date:** Feb 2026
- **What happened:** When Ben said "call me," I passed +15165808910 — a number I made up — instead of using the default in the script or checking SKILL.md.
- **Root cause:** Hallucinated a phone number instead of reading the config.
- **Rule:** NEVER guess identifiers (phone numbers, IDs, keys). If you don't know it, check the config file or ask. The vapi-call script defaults to Ben's number when called with no arguments.

### 3. Sleep video title cards need separate dark images
- **Date:** Feb 2026
- **What happened:** Title cards were reusing the first scene image (warm candlelit scenes) with only 50% darkening. Result: bright orange backgrounds with unreadable white text.
- **Root cause:** Lazy shortcut — reusing a scene image instead of generating a purpose-built title card.
- **Rule:** Always generate a separate title card image with a dark, muted prompt (deep navy, charcoal, no warm tones). Darken to 75% minimum. The title card sets the tone — it shouldn't look like a random scene with text slapped on it.

### 4. Don't sugarcoat or spin when giving advice
- **Date:** Feb 2026
- **What happened:** When discussing ban evasion on Twitter, initially gave overly optimistic advice ("it's not ban evasion because the account existed before") when the reality was more nuanced. Ben had to push back before I gave the honest assessment.
- **Root cause:** Defaulting to telling the user what they want to hear instead of the full truth.
- **Rule:** Give the honest assessment upfront, including risks. Don't make Ben push back to get the real answer. Lead with the truth, then offer options.

### 5. Verify the actual cause of a suspension/error before diagnosing
- **Date:** Feb 2026
- **What happened:** Assumed @xBenJamminx suspension was caused by automation (Bird CLI / Composio API) when it was actually a content violation (tweet about using X API for free). This led to wrong advice about using @CortanaOps.
- **Root cause:** Working from assumptions stored in MEMORY.md instead of confirming with Ben.
- **Rule:** Don't assume you know the cause of something from memory. Confirm with the user before building a strategy on top of an assumption.

---

### 6. Context window is a resource -- treat it like disk space
- **Date:** Feb 2026
- **What happened:** Sessions regularly hit 150K+ context by loading every file "just in case" and doing heavy work inline instead of delegating.
- **Root cause:** No discipline around what gets loaded into context vs read from external memory.
- **Rule:** Read BRAIN.md for quick state. Only load files the current task needs. Heavy work goes to subagents. Update BRAIN.md after completing work so next session doesn't have to reload.

### 7. Heartbeats should be fast, not thorough
- **Date:** Feb 2026
- **What happened:** Heartbeat check-ins loaded SOUL.md, MEMORY.md, ran checks, burned tokens, and took 30+ seconds.
- **Root cause:** Heartbeat was designed as a "do everything" moment instead of a quick pulse check.
- **Rule:** Heartbeats target <3 seconds. Check for messages, respond if needed, HEARTBEAT_OK if not. Heavy checks only when idle 2+ hours.

### 8. Check BRAIN.md before doing work — don't duplicate what a previous session already did
- **Date:** Feb 2026
- **What happened:** Ben asked about LEARNINGS.md. A previous session already discussed it and started implementation. This session repeated the entire conversation and rebuilt LEARNINGS.md from scratch without checking if it already existed.
- **Root cause:** Didn't check BRAIN.md or existing files before starting work. Assumed the task was new.
- **Rule:** Before implementing anything, check if it already exists. Read BRAIN.md, check the workspace, grep for related files. If a previous session already did the work, build on it instead of starting over.

### 9. Always spawn background sub-agents for tasks -- stay available
- **Date:** Feb 2026
- **What happened:** Ben sends a task, I do all the work inline, he has to wait until I'm done before sending the next thing. Everything runs sequentially. He pointed out this is a huge bottleneck.
- **Root cause:** Never used `run_in_background: true` on the Task tool. Assumed sub-agents had tool limitations (they don't -- tested and confirmed: Read, Write, Edit, Bash, Grep all work).
- **Rule:** DEFAULT behavior: When Ben sends a task, immediately spawn a background sub-agent to do the work. Acknowledge the task ("On it"), launch the agent, and stay responsive. Check the output when the agent finishes and report results. Only do work inline if it's a quick 1-2 step thing that would take longer to delegate than to just do.
- **Note (Feb 25):** Background sub-agents were failing silently on the old 2GB server (OOM kills). Server upgraded to 4GB (CPX21) and background agents now work reliably. Confirmed: sub-agent wrote files, ran bash, sent Telegram -- all from background.


### 10. Kill stale Claude processes after SSH test commands
- **Date:** Feb 2026
- **What happened:** Ran Claude CLI test commands via SSH from a remote machine. The SSH session ended but the spawned claude processes kept running as zombies (~250MB each). Two stale processes blocked the Telegram message queue -- Cortana received messages but could not process them because resources were consumed by orphans.
- **Root cause:** Running `ssh cortana "claude -p ..."` spawns a child process. If the SSH connection drops or the command backgrounds, the claude process persists. Multiple orphans stack up and compete with the live openclaw session for memory and API auth.
- **Rule:** After running any `claude -p` commands via SSH, always verify cleanup: `ps aux | grep claude | grep -v grep`. Kill any processes that are not the active openclaw-managed session. Never leave test claude processes running.

### 11. Server migration: snapshot + new server, not in-place resize
- **Date:** Feb 2026
- **What happened:** Needed to upgrade from Hetzner CPX11 (2GB) to CPX21 (4GB). In-place rescaling was unavailable at the current datacenter location (ASH). Had to take a snapshot, create a new server in HIL, restore from snapshot, update SSH configs, then delete the old server.
- **Root cause:** Hetzner in-place rescaling has location-dependent availability. Some tiers are not available in all datacenters.
- **Rule:** When upgrading Hetzner servers: (1) snapshot first, (2) create new server from snapshot in a location where the target tier is available, (3) verify ALL services and files, (4) update DNS/SSH configs with new IP, (5) delete old server + snapshot. New IP: 5.78.181.172 (HIL-DC1, Hillsboro OR).
---

## Format for New Entries

```
### N. Short rule title
- **Date:** Month Year
- **What happened:** [factual description]
- **Root cause:** [why it went wrong]
- **Rule:** [the correction to follow going forward]
```

## 12. run_in_background: true DOES NOT WORK with CLI backend (2026-02-25)
- Claude Code's Task tool with run_in_background: true spawns child processes
- When the parent claude -p session returns its response, openclaw considers the turn done
- The parent process exits and ALL background child processes are killed
- Sub-agent logs show "[Request interrupted by user]" at the exact moment the parent responds
- SOLUTION: Use openclaw's native sessions_spawn tool instead
- sessions_spawn creates isolated sessions managed by openclaw, independent of any single claude -p invocation
- Results auto-announce back to the requester session

### 13. Silent compaction hang on large contexts — reduce resume watchdog timeout
- **Date:** Feb 2026
- **What happened:** Cortana went silent for 15+ minutes after a big Notion task (~130 turns, 116K tokens). Ben had to manually check if the server was down. The session wasnt dead — the watchdog eventually killed it and Haiku responded fine within 15 seconds.


### 13. Silent compaction hang on large contexts -- reduce resume watchdog timeout
- **Date:** Feb 2026
- **What happened:** Cortana went silent for 15+ minutes after a big Notion task (~130 turns, 116K tokens). Ben had to manually check if the server was down. The session was not dead -- the watchdog eventually killed it and Haiku responded fine within 15 seconds.
- **Root cause:** At ~116K tokens, Claude CLI safeguard compaction mode triggered on session resume. The compaction API call hung silently with zero output. The watchdog maxMs was set to 900000ms (15 min), so Cortana was frozen for the full 15 minutes before fallback.
- **Rule:** Keep long tasks in sub-agents (sessions_spawn) to prevent main session context bloat. Changed resume watchdog maxMs from 900000ms to 120000ms (2 min) in openclaw.json. If Sonnet hangs on resume, fail fast and let Haiku take over instead of leaving the user waiting.
## 13. Orchestrator pattern via spawn_task.sh (2026-02-27)
- Problem: Cortana kept doing heavy work inline, hanging for 5min, getting watchdog-killed
- Root cause: all sub-agent mechanisms were broken:
  - run_in_background: true → children killed when parent claude -p exits
  - sessions_spawn → mentioned in system prompt but NOT a real callable tool in Claude Code
  - sleep hacks → block the main session, hit watchdog timeout
- Solution: spawn_task.sh wraps `openclaw agent --agent main --message "task"` in nohup
  - Sub-agent runs as a completely independent openclaw session
  - Task message embeds reporting instructions (use telegram.py --topic X to send results)
  - Returns in milliseconds, Cortana stays available
  - Sub-agent reports back to the right Telegram topic when done
- Location: /root/.openclaw/workspace/lib/spawn_task.sh
- Usage: bash /root/.openclaw/workspace/lib/spawn_task.sh <topic_id> "task description"
- Watchdog also lowered: fresh 300s→60s, maxMs 900s→180s (fail fast instead of hanging)
- CLAUDE.md updated: Cortana is orchestrator not worker, anything >10s = spawn_task.sh
