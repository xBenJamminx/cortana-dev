#!/bin/bash
# Setup cron jobs for Cortana-OS autonomous operations

# Remove existing cortana crons
crontab -l 2>/dev/null | grep -v "clawd" | crontab -

# Add new crons (all times in server timezone, adjust for ET)
(crontab -l 2>/dev/null; cat << 'CRON'
# Cortana-OS Autonomous Operations

# Morning briefing at 7:00 AM ET (12:00 UTC)
0 12 * * * /usr/bin/python3 /root/clawd/scripts/morning-briefing.py >> /root/clawd/logs/cron-morning.log 2>&1

# Content ideas at 7:30 AM ET (12:30 UTC) 
30 12 * * * /usr/bin/python3 /root/clawd/scripts/content-ideas-generator.py >> /root/clawd/logs/cron-ideas.log 2>&1

# Real trends every 4 hours
0 */4 * * * /usr/bin/python3 /root/clawd/scripts/real-trends-monitor.py >> /root/clawd/logs/cron-trends.log 2>&1

# Competitor monitor every 6 hours
0 */6 * * * /usr/bin/python3 /root/clawd/scripts/competitor-monitor.py >> /root/clawd/logs/cron-competitor.log 2>&1

CRON
) | crontab -

echo "Cron jobs installed:"
crontab -l | grep clawd
