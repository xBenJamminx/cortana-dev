#!/bin/bash
# Review Monitor - Cron Setup
# Adds automated review checking and daily digests

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="/usr/bin/python3"
REVIEW_SCRIPT="$SCRIPT_DIR/review_monitor.py"
LOG_DIR="/root/.openclaw/workspace/logs"

echo "Setting up Review Monitor cron jobs..."

# Check all clients every 2 hours (6am-10pm)
(crontab -l 2>/dev/null | grep -v "review_monitor.py"; echo "0 6,8,10,12,14,16,18,20,22 * * * cd $SCRIPT_DIR && $PYTHON $REVIEW_SCRIPT --check-all >> $LOG_DIR/review-monitor.log 2>&1") | crontab -

# Send daily digest at 7am
(crontab -l 2>/dev/null | grep -v "review_monitor.*digest"; echo "0 7 * * * cd $SCRIPT_DIR && $PYTHON $REVIEW_SCRIPT --digest-all >> $LOG_DIR/review-monitor-digest.log 2>&1") | crontab -

echo "Cron jobs installed:"
echo "  - Review check: Every 2 hours (6am-10pm)"
echo "  - Daily digest: 7:00 AM"
echo ""
echo "Verify with: crontab -l | grep review"
