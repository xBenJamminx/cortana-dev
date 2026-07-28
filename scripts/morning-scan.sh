#!/usr/bin/env bash
# Legacy compatibility guard. Morning Scan is scheduled as a Hermes cron job.
set -euo pipefail

cat >&2 <<'EOF'
This OpenClaw-era wrapper is retired and intentionally does not launch an agent.
Create or run the durable Hermes cron job described in:
  scripts/MORNING-SCAN-SETUP.md

Useful checks:
  hermes cron list
  hermes cron status
EOF
exit 2
