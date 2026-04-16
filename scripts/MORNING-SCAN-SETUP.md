# Morning Scan — Setup

## What it does
Every weekday at 9am Eastern, Cortana automatically:
1. Pulls last 24h from #meeting-notes, #updates, #testing
2. Checks Notion board state (In Progress, In Testing, Top Priority counts)
3. Posts a concise daily briefing to #updates so the whole team sees it
4. Sends Ben a TG ping if anything needs attention

## Deploy to server

```bash
# 1. Copy files to server
scp scripts/morning-scan-prompt.md cortana:/root/.openclaw/workspace/scripts/
scp scripts/morning-scan.sh cortana:/root/.openclaw/workspace/scripts/

# 2. SSH in and make executable
ssh cortana
chmod +x /root/.openclaw/workspace/scripts/morning-scan.sh

# 3. Add cron job (Mon-Fri at 9am Eastern = 13:00 UTC during EDT)
crontab -e
# Add this line:
# 0 13 * * 1-5 /root/.openclaw/workspace/scripts/morning-scan.sh >> /var/log/morning-scan.log 2>&1

# 4. Test it manually first
bash /root/.openclaw/workspace/scripts/morning-scan.sh
```

## Tuning
- **Time**: Currently `0 13` (13:00 UTC = 9am EDT). Change to `0 14` in November when EST resumes.
- **Days**: `1-5` = Mon-Fri. Change to `*` for every day.
- **Briefing format**: Edit `morning-scan-prompt.md` to change what gets posted.
- **TG topic**: Currently posts to Topic 31 (Business). Change in `morning-scan.sh`.

## Dependencies
- `spawn_task.sh` must exist at `/root/.openclaw/workspace/core/utils/spawn_task.sh`
- Composio Slack credential must be active (connectedAccountId: `b02db1f4-...`)
- Composio Notion credential needs to be re-established (currently dead as of 2026-03-24)
