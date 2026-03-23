#!/bin/bash
# Auto-update symlink between OpenClaw session and Claude CLI session

SESSION_JSON="/root/.openclaw/agents/main/sessions/sessions.json"
SESSIONS_DIR="/root/.openclaw/agents/main/sessions"
CLAUDE_DIR="/root/.claude/projects/-root--openclaw-workspace"

# Read current session IDs from sessions.json
OPENCLAW_SESSION=$(jq -r '."agent:main:main".sessionId // empty' "$SESSION_JSON" 2>/dev/null)
CLAUDE_SESSION=$(jq -r '."agent:main:main".claudeCliSessionId // empty' "$SESSION_JSON" 2>/dev/null)

if [ -z "$OPENCLAW_SESSION" ] || [ -z "$CLAUDE_SESSION" ]; then
    echo "No active session found"
    exit 0
fi

SYMLINK_PATH="$SESSIONS_DIR/$OPENCLAW_SESSION.jsonl"
TARGET_PATH="$CLAUDE_DIR/$CLAUDE_SESSION.jsonl"

# Check if target exists
if [ ! -f "$TARGET_PATH" ]; then
    echo "Target session file doesn't exist: $TARGET_PATH"
    exit 0
fi

# Check if symlink already points to the right place
if [ -L "$SYMLINK_PATH" ]; then
    CURRENT_TARGET=$(readlink "$SYMLINK_PATH")
    if [ "$CURRENT_TARGET" = "$TARGET_PATH" ]; then
        exit 0  # Already correct
    fi
fi

# Create or update symlink
ln -sf "$TARGET_PATH" "$SYMLINK_PATH"
echo "[$(date)] Updated symlink: $OPENCLAW_SESSION -> $CLAUDE_SESSION"
