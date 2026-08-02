#!/bin/bash
# Setup cron jobs for Cortana-OS autonomous operations.
#
# NOTE: Hermes cron (`hermes cron`, or the `cronjob` tool) is the preferred way
# to schedule durable agent work -- see README.md and AGENTS.md. This script
# remains for plain script schedules that do not need an agent session.
#
# Paths resolve from the checkout, or CORTANA_WORKSPACE when set.
set -euo pipefail

REPO_ROOT="${CORTANA_WORKSPACE:-$(cd "$(dirname "$0")/.." && pwd)}"
MARKER="# cortana-os-cron"

mkdir -p "$REPO_ROOT/logs"

# Remove previously installed Cortana entries (current marker and legacy paths).
crontab -l 2>/dev/null \
  | grep -v "$MARKER" \
  | grep -v "clawd" \
  | crontab - || true

# Add new crons (all times UTC; adjust for ET).
(crontab -l 2>/dev/null; cat << CRON
$MARKER Cortana-OS Autonomous Operations

$MARKER Morning briefing at 7:00 AM ET (12:00 UTC)
0 12 * * * /usr/bin/python3 $REPO_ROOT/scripts/morning-briefing.py >> $REPO_ROOT/logs/cron-morning.log 2>&1

$MARKER Content ideas at 7:30 AM ET (12:30 UTC)
30 12 * * * /usr/bin/python3 $REPO_ROOT/scripts/content-ideas-generator.py >> $REPO_ROOT/logs/cron-ideas.log 2>&1

$MARKER Real trends every 4 hours
0 */4 * * * /usr/bin/python3 $REPO_ROOT/scripts/real-trends-monitor.py >> $REPO_ROOT/logs/cron-trends.log 2>&1

$MARKER Competitor monitor every 6 hours
0 */6 * * * /usr/bin/python3 $REPO_ROOT/scripts/competitor-monitor.py >> $REPO_ROOT/logs/cron-competitor.log 2>&1

CRON
) | crontab -

echo "Cron jobs installed:"
crontab -l | grep -F "$MARKER"
