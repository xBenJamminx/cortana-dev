# TOOLS.md — Tool Routing Guide

## Quick Reference

| Task | Use This | NOT This |
|------|----------|----------|
| Read/send email | \ | composio direct |
| Browse the web / sign up for a service | Playwright via Python (`from playwright.sync_api import sync_playwright`) | saying "no browser available" |
| Calendar events | composio `GOOGLECALENDAR_*` | inbox-triage |
| Google Docs/Sheets | composio `GOOGLEDOCS_*` / `GOOGLESHEETS_*` | direct API |
| Slack message | composio `SLACK_*` | inbox-triage |
| Web search | `skills/brave-search/` | composio |
| Track follow-up | `skills/follow_up_tracker/` | memory file manually |
| Meeting prep | `skills/meeting_prep/` | raw calendar API |
| Morning briefing | `scripts/morning-briefing.py` | (cron-driven, don't call manually) |
| Evening recap | `scripts/evening-recap.py` | (cron-driven, don't call manually) |

> **Rule**: Always check this table before picking a tool. Skills define *how*. This table defines *which*.

---

## Composio

All external service calls go through Composio using:
- **Entity ID:** stored in `.env` as `COMPOSIO_ENTITY_ID`
- **API Key:** stored in `.env` as `COMPOSIO_API_KEY`

Connected services (varies by client):
- Google (Gmail, Calendar, Drive, Docs, Sheets, Tasks)
- Slack
- HubSpot
- Others as configured during onboarding

To call Composio actions, use the Composio skill:
```
/composio <ACTION_NAME> <params>
```

---

## Follow-Up Tracker

Database: `memory/follow-ups.db` (SQLite)

| Column | Description |
|--------|-------------|
| id | Auto-increment |
| description | What was promised |
| direction | "we_owe" or "they_owe" |
| contact | Who's involved |
| due_date | When (ISO 8601) |
| source | Email subject / Slack thread / Telegram msg |
| status | open / reminded / done |
| created_at | When logged |

Add a follow-up: `skills/follow_up_tracker/ --add`
Check due today: `skills/follow_up_tracker/ --due-today`
Mark done: `skills/follow_up_tracker/ --done <id>`

---

## Secrets

All credentials: `.env` (in workspace root, chmod 600)

Loading pattern (Python):
```python
from lib.env import _load_env
_load_env()
# Checks ~/.openclaw/.env first (production), then workspace root .env (dev)
```

---

## Telegram

Bot token: `.env` as `TELEGRAM_BOT_TOKEN`
Chat ID: `.env` as `TELEGRAM_CHAT_ID`
Thread IDs (topics): `.env` as `TELEGRAM_TOPIC_BRIEFING`, `TELEGRAM_TOPIC_ALERTS`

Use `lib/telegram.py` for all sends — it handles markdown escaping, splitting, retry.

---


---

## Sub-Agents (sessions_spawn)

Use `sessions_spawn` for ANY task that takes more than ~5 seconds. It's the right tool — killable, monitorable, and reports back automatically when done.

**How to spawn:** Call the `sessions_spawn` tool directly:
- `task` (required): Full self-contained instructions — include file paths, exact steps, what to do when done. **Worker does NOT get SOUL.md**, only AGENTS.md + TOOLS.md.
- `label` (optional): Human-readable name for monitoring (e.g. `"sleep-video-assembly"`)
- `model` (optional): Inherits yours by default. Use `claude-cli/haiku` for simple tasks.
- `runTimeoutSeconds` (optional): Auto-kill if stuck. Set this for all video jobs (e.g. `3600`).

**Monitor & control:**
- `/subagents list` — see all running sub-agents
- `/subagents log <id>` — tail a sub-agent's logs
- `/subagents kill <id>` — kill a stuck sub-agent
- `/subagents info <id>` — status, runtime, token stats

**When done:** Sub-agent announces result back to your chat automatically.

See task templates in AGENTS.md → "Sleep Video Sub-Agent Templates".

---

## Video Production Rules

Subtitles: NEVER burn subtitles. No SRT. No srt_path. Handled in post.
Channel routing: Video → Content Creation (topic 20). Never Research.
Images: Always 16:9 horizontal for YouTube/sleep videos.
Voice defaults: Stoic/Philosophy → Frank (V2bPluzT7MuirpucVAKH)
Image count is DYNAMIC (based on script scenes) — never hardcode.

**CRITICAL: Use sessions_spawn for all heavy pipeline steps.** Never run inline.
After spawning: tell Ben what you kicked off, then stay responsive.