#!/bin/bash
# Sync Claude CLI session transcripts to OpenClaw sessions folder

OPENCLAW_SESSIONS="/root/.openclaw/agents/main/sessions"
CLAUDE_SESSIONS="/root/.claude/projects/-root-clawd"

# Read sessions.json and create symlinks for CLI-backed sessions
jq -r 'to_entries[] | select(.value.cliSessionIds["claude-cli"] != null) | "\(.value.sessionId) \(.value.cliSessionIds["claude-cli"])"' "$OPENCLAW_SESSIONS/sessions.json" 2>/dev/null | while read oc_id cli_id; do
  if [ -n "$cli_id" ] && [ -f "$CLAUDE_SESSIONS/$cli_id.jsonl" ]; then
    target="$OPENCLAW_SESSIONS/$oc_id.jsonl"
    source="$CLAUDE_SESSIONS/$cli_id.jsonl"
    if [ ! -L "$target" ] && [ ! -f "$target" ]; then
      ln -sf "$source" "$target"
      echo "Linked: $oc_id -> $cli_id"
    fi
  fi
done
