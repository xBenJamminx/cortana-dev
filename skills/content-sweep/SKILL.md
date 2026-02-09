# Content Sweep Skill

## Trigger Phrases
- "do a content sweep"
- "what's trending"
- "check trending"
- "trending content"
- "content ideas"
- "what's hot"
- "show me trending"
- "run content sweep"

## Action
Run the content sweep script and return the results to the user.

## Script
```bash
/root/clawd/scripts/content-sweep.py
```

## Response Format
The script outputs Markdown-formatted trending content from:
- AI/Tech news (via DuckDuckGo)
- Hacker News top stories
- Indie hacker topics

Send the output directly to the user via Telegram.

## Notes
- Takes ~30-60 seconds to refresh data
- Can use --no-refresh flag to skip refresh and show cached data
- Data is stored in SQLite and updates every 4 hours via cron
