# Context: Server & Infrastructure

## Server
- Hetzner CPX21 (4GB RAM, 3 vCPU, HIL-DC1 Hillsboro OR)
- IP: 5.78.181.172 (previously 178.156.181.67)
- SSH root, key auth, UFW port 22 only
- OpenClaw gateway port 18789
- VAPI tools port 8787 (via Cloudflare tunnel)

## OpenClaw Config
- Config file: `/root/.openclaw/openclaw.json`
- Session reset: idle mode, 1440min timeout (24hrs)
- Primary model: claude-cli/sonnet
- Fallbacks: haiku -> gemini-3-flash -> openrouter/auto
- Watchdog: fresh 90-240s, resume 90-180s
- Max concurrent: 4 agents, 8 subagents

## Key Processes
- Gateway: systemd managed, auto-restarts
- Internal health-monitor: still crashes ~once per session (code 1, unknown trigger)
- Watchdog: fresh 60s timeout, maxMs 180s (fail fast)

## Sub-Agent Spawning
- `bash /root/.openclaw/workspace/lib/spawn_task.sh <topic_id> "task"`
- Wraps `openclaw agent --agent main --message "task"` in nohup
- Returns immediately, sub-agent runs independently
- Sub-agent reports to Telegram topic when done

## Disk
- Target: keep under 70%
- Memory dir: 3.9MB across 64 files

## Migration Notes
- In-place resize unavailable at some datacenters
- Process: snapshot -> new server from snapshot -> verify -> update SSH/DNS -> delete old
