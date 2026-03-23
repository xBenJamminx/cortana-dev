#!/bin/bash
# Auto-commit and push workspace changes to cortana-dev
cd /root/.openclaw/workspace

# Pull first to avoid conflicts
git pull origin master --rebase -q 2>/dev/null

# Stage all changes (including untracked files)
git add -A

# Commit if there's anything staged
if ! git diff --staged --quiet; then
    git commit -m "auto: workspace sync $(date '+%Y-%m-%d %H:%M')" -q
    git push origin master -q
fi
