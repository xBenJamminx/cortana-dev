---
name: system-health
description: Check Cortana's system health status (gateway, processes, sessions, disk). Use when user asks about health, status, or if something seems wrong. Triggers on "/health", "how's your health", "are you ok", "check status", "system status".
---

# System Health Check

Check Cortana's current system health and report status.

## When to Use

- User asks: "/health", "how are you", "are you ok", "system status", "check health"
- User reports issues: "you seem slow", "are you stuck", "not responding"
- Proactive check if you suspect something is wrong

## How to Use

Run the health check script:

```bash
bash /root/.openclaw/workspace/scripts/health-check.sh
```

## Output Format

Report the results in a clear, concise format:

```
System Health Check

Gateway: [✅ Running | ❌ Down]
Processes: [X active]
Sessions: [Largest file size]
Activity: [Recent | Idle]
Disk: [X% used, XGB free]

[Any warnings or issues detected]
```

## When Issues Detected

If the health check reveals problems:

1. **Gateway down** → Suggest manual restart: "Gateway appears down. Would you like me to restart it?"
2. **Large session** (>20MB) → Suggest session reset: "Session file is large (XMB). This could cause issues. Reset recommended."
3. **No recent activity** → "No recent CLI activity detected. I may be idle or stuck."
4. **High disk usage** → "Disk space is running low (X% used)."

## Manual Actions Available

If user confirms, you can run:

- **Restart gateway**: `systemctl restart openclaw-gateway && sleep 5 && systemctl status openclaw-gateway`
- **Reset session**: Edit `/root/.openclaw/agents/main/sessions/sessions.json` to clear sessionId/sessionFile
- **Kill stuck processes**: `pkill -9 claude` (use with caution)

## Notes

- This is a diagnostic tool, not a fix-all
- Always ask before taking disruptive actions (restarts, kills)
- Report findings clearly and suggest next steps
