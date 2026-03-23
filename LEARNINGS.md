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

### 14. OpenClaw default session config wipes context — change it immediately
- **Date:** Mar 2026
- **What happened:** Ben kept losing conversation context between messages, sometimes even minutes apart. Cortana would respond to "Huh?" with no idea what they'd been discussing. Multi-day conversations (like the 50 business ideas research) vanished completely after gaps.
- **Root cause:** OpenClaw ships with session defaults that aggressively wipe sessions:
  - `reset.mode: "daily"` — wipes ALL sessions at 4am every day
  - `idleMinutes: 60` (default) — any gap >1 hour between messages = brand new session
  - These defaults applied to ALL session types (direct, group, thread/topic)
  - No `session` block existed in openclaw.json, so all defaults were active
- **How sessions work:** Each Telegram message spawns a fresh `claude -p --resume {sessionId}` process. If the session is "fresh" (not stale per idle/daily rules), it reuses the existing Claude CLI session ID. If stale, it generates a new UUID and all prior context is gone.
- **Fix applied:** Added `session` config block to `/root/.openclaw/openclaw.json`:
  - `reset.mode: "idle"` (no more 4am daily wipe)
  - `reset.idleMinutes: 1440` (24 hours instead of 60 minutes)
  - Applied via `resetByType` to thread, group, and direct sessions
- **Rule:** After any OpenClaw install or upgrade, check `openclaw.json` for a `session` block. If missing, add one with idle mode and a high timeout. The defaults are designed for casual chatbots, not persistent assistants.
- **Key code locations:**
  - Freshness check: `sessions-DOpDuDMA.js` line 327 `evaluateSessionFreshness()`
  - Session key derivation: same file line 349 `deriveSessionKey()`
  - CLI resume logic: `reply-YQvtZDnf.js` line 31339 `useResume` flag
- **Note:** Gateway restart kills the current session (ironic when fixing session persistence). The fix survives restarts since it's in the config file. Gateway auto-restarts via systemd.

## 13. Never say "let me check" then go silent (2026-03-09)
If you search memory/files and find nothing, report the failure in the SAME response. "Searched memory, don't have it — what's the URL?" is the correct answer. Going silent after a failed search made Ben think the system was broken.

### 15. Sticky model fallback poisons ALL sessions silently (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Cortana was responding poorly for weeks — stalling, giving shallow answers, using NO_REPLY to skip messages. Investigation revealed she was running on Kimi K2.5 (OpenRouter fallback) instead of Claude across ALL 6 active Telegram topics.
- **Root cause:** OpenClaw's fallback system ( in openclaw.json) is STICKY. When Claude's API hiccupped once, the gateway switched to the fallback model. That model override was saved in  per-session and NEVER reverted — even after Claude came back online. Every topic accumulated the override independently.
- **Fields that get stuck:** , , , , , , 
- **Fix applied:** Removed all fallbacks from config (). Cleaned all sticky model overrides from sessions.json. Reset all session bindings so topics start fresh.
- **Rule:** Do NOT use model fallbacks in openclaw.json. A silent degradation to a worse model is far more damaging than a visible failure. If Claude goes down, it should fail loud — not pretend to work while running on a model that doesn't understand the system prompt.
- **Diagnostic:** Check  for any session with a  field that doesn't match the primary. Or check openclaw session files for  entries showing the wrong provider.

### 16. NO_REPLY token suppresses responses entirely (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Ben sent a detailed content brief. Cortana reacted (ack emoji) but never responded. Session file showed the model returned  — a single token that tells the gateway to suppress the response completely.
- **Root cause:**  is a built-in openclaw feature (defined in ). When the model outputs only , the gateway treats it as this message doesnt need a response" and sends nothing to Telegram. The fallback model (Kimi) didnt understand Cortanas rules and used it inappropriately.
- **Fix applied:** Added explicit rule to CLAUDE.md Core Rule #1: "NEVER output NO_REPLY."
- **Rule:** If an agent appears to receive a message (shows ack reaction) but never responds, check the session `.jsonl` file for `NO_REPLY` in the assistant content. The fix is a system prompt rule banning the token.

