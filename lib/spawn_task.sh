#!/bin/bash
# spawn_task.sh - Spawn an independent sub-agent worker
# Usage: spawn_task.sh <topic_id> "task description"
#
# The sub-agent runs fully independently, does the work,
# and reports results back to the telegram topic when done.

TOPIC="${1}"
TASK="${2}"

if [ -z "$TOPIC" ] || [ -z "$TASK" ]; then
  echo "Usage: spawn_task.sh <topic_id> <task>"
  exit 1
fi

LOG="/tmp/subtask_$(date +%s%N | cut -c1-13).log"

# Embed reporting instructions directly in the task so the sub-agent
# knows exactly how to send results back — no routing context needed
FULL_TASK="${TASK}

---
REPORTING INSTRUCTIONS:
When your task is complete, send a summary of results to Telegram topic ${TOPIC} using:
  python3 /root/.openclaw/workspace/lib/telegram.py --topic ${TOPIC} \"your results message here\"

Load env first if needed:
  source /root/.openclaw/.env
  export \$(grep -v '^#' /root/.openclaw/.env | xargs)
---"

nohup openclaw agent \
  --agent main \
  --message "$FULL_TASK" \
  --timeout 1200 \
  > "$LOG" 2>&1 &

PID=$!
echo "spawned pid=$PID log=$LOG"
