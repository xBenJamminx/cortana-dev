---
name: reply-guy
description: >
  Reply Guy — finds fresh, high-engagement posts to reply to across content pillars.
  Aggregates multi-query searches, deduplicates, scores by engagement velocity.
  Use when: (1) user says "reply guy", "reply-guy", "/reply-guy", "/radar",
  "find posts to reply to", "what should I reply to", "reply targets",
  (2) user wants fresh trending posts in their niche.
metadata:
  clawdbot:
    emoji: "🎯"
    triggers:
      - "/reply-guy"
      - "/radar"
      - "/search"
      - "/pillars"
---

## Routing

### Use When
- User wants to find tweets/posts to reply to for engagement
- User says "find reply targets", "find posts to engage with", "reply-guy mode"
- User wants to build audience by strategically replying to others' content
- Task is about FINDING TARGETS to reply to (discovery + selection)

### Do NOT Use When
- User wants to RESEARCH a topic on Twitter → Use **x-research** instead
- User wants to POST original content → Use **cortana-post.py** instead
- User wants general Twitter/X data or trends → Use **x-research** instead
- User wants to interact with Twitter API directly → Use **composio** only if no other skill fits

### Negative Examples
- "What are people saying about AI agents on Twitter?" → Do NOT use reply-guy, use x-research
- "Search Twitter for discussions about LLMs" → Do NOT use reply-guy, use x-research
- "Post a tweet about our new feature" → Do NOT use reply-guy, use cortana-post.py

# Reply Guy

Finds fresh, high-engagement posts across content pillars for strategic replies.

## Commands

### /reply-guy or /radar

Full aggregated scan. Options:

```
/reply-guy                        → All pillars, last 3h, defaults
/reply-guy ai_tools               → Specific pillar
/reply-guy hot_takes 6h           → Pillar + time window
/reply-guy 12h                    → All pillars, custom time
/reply-guy --min-followers 10000  → Custom follower threshold
/reply-guy --min-likes 20         → Custom engagement threshold
/reply-guy --top 20               → More results
/reply-guy ai_tools 6h --top 15 --min-followers 10000
```

Run the script with matching args:
```bash
python3 /root/.openclaw/workspace/scripts/reply-radar.py --send [OPTIONS]
```

**Argument mapping:**
- Pillar name → `--pillars <name>`
- Time like `6h` → `--since 6 --max-age 6`
- `--min-followers N` → `--min-followers N`
- `--min-likes N` → `--min-likes N`
- `--top N` → `--top N`

### /search <query>

Custom one-off X search:
```
/search claude code MCP
/search from:levelsio
/search "vibe coding" shipped
```

Use x-research skill for the search, then format nicely and send to Telegram:
```bash
cd /root/.openclaw/workspace/skills/x-research && bun run x-search.ts search "<query> lang:en -is:retweet" --sort likes --since 3h --limit 10
```

### /pillars

List available content pillars:
- **ai_tools** (4 queries) — Claude Code, Cursor, AI agents, MCP, vibe coding
- **build_in_public** (3 queries) — building in public, shipped/launched, indie hacker
- **solopreneur** (3 queries) — solopreneur, quit my job, side projects
- **ai_workflow** (3 queries) — AI automation, prompt engineering, free APIs
- **hot_takes** (2 queries) — unpopular opinions, overrated/underrated

## Defaults

- Time window: 3 hours
- Max post age: 3 hours
- Min followers: 5,000
- Min likes: 10
- Top results: 10
- Freshness bonus: 2x for posts under 1 hour old

## How It Works

1. Runs 15 search queries across 5 content pillars via Composio Twitter API
2. Deduplicates results across all queries
3. Filters by follower count, likes, and post age
4. Scores by velocity (likes/hour) × log(followers) with freshness bonus
5. Returns top ranked results with tweet URLs

## Script Location

`/root/.openclaw/workspace/scripts/reply-radar.py`