### 17. Watchdog kills working Claude after 180s of no streamed output (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Claude was actively working (reading files, calling tools, thinking) but the openclaw watchdog killed it after 180 seconds because no text had been streamed to stdout yet. Error: "CLI produced no output for 180s and was terminated."
- **Root cause:** The `noOutputTimeoutMs` default is 180000ms (3 min). This timer counts time since the LAST text output — tool calls, file reads, and thinking dont count as output. Complex tasks that require multiple tool calls before generating text will always hit this limit.


### 15. Sticky model fallback poisons ALL sessions silently (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Cortana was responding poorly for weeks -- stalling, giving shallow answers, using NO_REPLY to skip messages. Investigation revealed she was running on Kimi K2.5 (OpenRouter fallback) instead of Claude across ALL 6 active Telegram topics.
- **Root cause:** OpenClaw's fallback system (model.fallbacks in openclaw.json) is STICKY. When Claude's API hiccupped once, the gateway switched to the fallback model. That model override was saved in sessions.json per-session and NEVER reverted -- even after Claude came back online. Every topic accumulated the override independently.
- **Fields that get stuck:** model, modelProvider, fallbackNoticeSelectedModel, fallbackNoticeActiveModel, cliSessionIds, claudeCliSessionId, systemPromptReport
- **Fix applied:** Removed all fallbacks from config (model.fallbacks: []). Cleaned all sticky model overrides from sessions.json. Reset all session bindings so topics start fresh.
- **Rule:** Do NOT use model fallbacks in openclaw.json. A silent degradation to a worse model is far more damaging than a visible failure. If Claude goes down, it should fail loud -- not pretend to work while running on a model that doesn't understand the system prompt.
- **Diagnostic:** Check sessions.json for any session with a model field that doesn't match the primary. Or check openclaw session files for model-snapshot entries showing the wrong provider.

### 16. NO_REPLY token suppresses responses entirely (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Ben sent a detailed content brief. Cortana reacted (ack emoji) but never responded. Session file showed the model returned NO_REPLY -- a single token that tells the gateway to suppress the response completely.
- **Root cause:** NO_REPLY is a built-in openclaw feature (defined in tokens-rNiM9362.js). When the model outputs only NO_REPLY, the gateway treats it as "this message doesn't need a response" and sends nothing to Telegram. The fallback model (Kimi) didn't understand Cortana's rules and used it inappropriately.
- **Fix applied:** Added explicit rule to CLAUDE.md Core Rule #1: "NEVER output NO_REPLY."
- **Rule:** If an agent appears to receive a message (shows ack reaction) but never responds, check the session .jsonl file for NO_REPLY in the assistant content. The fix is a system prompt rule banning the token.

### 17. Watchdog kills working Claude after 180s of no streamed output (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Claude was actively working (reading files, calling tools, thinking) but the openclaw watchdog killed it after 180 seconds because no text had been streamed to stdout yet. Error: "CLI produced no output for 180s and was terminated."
- **Root cause:** The noOutputTimeoutMs default is 180000ms (3 min). This timer counts time since the LAST text output -- tool calls, file reads, and thinking don't count as "output." Complex tasks that require multiple tool calls before generating text will always hit this limit.
- **Fix applied:** Could NOT set via config -- noOutputTimeoutSeconds/noOutputTimeoutMs are not exposed as valid config keys in openclaw v2026.3.8. The 180s default is hardcoded. Workaround: ensure Cortana always sends an acknowledgment message BEFORE doing heavy tool work, which resets the watchdog timer.
- **Rule:** If Cortana is getting killed mid-task with "no output for 180s," increase noOutputTimeoutSeconds. The default 180s is too short for tasks involving file reads, web fetches, or multi-step tool use.

### 18. Typing indicator service crash-looping silently (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Ben couldn't see any typing indicators when Cortana was working. The tg-reaction-monitor.service had been crash-looping (4,500+ restart attempts) because the script path was wrong.
- **Root cause:** tg-reaction-monitor.py was moved from /root/.openclaw/workspace/scripts/ to /root/.openclaw/workspace/automation/social/ but the systemd service file still pointed to the old path.
- **Fix applied:** Updated the ExecStart path in /etc/systemd/system/tg-reaction-monitor.service.
- **Rule:** After moving ANY script that has a systemd service, update the service file path. Check crash-looping services with systemctl status -- a restart counter in the thousands means it's been broken for a long time.

