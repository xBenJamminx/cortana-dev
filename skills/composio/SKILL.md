---
name: composio
description: Universal tool router for 500+ apps via Composio. Use for Twitter, Gmail, Slack, Notion, Google Sheets, Calendar, Drive, and any other connected service.
metadata:
  clawdbot:
    emoji: "🔌"
---

# Composio Integration

Universal API gateway to 500+ connected apps including Twitter, Gmail, Slack, Notion, Google services, and more.

## Quick Start

```bash
# Search for tools by use case
~/clawd/skills/composio/composio-mcp.py --search "post tweet"

# Execute a tool
~/clawd/skills/composio/composio-mcp.py --exec TOOL_SLUG '{"param": "value"}'
```

## Connected Services

**Currently connected:**
- Twitter/X (@xBenJamminx) - posting, reading, searching, DMs

**Available to connect (500+ apps):**
- Gmail, Google Calendar, Drive, Sheets, Docs
- Slack, Discord, Telegram
- Notion, Airtable, Trello
- GitHub, GitLab, Linear
- And many more at https://platform.composio.dev

## Twitter Examples

**Get my profile:**
```bash
~/clawd/skills/composio/composio-mcp.py --exec TWITTER_USER_LOOKUP_ME
```

**Post a tweet:**
```bash
~/clawd/skills/composio/composio-mcp.py --exec TWITTER_CREATION_OF_A_POST '{"text": "Hello world!"}'
```

**Search tweets:**
```bash
~/clawd/skills/composio/composio-mcp.py --exec TWITTER_RECENT_SEARCH '{"query": "AI agents", "max_results": 10}'
```

**Get home timeline:**
```bash
~/clawd/skills/composio/composio-mcp.py --exec TWITTER_USER_HOME_TIMELINE_BY_USER_ID '{"max_results": 20}'
```

## Connecting New Apps

To connect a new app (e.g., Gmail, Slack, Notion):

```bash
~/clawd/skills/composio/composio-mcp.py COMPOSIO_MANAGE_CONNECTIONS '{"toolkits": ["gmail"]}'
```

This returns an authentication URL. Open it in a browser to complete OAuth.

## Finding Tools

Search by what you want to do:
```bash
~/clawd/skills/composio/composio-mcp.py --search "send email"
~/clawd/skills/composio/composio-mcp.py --search "create calendar event"
~/clawd/skills/composio/composio-mcp.py --search "post slack message"
```

## Meta Tools

- `COMPOSIO_SEARCH_TOOLS` - Find tools by use case
- `COMPOSIO_MANAGE_CONNECTIONS` - Connect new apps
- `COMPOSIO_MULTI_EXECUTE_TOOL` - Execute multiple tools in parallel
- `COMPOSIO_GET_TOOL_SCHEMAS` - Get detailed parameter info
