# Cortana/OpenClaw Error Log

This document tracks errors encountered and their solutions for future reference.

---

## 2026-02-04: OAuth Token Expired

**Error:**
```
Failed to authenticate. API Error: 401 {"type":"error","error":{"type":"authentication_error","message":"OAuth token has expired. Please obtain a new token or refresh your existing token."}}
```

**Cause:** Claude CLI OAuth token expired after some time.

**Solution:** Re-authenticate the Claude CLI on the server:
```bash
ssh openclaw
claude login
# Complete OAuth flow in browser
```

**Prevention:** OAuth tokens expire periodically. May need to set up automatic token refresh or monitor for auth errors.

---

## 2026-02-04: E2BIG - File Too Large for CLI Args

**Error:**
```
Embedded agent failed before reply: spawn E2BIG
Error: spawn E2BIG at ChildProcess.spawn
```

**Cause:** User sent a large file (1.2MB CSV) via Telegram. OpenClaw passes file content as command line arguments to the Claude CLI, but Linux has a max argument size limit (~2MB).

**Solution:** Created an Excel/CSV processor that:
1. Pre-processes large spreadsheets
2. Saves summaries to `/root/.openclaw/workspace/memory/spreadsheets/`
3. Allows agent to read processed files instead

**Script location:** `/root/.openclaw/workspace/scripts/excel-processor.py`

**Usage:**
```bash
/root/.openclaw/workspace/workspace-os/venv/bin/python /root/.openclaw/workspace/scripts/excel-processor.py /path/to/file.csv
```

**Prevention:** Need to implement automatic file preprocessing before messages reach the CLI, or configure openclaw to handle large attachments differently.

---

## 2026-02-04: CLI Failed / Typing TTL Timeout

**Error:**
```
typing TTL reached (2m); stopping typing indicator
FailoverError: CLI failed.
```

**Cause:** Claude CLI processes getting stuck or taking too long to respond, causing 2-minute timeout.

**Solution:** 
1. Kill stuck claude processes: `pkill -9 claude`
2. Clear session state: `rm -rf /root/.claude/projects/*`
3. Restart gateway: `systemctl restart openclaw-gateway`

**Prevention:** Monitor for stuck processes. May need to adjust timeout settings or investigate why CLI hangs.

---

## Common Troubleshooting Commands

```bash
# Check gateway status
systemctl status openclaw-gateway

# View recent logs
journalctl -u openclaw-gateway -n 50 --no-pager

# Check detailed log file
tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# Search for errors
cat /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i error | tail -20

# Test Claude CLI directly
echo "test" | claude -p --output-format json

# Kill stuck claude processes
pkill -9 claude

# Restart gateway
systemctl restart openclaw-gateway

# Check VAPI tools server
ps aux | grep -E 'uvicorn|8787'

# Check Cloudflare tunnel
ps aux | grep cloudflared
```

---

*Last updated: 2026-02-04*

---

## 2026-02-04 03:58:05: WARNING Alert

**Message:** Killed 1 stuck process(es) and restarted gateway


---

## 2026-02-04 15:37 UTC: Stuck Claude Process - Typing TTL Timeout

**Symptoms:**
- Cortana not responding to Telegram messages
- Gateway logs show: `typing TTL reached (2m); stopping typing indicator`
- `ps aux | grep claude` shows process running for extended time

**Root Cause:**
Claude CLI process hung/stuck during response generation. No output for 2+ minutes.

**Detection:**
```bash
# Check for stuck processes (running > 5 min)
ps -eo pid,etimes,cmd | grep claude | awk "$2 > 300 {print}"

# Check gateway logs for TTL warnings
journalctl -u openclaw-gateway --since "5 min ago" | grep "TTL reached"
```

**Fix:**
```bash
# Kill stuck claude processes and restart gateway
pkill -9 -f "claude"
systemctl restart openclaw-gateway
```

**Prevention:**
- Watchdog script runs every 2 min: `/root/.openclaw/workspace/scripts/watchdog.py`
- Kills processes running > 5 min (MAX_CLAUDE_RUNTIME = 300)
- Auto-restarts gateway after killing stuck processes

**Status:** Watchdog should catch this automatically. If it keeps happening, investigate:
1. Is watchdog cron running? `crontab -l | grep watchdog`
2. Check watchdog logs: `tail -50 /root/.openclaw/workspace/logs/watchdog.log`
3. May need to reduce MAX_CLAUDE_RUNTIME if 5 min is too long


