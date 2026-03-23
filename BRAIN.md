# BRAIN.md - Current State

> Read at session start. Update after completing work. Keep under 60 lines.

## Telecrawl Active 💜
- **What:** Real-time message memory for Telegram groups (like discrawl)
- **DB:** `~/.openclaw/memory/telecrawl.db` (SQLite + FTS5)
- **Repo:** https://github.com/xBenJamminx/telecrawl
- **Natural language:** Just ask me "what did we decide about X?" and I'll search
- **Code:** `from core.utils.memory_helper import search_conversation_memory`

## Memory Usage
- I auto-log all messages to telecrawl.db with chat_id + topic_id
- Ask naturally: "what did we say about telegaf yesterday?" or "remind me of that decision"
- I query internally and surface relevant context

## Active Projects
- **Cortana sub-agents:** FIXED 2026-03-03. Use spawn_task.sh → --agent worker. Works.
- **MiMoo:** Same fixes deployed. GitHub updated. Both servers in sync.
- **Context Engine Phase 1:** Complete. context/ files live. CLAUDE.md slimmed.

## Last Completed (2026-03-08)
- **Workspace Refactor:** lib/ → core/, scripts/ → automation/
- New structure: core/{integrations,content,fathom,monitoring,utils}
- All imports updated: `from lib.X` → `from core.Y.X`
- TOOLS.md and AGENTS.md updated with new paths
- Git history preserved via git mv

## How Sub-Agents Work (CRITICAL — read before delegating)
- Command: bash /root/.openclaw/workspace/core/utils/spawn_task.sh <topic_id> task
- Uses --agent worker (NOT --agent main — that causes infinite recursion)
- Each spawn gets a fresh session ID — no shared history between workers
- Worker knows it's a worker: has anti-recursion preamble in task
- NEVER call spawn_task.sh from inside a worker

## Google Calendar
- Script: python3 /root/.openclaw/workspace/core/integrations/gcal.py
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
