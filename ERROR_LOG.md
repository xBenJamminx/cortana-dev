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
2. Saves summaries to `/root/clawd/memory/spreadsheets/`
3. Allows agent to read processed files instead

**Script location:** `/root/clawd/scripts/excel-processor.py`

**Usage:**
```bash
/root/clawd/workspace-os/venv/bin/python /root/clawd/scripts/excel-processor.py /path/to/file.csv
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
- Watchdog script runs every 2 min: `/root/clawd/scripts/watchdog.py`
- Kills processes running > 5 min (MAX_CLAUDE_RUNTIME = 300)
- Auto-restarts gateway after killing stuck processes

**Status:** Watchdog should catch this automatically. If it keeps happening, investigate:
1. Is watchdog cron running? `crontab -l | grep watchdog`
2. Check watchdog logs: `tail -50 /root/clawd/logs/watchdog.log`
3. May need to reduce MAX_CLAUDE_RUNTIME if 5 min is too long


**Additional Finding:**
Crontab was overwritten - watchdog cron job was missing for ~3 hours. Other scripts (content-ideas-generator, competitor-monitor, real-trends-monitor) replaced our cron entries.

**Lesson Learned:**
When adding new cron jobs, ALWAYS use `crontab -l` first and APPEND, dont replace:

---

## 2026-02-04 17:16:04: WARNING Alert

**Message:** Killed 1 stuck process(es) and restarted gateway

