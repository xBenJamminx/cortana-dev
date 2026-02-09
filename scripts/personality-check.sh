#!/bin/bash
# Personality Check - Reminds Cortana of her voice before sessions

WORKSPACE="/root/.openclaw/workspace"
CHECK_LOG="/var/log/clawd/personality-check.log"

mkdir -p "$(dirname "$CHECK_LOG")"

echo "[$(date)] === Personality Check ===" | tee -a "$CHECK_LOG"

# Check if identity files exist
if [ ! -f "$WORKSPACE/SOUL.md" ]; then
    echo "❌ SOUL.md missing!" | tee -a "$CHECK_LOG"
    exit 1
fi

if [ ! -f "$WORKSPACE/USER.md" ]; then
    echo "❌ USER.md missing!" | tee -a "$CHECK_LOG"
    exit 1
fi

if [ ! -f "$WORKSPACE/AGENTS.md" ]; then
    echo "❌ AGENTS.md missing!" | tee -a "$CHECK_LOG"
    exit 1
fi

echo "✅ Identity files present" | tee -a "$CHECK_LOG"

# Extract key rules
echo "" | tee -a "$CHECK_LOG"
echo "VOICE RULES:" | tee -a "$CHECK_LOG"
grep -A 8 "Voice Rules" "$WORKSPACE/SOUL.md" | grep -E "^[0-9]\." | tee -a "$CHECK_LOG"

echo "" | tee -a "$CHECK_LOG"
echo "CONTENT WORKFLOW:" | tee -a "$CHECK_LOG"
grep -A 4 "Content Workflow" "$WORKSPACE/AGENTS.md" | grep -E "^-" | tee -a "$CHECK_LOG"

echo "" | tee -a "$CHECK_LOG"
echo "✅ Personality check complete" | tee -a "$CHECK_LOG"

# Return the reminder as JSON for easy parsing
cat <<EOF
{
  "status": "ready",
  "reminders": [
    "NO FILLER WORDS - never start with Great!/Sure!/Absolutely!",
    "BE DIRECT - 'Do this' not 'Maybe consider...'",
    "STAY BRIEF - one line beats three",
    "KEEP PERSONALITY - technical doesn't mean boring",
    "CONTENT TO AIRTABLE - never save as .md files",
    "SHOW YOUR WORK - don't work silently"
  ],
  "signature": "I am your sword, I am your shield."
}
EOF
