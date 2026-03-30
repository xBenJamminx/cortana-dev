#!/usr/bin/env python3
"""
OpenClaw <-> Claude CLI Session Bridge

OpenClaw and Claude CLI use different session IDs and store transcripts
in different directories. OpenClaw removed symlink bridging in ~2026.3.10
but never replaced it, breaking session resume after gateway restarts.

This script recreates the symlinks by reading OpenClaw's sessions.json,
finding the corresponding Claude CLI session files, and linking them.

Runs as a systemd timer (every 30s) or called directly.
"""

import json
import os
import sys
from pathlib import Path

SESSIONS_JSON = Path("/root/.openclaw/agents/main/sessions/sessions.json")
CLAUDE_PROJECT_DIR = Path("/root/.claude/projects/-root--openclaw-workspace")
OPENCLAW_SESSIONS_DIR = Path("/root/.openclaw/agents/main/sessions")


def bridge_sessions():
    if not SESSIONS_JSON.exists():
        return

    try:
        with open(SESSIONS_JSON) as f:
            store = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    created = 0
    for key, entry in store.items():
        if not isinstance(entry, dict):
            continue

        session_id = entry.get("sessionId", "")
        session_file = entry.get("sessionFile", "")
        cli_session_id = (
            entry.get("cliSessionIds", {}).get("claude-cli", "")
            or entry.get("claudeCliSessionId", "")
        )

        if not session_id or not cli_session_id or not session_file:
            continue

        # The expected OpenClaw session file path
        oc_path = Path(session_file)

        # The actual Claude CLI session file
        claude_path = CLAUDE_PROJECT_DIR / f"{cli_session_id}.jsonl"

        # Skip if OpenClaw file already exists (real file or valid symlink)
        if oc_path.exists():
            continue

        # Skip if Claude CLI file doesn't exist
        if not claude_path.exists():
            continue

        # Remove broken symlink if present
        if oc_path.is_symlink():
            oc_path.unlink()

        # Create symlink: openclaw path -> claude CLI path
        try:
            oc_path.symlink_to(claude_path)
            created += 1
        except OSError as e:
            print(f"[session-bridge] symlink failed: {oc_path} -> {claude_path}: {e}", file=sys.stderr)

    if created > 0:
        print(f"[session-bridge] created {created} symlink(s)")


if __name__ == "__main__":
    bridge_sessions()
