# HEARTBEAT.md - Lean Check-ins

> Target: <3 seconds. Don't load files unless idle.

## Fast Path (default)

1. Any pending Telegram messages? If yes, respond. If no, HEARTBEAT_OK.
2. That's it. Done. Don't load SOUL.md, MEMORY.md, or anything else.

## Idle Path (only if no messages in 2+ hours)

If Ben hasn't messaged in 2+ hours AND it's daytime (08:00-23:00 ET):
1. Check email (any urgent unread?)
2. Check calendar (anything in next 2 hours?)
3. If something found, message Ben via Telegram
4. Update BRAIN.md "Waiting On" section if relevant

## What NOT to Do in Heartbeats

- Don't read SOUL.md, IDENTITY.md, MEMORY.md
- Don't run scripts or monitors
- Don't load project files
- Don't review/organize memory
- Don't generate content
- Don't check social media analytics

## Voice Checklist (mental, don't load files)
- No filler words
- Direct language
- Brief responses
- Personality intact
