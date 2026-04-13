#!/bin/bash
# Morning Scan — triggered daily by cron
# Generates the Slack morning update in an isolated worker context.
# Delivery target is defined by the prompt/worker logic, not by a Telegram topic wrapper.
#
# Cron entry (add via: crontab -e):
#   0 8 * * 1-5 /root/.openclaw/workspace/scripts/morning-scan.sh >> /var/log/morning-scan.log 2>&1
#
# Runs Mon-Fri at 8:00 AM server time. Adjust timezone as needed.

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
PROMPT_FILE="$WORKSPACE/scripts/morning-scan-prompt.md"
LOG_PREFIX="[morning-scan $(date '+%Y-%m-%d %H:%M')]"
PROMPT="$(cat "$PROMPT_FILE")"

echo "$LOG_PREFIX Starting morning scan..."

openclaw sessions spawn \
  --runtime subagent \
  --label morning-scan \
  --cwd "$WORKSPACE" \
  --run-timeout 900 \
  "$PROMPT"

echo "$LOG_PREFIX Scan agent spawned."
