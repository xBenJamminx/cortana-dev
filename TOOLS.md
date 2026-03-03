# TOOLS.md — Tool Routing Guide

## Quick Reference

| Task | Use This | NOT This |
|------|----------|----------|
| Read/send email | \ | composio direct |
| Browse the web / sign up for a service | Playwright via Python (`from playwright.sync_api import sync_playwright`) | saying "no browser available" |
| Calendar events | `python3 lib/gcal.py` | composio GOOGLECALENDAR_* directly |
| Google Docs/Sheets | composio `GOOGLEDOCS_*` / `GOOGLESHEETS_*` | direct API |
| Slack message | Slack API (SLACK_BOT_TOKEN) or composio SLACK_* | saying no access |
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

## Sub-Agents

Use `spawn_task.sh` for any task that takes more than ~10 seconds.

```bash
bash /root/.openclaw/workspace/lib/spawn_task.sh <topic_id> "detailed task instructions"
```

- Worker runs as --agent worker (isolated, no Cortana session history)
- Fresh session ID per run — no shared state between workers
- Worker reports back to the Telegram topic when done
- NEVER call spawn_task.sh from inside a worker (infinite loop)
- sessions_spawn and run_in_background:true are BROKEN — do not use

Topics: 20=Content, 22=Research, 26=Ideas, 29=Analytics, 31=Business


## Video Production Rules

Subtitles: NEVER burn subtitles. No SRT. No srt_path. Handled in post.
Channel routing: Video → Content Creation (topic 20). Never Research.
Images: Always 16:9 horizontal for YouTube/sleep videos.
Voice defaults: Stoic/Philosophy → Frank (V2bPluzT7MuirpucVAKH)
Image count is DYNAMIC (based on script scenes) — never hardcode.

**CRITICAL: Use spawn_task.sh for all heavy pipeline steps.** Never run inline.
After spawning: tell Ben what you kicked off, then stay responsive.