### 19. Session symlink mapping between openclaw and Claude CLI (2026-03-09)
- **Date:** Mar 2026
- **What happened:** Cortana responded to the first message in a topic but crashed on every subsequent message with "No conversation found with session ID."
- **Root cause:** Openclaw creates its own session ID (e.g. 76063dde) but Claude CLI creates a DIFFERENT session ID (e.g. 69761d4f). Normally openclaw creates a symlink in /root/.openclaw/agents/main/sessions/ from its ID to the Claude CLI session file. When sessions are cleared/reset, the symlink is lost and claude --resume fails because Claude CLI doesn't know the openclaw ID.
- **Fix applied:** Manually created symlink and updated cliSessionIds/claudeCliSessionId in sessions.json.
- **Rule:** Never manually clear session fields in sessions.json without understanding the symlink mapping. If sessions must be reset, let the gateway create fresh ones by restarting -- don't surgically remove fields. If resume fails with "No conversation found," check if the symlink exists in /root/.openclaw/agents/main/sessions/.

### 20. noOutputTimeoutSeconds is wrong key — use cliBackends.reliability.watchdog (2026-03-16)
- **Date:** Mar 2026
- **What happened:** Tried to fix 180s watchdog by setting agents.defaults.noOutputTimeoutSeconds: 600 — openclaw rejected it as an unrecognized key and crashed on startup.
- **Root cause:** The correct config path is agents.defaults.cliBackends.claude-cli.reliability.watchdog.fresh.noOutputTimeoutMs (and .resume). The internal variable is in milliseconds and lives in the reliability.watchdog nested object.
- **Fix applied:** Set noOutputTimeoutMs: 600000 under agents.defaults.cliBackends.claude-cli.reliability.watchdog.fresh and .resume in openclaw.json.
- **Rule:** When setting the watchdog timeout, use agents.defaults.cliBackends.claude-cli.reliability.watchdog.{fresh|resume}.noOutputTimeoutMs. Value is in milliseconds. No max limit (unlike per-provider timeout which caps at 120000ms).


### 21. Never claim missing info without searching first (2026-03-18)
- **Date:** Mar 2026
- **What happened:** Ben asked Cortana to update Google Sheets and Notion. Cortana said "I don't have those IDs" and asked Ben for them — even though the IDs, credentials, and full sync process were documented in context/fam-sync-process.md, which she wrote herself days earlier.
- **Root cause:** Cortana didn't check her own context/ files before claiming she didn't have the information. The Task Router also had no entry pointing FAM sync tasks to fam-sync-process.md.
- **Fix applied:** Added Task Router entry for FAM sync → context/fam-sync-process.md. Added Active Mistake #0: never claim missing info without searching context/, memory/, workspace, and telecrawl first.
- **Rule:** Before saying "I don't have X," search for it. grep the workspace, check context/ files, check memory/, query telecrawl. The information is almost always already stored somewhere. Only ask Ben after an exhaustive search that came up empty.

### 22. Never claim tools are disabled without trying them (2026-03-18)
- **Date:** Mar 2026
- **What happened:** Ben asked Cortana to check Slack. Cortana said "Tools are disabled in this session" — but tools were fully available. She hallucinated the limitation instead of attempting the tool call.
- **Root cause:** After a 529 overloaded error crashed the previous session, the fresh session started uncertain about its environment. Sonnet hedged by claiming tools were disabled rather than trying them.
- **Rule:** You ALWAYS have tool access. Never claim tools are disabled or unavailable — try them first. If a tool actually fails, report the real error message. Hedging about capabilities wastes Ben's time and erodes trust.

### 23. Never write to external systems without Ben's approval (2026-03-18)
- **Date:** Mar 2026
- **What happened:** Ben asked Cortana to update Google Sheets and Notion. Cortana ran the full sync process and pushed 24 Notion status changes and 16 QA Sheet updates without showing Ben the proposed changes first.
- **Root cause:** fam-sync-process.md had no approval gate between building the delta list (Step 3) and writing to Notion (Step 4). CLAUDE.md had no general rule about external write access requiring approval.
- **Fix applied:** Added Step 3.5 (approval gate) to fam-sync-process.md. Added Core Rule #8 to CLAUDE.md: never write to external systems without showing Ben first.
- **Rule:** Read access to external systems is free. Write access always requires Ben to review and approve the proposed changes first. Show the delta, wait for the go-ahead, then push.