# BRAIN.md - Current State

> Read at session start. Update after completing work. Keep under 60 lines.

## Active Projects
- **Cortana sub-agents:** FIXED 2026-03-03. Use spawn_task.sh → --agent worker. Works.
- **MiMoo:** Same fixes deployed. GitHub updated. Both servers in sync.
- **Context Engine Phase 1:** Complete. context/ files live. CLAUDE.md slimmed.

## Last Completed (2026-03-03)
- Sub-agent infinite recursion FIXED: was using --agent main (shared session = recursion)
- Fix: spawn_task.sh now uses --agent worker + fresh --session-id per run
- worker agent added to openclaw.json (isolated session, no Cortana history contamination)
- Google Calendar via Composio: gcal.py written, create+patch attendee fix working
- tg-reaction-monitor v7: debounced — one alert per incident, not per model retry
- Fixed duplicate monitor process (was doubling every alert)
- MiMoo workspace template: gcal.py, spawn_task.sh, AGENTS.md, TOOLS.md all updated
- Pushed to GitHub (xBenJamminx/mimoo commits fa48d79 + 865b1c3)

## How Sub-Agents Work (CRITICAL — read before delegating)
- Command: bash /root/.openclaw/workspace/lib/spawn_task.sh <topic_id> task
- Uses --agent worker (NOT --agent main — that causes infinite recursion)
- Each spawn gets a fresh session ID — no shared history between workers
- Worker knows it's a worker: has anti-recursion preamble in task
- NEVER call spawn_task.sh from inside a worker

## Google Calendar
- Script: python3 /root/.openclaw/workspace/lib/gcal.py
- Commands: list | events primary 7 | create_one '{...}'
- Calendars: benjoselson@gmail.com (primary), ben@kaleidoco.com, ben@mimoo.ai
- Timezone: America/New_York
- Events land clean (attendee patch runs automatically after create)

## Waiting On
- Ben's pick from top 5 autonomous business ideas
- Twitter @xBenJamminx appeal response

## Recent Decisions
- Sub-agent pattern: worker agent only, never --agent main for spawning
- Fallback chain: claude-cli/sonnet → openrouter/moonshotai/kimi-k2.5 (haiku removed)
- Alert policy: one ⚠️ per incident max, ❌ on full failure only
- Twitter: @BuildsByBen for posting while @xBenJamminx appeal pending

## Key Numbers
- Telegram group: -1003856131939
- Topics: 20=Content, 22=Research, 26=Ideas, 29=Analytics, 31=Business
- Server: 5.78.181.172 (Hetzner CPX21, 4GB)
- Ben's phone: +15168706749

## Flags
- @xBenJamminx suspended, appeal pending
- No Bird CLI until resolved
- Gateway health-monitor: auto-restarts via systemd if it crashes
