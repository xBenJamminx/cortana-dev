#!/bin/bash
# spawn_task.sh - Spawn an independent sub-agent worker
# Usage: spawn_task.sh <topic_id> "task description"
#
# Uses --agent worker (separate session space from Cortana main).
# Fresh session ID per invocation = no shared history between workers.
# Anti-recursion preamble prevents worker from spawning more sub-agents.

TOPIC="${1}"
TASK="${2}"
WORKER_ID="worker-$(date +%s)"
SESSION_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

if [ -z "$TOPIC" ] || [ -z "$TASK" ]; then
  echo "Usage: spawn_task.sh <topic_id> <task>"
  exit 1
fi

LOG="/tmp/subtask_$(date +%s%3N).log"

FULL_TASK="## WORKER SUB-AGENT — ${WORKER_ID}

You are a focused task executor. Your ONLY job is to complete the task below using your tools.

RULES (non-negotiable):
- Execute ALL steps DIRECTLY using Bash, Read, Write, Edit, Glob, Grep, WebFetch, etc.
- Do NOT call spawn_task.sh — that creates infinite loops
- Do NOT say you will spawn a sub-agent or delegate — you ARE the sub-agent
- Do NOT wait for user input — complete the task autonomously
- When done, report results to Telegram topic ${TOPIC}:
  python3 /root/.openclaw/workspace/lib/telegram.py --topic ${TOPIC} \"your results here\"

---

## TASK

${TASK}
---"

nohup openclaw agent \
  --agent worker \
  --session-id "${SESSION_ID}" \
  --message "${FULL_TASK}" \
  --timeout 1200 \
  > "${LOG}" 2>&1 &

PID=$!
echo "spawned pid=${PID} session=${SESSION_ID} log=${LOG}"
