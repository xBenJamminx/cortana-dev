#!/bin/bash
# Obsidian Vault Sync — pushes memory/context changes to a bare repo Ben can clone
# Run via cron every 5 minutes or on-demand after memory writes

VAULT_ROOT="/root/.openclaw/workspace"
SYNC_REPO="/root/.openclaw/obsidian-vault.git"
LOG="/root/.openclaw/workspace/logs/obsidian-sync.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG"; }

# Initialize bare repo if it doesn't exist
if [ ! -d "$SYNC_REPO" ]; then
    git init --bare "$SYNC_REPO" 2>/dev/null
    log "Initialized bare sync repo at $SYNC_REPO"
fi

cd "$VAULT_ROOT" || exit 1

# Check if there are changes worth syncing
CHANGES=$(git status --porcelain memory/ context/ .obsidian/ CLAUDE.md BRAIN.md 2>/dev/null | wc -l)

if [ "$CHANGES" -eq 0 ]; then
    exit 0
fi

# Stage only vault-relevant files (not logs, scripts, etc.)
git add memory/ context/ .obsidian/ CLAUDE.md BRAIN.md 2>/dev/null

# Only commit if there are staged changes
if git diff --cached --quiet 2>/dev/null; then
    exit 0
fi

git commit -m "vault sync: $(date '+%Y-%m-%d %H:%M')" --no-gpg-sign 2>/dev/null
log "Committed vault changes ($CHANGES files)"

# Push to bare repo (Ben clones from this)
git push "$SYNC_REPO" master 2>/dev/null && log "Pushed to sync repo" || log "Push failed"
