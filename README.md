# Cortana

An AI executive assistant running on [OpenClaw](https://github.com/openclaw/openclaw). Cortana handles research, content intelligence, and operational tasks autonomously.

## What Cortana Does

Cortana is a persistent AI agent that:

- **Monitors trends** — Scans Twitter, Reddit, Product Hunt, Hacker News, YouTube for content opportunities
- **Tracks competitors** — Follows indie hackers, AI builders, and content creators
- **Manages memory** — Maintains context about projects, preferences, and ongoing work via QMD semantic search
- **Handles communication** — Available via Telegram, voice calls (Twilio), and the OpenClaw web UI
- **Executes tasks** — Web search, file management, research, content drafting

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Cortana                              │
│                    (OpenClaw Agent)                          │
├─────────────────────────────────────────────────────────────┤
│  Model: Claude Opus 4.5 (via claude-cli)                    │
│  Memory: QMD (local semantic search, no cloud dependency)    │
│  Tools: Bash, Read, Write, Edit, Glob, Grep, WebSearch      │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │ Telegram │       │  Voice   │       │ Web UI   │
    │   Bot    │       │ (Twilio) │       │ Gateway  │
    └──────────┘       └──────────┘       └──────────┘
```

## Memory System (QMD)

Cortana uses [QMD](https://github.com/tobi/qmd) for memory — a local-first semantic search system:

- **BM25** — Fast keyword matching
- **Vector search** — Semantic similarity via local embeddings (embeddinggemma)
- **LLM reranking** — Qwen3 scores results for relevance
- **Fully local** — No API calls, works offline, private

Memory files live in `/root/clawd/memory/` and include:
- Daily logs and context
- Trend reports and research
- Integration status and preferences
- Content ideas and drafts

## Channels

| Channel | Access |
|---------|--------|
| Telegram | @CortanaOpsBot |
| Voice | Twilio integration |
| Web UI | OpenClaw Gateway (localhost:18789) |
| Dashboard | [Cortana OS](https://github.com/xBenJamminx/cortana-os) |

## Skills & Tools

**Built-in:**
- WebSearch (DuckDuckGo)
- File operations (Read, Write, Edit, Glob, Grep)
- Bash command execution

**Integrations (via Cortana OS backend):**
- Gmail & Calendar
- Twitter (Bird CLI)
- YouTube Analytics
- Notion
- Google Drive & Tasks

## Dev Workflow

Cortana can request development work by creating GitHub issues:

```bash
gh issue create --repo xBenJamminx/cortana-dev   --title "[Feature] Add new capability"   --label "claude-code,pending"   --body "Description of what needs to be built..."
```

When Ben says **"check cortana"**, Claude Code reviews open issues and implements them.

## Configuration

Config lives at `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "claude-cli/opus" },
      "workspace": "/root/clawd",
      "cliBackends": {
        "claude-cli": {
          "args": ["--allowedTools", "Bash,Read,Write,Edit,Glob,Grep,WebSearch"]
        }
      }
    }
  },
  "memory": {
    "backend": "qmd"
  },
  "channels": {
    "telegram": { "enabled": true }
  }
}
```

## Related Projects

- [Cortana OS](https://github.com/xBenJamminx/cortana-os) — The dashboard frontend
- [OpenClaw](https://github.com/openclaw/openclaw) — The agent framework

---

*"I handle the ops. You handle the vision."* — Cortana
