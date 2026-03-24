#!/bin/bash
# Morning Scan — triggered daily by cron
# Posts a team briefing to FAM #updates Slack channel
#
# Cron entry (add via: crontab -e):
#   0 8 * * 1-5 /root/.openclaw/workspace/scripts/morning-scan.sh >> /var/log/morning-scan.log 2>&1
#
# Runs Mon-Fri at 8:00 AM server time. Adjust timezone as needed.

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
PROMPT_FILE="$WORKSPACE/scripts/morning-scan-prompt.md"
SPAWN="$WORKSPACE/core/utils/spawn_task.sh"
LOG_PREFIX="[morning-scan $(date '+%Y-%m-%d %H:%M')]"

echo "$LOG_PREFIX Starting morning scan..."

# Use spawn_task.sh to run as independent agent session
# Topic 31 = Business (where Ben gets notified)
bash "$SPAWN" 31 "$(cat "$PROMPT_FILE")"

echo "$LOG_PREFIX Scan agent spawned."
