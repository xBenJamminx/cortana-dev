#!/bin/bash
# Health check script - callable via Telegram /health command
# Returns current status of gateway, processes, and sessions

OUTPUT=""

# Gateway status
OUTPUT+="🔍 **Gateway Status**\n"
if systemctl is-active --quiet openclaw-gateway; then
    OUTPUT+="✅ Service: running\n"
    UPTIME=$(systemctl show openclaw-gateway -p ActiveEnterTimestamp --value)
    OUTPUT+="⏱️ Uptime: ${UPTIME}\n"
else
    OUTPUT+="❌ Service: DOWN\n"
fi

# Check if port is responding
if timeout 2 curl -s http://localhost:18789/health > /dev/null 2>&1; then
    OUTPUT+="✅ HTTP: responding\n"
else
    OUTPUT+="⚠️ HTTP: not responding\n"
fi

OUTPUT+="\n"

# Claude processes
OUTPUT+="🤖 **Claude Processes**\n"
CLAUDE_PROCS=$(ps aux | grep -E 'claude$|claude ' | grep -v grep | wc -l)
if [ "$CLAUDE_PROCS" -gt 0 ]; then
    OUTPUT+="✅ Active processes: ${CLAUDE_PROCS}\n"
    # Show process details (runtime, CPU)
    ps aux | grep -E 'claude$|claude ' | grep -v grep | awk '{printf "  • PID %s: %.1f%% CPU, %s\n", $2, $3, $10}' | while read line; do
        OUTPUT+="${line}\n"
    done
else
    OUTPUT+="⚠️ No claude processes running\n"
fi

OUTPUT+="\n"

# Session files
OUTPUT+="📁 **Session Files**\n"
SESSION_DIR="/root/.claude/projects/-root--openclaw-workspace"
if [ -d "$SESSION_DIR" ]; then
    LARGEST=$(find "$SESSION_DIR" -name '*.jsonl' -type f -printf '%s %p\n' 2>/dev/null | sort -rn | head -1)
    if [ -n "$LARGEST" ]; then
        SIZE_BYTES=$(echo $LARGEST | awk '{print $1}')
        SIZE_MB=$(echo "scale=1; $SIZE_BYTES / 1024 / 1024" | bc)
        FILENAME=$(basename $(echo $LARGEST | awk '{print $2}'))
        OUTPUT+="📊 Largest: ${FILENAME} (${SIZE_MB}MB)\n"
        
        # Warn if approaching limit
        SIZE_INT=${SIZE_MB%.*}
        if [ "$SIZE_INT" -ge 20 ]; then
            OUTPUT+="⚠️ Session approaching 25MB limit!\n"
        fi
    else
        OUTPUT+="✅ No active sessions\n"
    fi
else
    OUTPUT+="⚠️ Session directory not found\n"
fi

OUTPUT+="\n"

# Recent activity
OUTPUT+="📝 **Recent Activity**\n"
LOG_FILE=$(ls -t /tmp/openclaw/openclaw-*.log 2>/dev/null | head -1)
if [ -n "$LOG_FILE" ]; then
    LAST_EXEC=$(tail -100 "$LOG_FILE" | grep 'cli exec:' | tail -1)
    if [ -n "$LAST_EXEC" ]; then
        # Extract timestamp (rough - just show it was recent)
        OUTPUT+="✅ Recent CLI activity detected\n"
    else
        OUTPUT+="⚠️ No recent CLI activity (check if idle)\n"
    fi
else
    OUTPUT+="⚠️ No gateway logs found\n"
fi

OUTPUT+="\n"

# Disk space
OUTPUT+="💾 **Disk Space**\n"
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
DISK_AVAIL=$(df -h / | tail -1 | awk '{print $4}')
OUTPUT+="📊 Usage: ${DISK_USAGE}% (${DISK_AVAIL} free)\n"

if [ "$DISK_USAGE" -gt 85 ]; then
    OUTPUT+="⚠️ Disk space running low\n"
fi

# Output (escape for proper formatting in Telegram)
echo -e "$OUTPUT"