**Additional Finding:**
Crontab was overwritten - watchdog cron job was missing for ~3 hours. Other scripts (content-ideas-generator, competitor-monitor, real-trends-monitor) replaced our cron entries.

**Lesson Learned:**
When adding new cron jobs, ALWAYS use `crontab -l` first and APPEND, dont replace:

---

## 2026-02-04 17:16:04: WARNING Alert

**Message:** Killed 1 stuck process(es) and restarted gateway


---

## 2026-02-09 13:06:05: WARNING Alert

**Message:** Killed 1 stuck process(es) and restarted gateway


---

## 2026-02-10 23:26:08: CRITICAL Alert

**Message:** Gateway restart FAILED (failure #1).
Service: activating/start-pre
HTTP: <urlopen error [Errno 111] Connection refused>
Manual intervention may be needed.


---

## 2026-02-10 23:32:13: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: active/running
HTTP probe: <urlopen error [Errno 111] Connection refused>


---

## 2026-02-17 19:57:33: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 175.0h old (max 26h)
  - Content intel: 156.0h old (max 6h)
  - Twitter monitor: 156.9h old (max 8h)
  - YouTube monitor: 158.0h old (max 8h)
  - Watchdog itself: 68.0h old (max 0.1h)


---

## 2026-02-17 20:58:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 176.0h old (max 26h)
  - Twitter monitor: 157.9h old (max 8h)
  - YouTube monitor: 159.0h old (max 8h)


---

## 2026-02-17 22:00:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 177.0h old (max 26h)
  - Twitter monitor: 159.0h old (max 8h)
  - YouTube monitor: 160.0h old (max 8h)


---

## 2026-02-17 23:00:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 178.0h old (max 26h)
  - Twitter monitor: 160.0h old (max 8h)
  - YouTube monitor: 161.0h old (max 8h)


---

## 2026-02-18 00:02:01: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 179.0h old (max 26h)
  - Twitter monitor: 161.0h old (max 8h)


---

## 2026-02-18 01:02:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 180.0h old (max 26h)


---

## 2026-02-18 02:04:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 181.1h old (max 26h)


---

## 2026-02-18 03:06:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 182.1h old (max 26h)


---

## 2026-02-18 04:08:01: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 183.1h old (max 26h)


---

## 2026-02-18 05:08:01: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 184.1h old (max 26h)


---

## 2026-02-18 06:08:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 185.1h old (max 26h)


---

## 2026-02-18 07:08:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 186.1h old (max 26h)


---

## 2026-02-18 08:10:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 187.2h old (max 26h)


---

## 2026-02-18 09:10:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 188.2h old (max 26h)


---

## 2026-02-18 10:12:02: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 189.2h old (max 26h)


---

## 2026-02-18 10:34:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >1800s


---

## 2026-02-18 11:14:01: WARNING Alert

**Message:** Stale cron jobs detected:
  - Morning briefing: 190.2h old (max 26h)


---

## 2026-02-18 19:00:12: CRITICAL Alert

**Message:** Gateway restart FAILED (failure #1).
Service: deactivating/stop
HTTP: None
Manual intervention may be needed.


---

## 2026-02-18 19:58:08: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: activating/start-pre
HTTP probe: <urlopen error [Errno 111] Connection refused>


---

## 2026-02-19 04:00:20: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-19 16:00:14: CRITICAL Alert

**Message:** Gateway restart FAILED (failure #1).
Service: deactivating/stop
HTTP: None
Manual intervention may be needed.


---

## 2026-02-20 05:00:13: CRITICAL Alert

**Message:** Gateway restart FAILED (failure #1).
Service: deactivating/stop
HTTP: None
Manual intervention may be needed.


---

## 2026-02-20 16:00:14: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-20 20:00:19: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-20 20:28:02: WARNING Alert

**Message:** Killed 2 stuck claude process(es) running >600s


---

## 2026-02-20 21:06:15: CRITICAL Alert

**Message:** Gateway restart FAILED (failure #1).
Service: deactivating/stop
HTTP: None
Manual intervention may be needed.


---

## 2026-02-20 23:34:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-20 23:52:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-21 00:00:15: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-21 00:16:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-21 00:30:02: WARNING Alert

**Message:** Killed 2 stuck claude process(es) running >600s


---

## 2026-02-21 00:44:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-21 01:06:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-21 02:00:14: CRITICAL Alert

**Message:** Gateway restart FAILED (failure #1).
Service: deactivating/stop
HTTP: None
Manual intervention may be needed.


---

## 2026-02-21 02:30:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-21 02:44:02: WARNING Alert

**Message:** Killed 2 stuck claude process(es) running >600s


---

## 2026-02-21 03:00:02: WARNING Alert

**Message:** Killed 2 stuck claude process(es) running >600s


---

## 2026-02-21 03:42:02: WARNING Alert

**Message:** Killed 2 stuck claude process(es) running >600s


---

## 2026-02-21 05:00:19: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-21 05:12:11: CRITICAL Alert

**Message:** Gateway restart FAILED (failure #1).
Service: deactivating/stop
HTTP: None
Manual intervention may be needed.


---

## 2026-02-21 05:56:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-21 07:00:12: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-22 22:32:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-22 23:30:01: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-23 13:00:12: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-23 16:00:13: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-23 18:00:13: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-23 23:36:01: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-24 00:26:02: WARNING Alert

**Message:** Hung session detected: claude process active but log silent for 330s — restarting


---

## 2026-02-24 01:00:12: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-24 20:28:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >600s


---

## 2026-02-24 22:00:12: WARNING Alert

**Message:** Gateway was down (failure #1) — auto-restarted successfully.
Service was: deactivating/stop
HTTP probe: None


---

## 2026-02-25 19:18: Server Migration (CPX11 -> CPX21)

**Issue:** Background sub-agents failing silently. Cortana would spawn run_in_background:true Task agents but they would die without output or error.

**Root cause:** OOM on 2GB RAM server. openclaw-gateway (470MB) + parent Claude process + background child Claude process exceeded available memory. OS silently killed the child process. Blocking sub-agents worked because they ran sequentially, not concurrently.

**Fix:** Migrated to Hetzner CPX21 (4GB RAM, 3 vCPU) at HIL-DC1. New IP: 5.78.181.172. Background agents confirmed working post-migration.

**Additional issue found:** SSH-spawned "claude -p" test commands left orphan processes (~250MB each) running after SSH disconnected. These zombies blocked the Telegram message queue. Fixed by killing stale processes.

**Prevention:**
- Server now has 4GB RAM (3.7GB usable), ~2.9GB available at idle
- After any SSH claude tests: ps aux | grep claude | grep -v grep -- and kill orphans
- Monitor memory: if available drops below 500MB, investigate

---

## 2026-02-27 03:45:02: WARNING Alert

**Message:** Killed 1 stuck claude process(es) running >3600s
---

## 2026-02-27: Sub-agent failures + repeated watchdog timeouts

### What happened
Cortana was repeatedly failing on heavy tasks (image gen, X API calls, video work).
Pattern: she'd try to do the work inline → bash command would hang → watchdog killed her after 300s → openclaw sent error to TG → cycle repeated.

### Root cause
All three sub-agent mechanisms she was trying to use were broken:
1. `run_in_background: true` (Task tool) — child processes get killed the instant the parent claude -p session returns its response. Logs show "[Request interrupted by user]" at exactly that moment.
2. `sessions_spawn` — referenced in openclaw system prompt injection but is NOT an actual callable tool in Claude Code's tool list. She'd see it mentioned but couldn't call it.
3. Sleep hacks (`sleep 370 && script.py`) — blocked the main session, hit the 300s watchdog.

### Symptoms
- Repeated `cli watchdog timeout` in gateway logs
- Sub-agent JSONL files show "[Request interrupted by user for tool use]" at moment parent responds
- Zombie bash processes (`sleep 750`, `sleep 370`) accumulating on server
- X API rate limits burned by repeated zombie script spawns

### Fix
1. Created `/root/.openclaw/workspace/lib/spawn_task.sh`
   - Wraps `nohup openclaw agent --agent main --message "task + reporting instructions"`
   - Sub-agent runs as completely independent openclaw session
   - Task message embeds instructions to use telegram.py to report results back
   - Returns immediately, Cortana stays available
2. Lowered watchdog timeouts (openclaw.json):
   - fresh: 300s min → 60s min, 900s max → 180s max
   - resume: 120s min → 60s min, 300s max → 120s max
3. Updated CLAUDE.md with orchestrator pattern:
   - Cortana = orchestrator, not worker
   - Anything >10s = spawn_task.sh
   - Examples of image gen, research, API work delegation

### Verified working
Test run: `spawn_task.sh 1 "run echo hello world and report back"` — sub-agent completed independently and sent results to Telegram topic.
