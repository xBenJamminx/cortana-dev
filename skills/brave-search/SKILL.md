---
name: brave-search
description: Web search and content extraction via Brave Search API. Use for searching documentation, facts, or any web content. Lightweight, no browser required.
---

# Brave Search

Headless web search using Brave Search API. No browser required.

## Status

**NEEDS SETUP** - Requires `BRAVE_API_KEY` in `~/.openclaw/.env`. Get one at https://brave.com/search/api/

## Alternative

Claude Code has built-in `WebSearch` and `WebFetch` tools that work without any API key. Use those instead unless Brave-specific features are needed.

## Setup (when ready)

1. Get API key from https://brave.com/search/api/
2. Add to `~/.openclaw/.env`: `BRAVE_API_KEY=your_key_here`
3. Skill will be functional after key is added

## When to Use

- Use built-in WebSearch for general searches (no setup needed)
- Use this skill only if Brave-specific search features are needed
