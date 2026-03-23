# TOOLS.md — Tool Routing Guide

## Quick Reference

| Task | Use This | NOT This |
|------|----------|----------|
| Read/send email | Composio skill | composio direct |
| Browse the web / sign up for a service | Playwright via Python (`from playwright.sync_api import sync_playwright`) | saying "no browser available" |
| Calendar events | `python3 core/integrations/gcal.py` | composio GOOGLECALENDAR_* directly |
| Google Docs/Sheets | composio `GOOGLEDOCS_*` / `GOOGLESHEETS_*` | direct API |
| Slack message | `python3 core/integrations/slack.py <channel> [limit]` | saying no access |
| Web search | `skills/brave-search/` | composio |
| Track follow-up | `skills/follow_up_tracker/` | memory file manually |
| Meeting prep | `skills/meeting_prep/` | raw calendar API |
| Morning briefing | `automation/reporting/morning-briefing.py` | (cron-driven, don't call manually) |

> **Rule**: Always check this table before picking a tool. Skills define *how*. This table defines *which*.

---

## Directory Structure

```
core/                    # Core system modules
├── integrations/        # Third-party API wrappers
│   ├── telegram.py      # Telegram bot API
│   ├── slack.py         # Slack API
│   ├── bird.py          # Twitter/X (Bird CLI)
│   ├── elevenlabs.py    # Text-to-speech
│   ├── gcal.py          # Google Calendar
│   └── pexels.py        # Stock video/images
├── content/             # Content creation tools
│   ├── sleep/           # Sleep video pipeline
│   │   ├── pipeline.py  # Main orchestrator
│   │   └── video.py     # Video assembly
│   ├── imagegen.py      # Image generation
│   ├── slideshow.py     # TikTok slideshows
│   └── tiktok_video.py  # TikTok video tools
├── fathom/              # Fathom meeting tools
│   ├── client.py
│   ├── webhook.py
│   ├── server.py
│   ├── poll.py
│   └── register.py
├── monitoring/          # Health & alerting
│   ├── alerting.py
│   ├── health.py
│   └── retry.py
└── utils/               # Utilities
    ├── env.py           # Environment loading
    ├── spawn_task.sh    # Sub-agent spawner
    └── git-sync.sh

automation/              # Runnable automation scripts
├── content/             # Content generation
├── social/              # Social media tools
├── monitoring/          # Trend/news monitors
├── reporting/           # Reports & briefings
└── infra/               # Infrastructure & health
```

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

## Secrets

All credentials: `.env` (in `~/.openclaw/`, chmod 600)

Loading pattern (Python):
```python
from core.utils.env import load_env
load_env()
# Checks ~/.openclaw/.env first, then workspace root .env (dev)
```

---

## Telegram

Bot token: `.env` as `TELEGRAM_BOT_TOKEN`
Chat ID: `.env` as `TELEGRAM_CHAT_ID`
Thread IDs (topics): `.env` as `TELEGRAM_TOPIC_BRIEFING`, `TELEGRAM_TOPIC_ALERTS`

Use `core/integrations/telegram.py` for all sends — it handles markdown escaping, splitting, retry.

---

## Sub-Agents

Use `spawn_task.sh` for any task that takes more than ~10 seconds.

```bash
bash /root/.openclaw/workspace/core/utils/spawn_task.sh <topic_id> "detailed task instructions"
```

- Worker runs as --agent worker (isolated, no Cortana session history)
- Fresh session ID per run — no shared state between workers
- Worker reports back to the Telegram topic when done
- NEVER call spawn_task.sh from inside a worker (infinite loop)

Topics: 20=Content, 22=Research, 26=Ideas, 29=Analytics, 31=Business

---

## Video Production Rules

Subtitles: NEVER burn subtitles. No SRT. No srt_path. Handled in post.
Channel routing: Video → Content Creation (topic 20). Never Research.
Images: Always 16:9 horizontal for YouTube/sleep videos.
Voice defaults: Stoic/Philosophy → Frank (V2bPluzT7MuirpucVAKH)
Image count is DYNAMIC (based on script scenes) — never hardcode.

**CRITICAL: Use spawn_task.sh for all heavy pipeline steps.** Never run inline.
After spawning: tell Ben what you kicked off, then stay responsive.
