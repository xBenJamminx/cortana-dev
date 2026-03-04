---
name: composio
description: Execute actions on connected apps (Google Calendar, Gmail, Docs, Sheets, Slack, Notion, Airtable) via Composio API. Use for calendar events, sending emails, Google Docs, Sheets operations.
---

# Composio Integration

Execute actions on 500+ connected apps via Composio.

## Status

**PARTIALLY WORKING** - Google integrations (Calendar, Docs, Sheets, Gmail) work via MCP. Twitter auth is DEAD (X suspended Composio managed credentials Feb 9, 2025).

## Usage

Composio is primarily accessed via the MCP server configured in `.mcp.json`, not the local scripts.

For direct API calls, use the Composio MCP URL and API key from `~/.openclaw/.env`.

## Working Integrations

- Google Calendar
- Gmail
- Google Docs
- Google Sheets
- Google Drive
- Slack
- Notion
- Airtable

## Dead Integrations

- Twitter/X (suspended Feb 9)

## Legacy Scripts

- `composio-tool.py` - Direct API wrapper (has hardcoded old paths, needs cleanup)
- `run-composio` - Shell wrapper (references deleted venv)

**Note:** These scripts reference old `~/clawd/` paths and hardcoded keys. Use MCP instead.
