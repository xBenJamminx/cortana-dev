#!/bin/bash
# Auto-commit and push workspace changes to cortana-dev
cd /root/.openclaw/workspace

# Pull first to avoid conflicts
git pull origin master --rebase -q 2>/dev/null

# Stage and commit any changes
if ! git diff --quiet || ! git diff --staged --quiet; then
    git add -A
    git commit -m "auto: workspace sync 2026-03-04 10:40" -q
    git push origin master -q
fi
