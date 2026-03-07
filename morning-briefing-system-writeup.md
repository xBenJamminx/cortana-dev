# Morning Briefing System - Technical Writeup

## Overview

**Cortana Morning Briefing v2** is a fully automated intelligence gathering and aggregation system that delivers a comprehensive daily briefing to Ben each morning. It runs on cron and pulls data from 10+ sources, deduplicates content, and presents it in a compact, scannable format via Telegram.

---

## Technical Stack

- **Runtime:** Python 3
- **Database:** SQLite (`/root/.openclaw/memory/main.sqlite`)
- **Message Delivery:** Telegram Bot API (to Analytics topic #29)
- **Data Sources:** 10+ monitors running independently on cron schedules
- **Authentication:** Google OAuth (Calendar), Airtable API, Reddit API, RSS feeds

---

## Architecture

### 1. Data Collection (Monitor Scripts)

The briefing doesn't collect data itself — it reads from a shared SQLite database populated by independent monitor scripts that run on their own schedules:

| Monitor | Frequency | What It Tracks |
|---------|-----------|----------------|
| `email-newsletter-monitor.py` | Every 2 hours | AI/creator newsletters (extracts stories + nuggets) |
| `reddit-monitor.py` | Every hour | r/ChatGPT, r/ClaudeAI, r/LocalLLaMA, etc. (keyword-filtered) |
| `producthunt-monitor.py` | Every 6 hours | Top Product Hunt launches (RSS + votes) |
| `competitor-monitor.py` | Every 12 hours | YouTube channels of AI creators |
| `real-trends-monitor.py` | Every 6 hours | Google Trends via RSS |
| `topic-aggregator.py` | Every 2 hours | Cross-platform topic detection (3+ sources) |

**Key design decision:** Monitors run independently so if one breaks, it doesn't block the briefing. The briefing simply pulls the latest data from the database, regardless of how fresh it is.

---

### 2. Briefing Generation (`scripts/morning-briefing.py`)

**Runs:** 6:30am ET daily (cron)

**Process:**

1. **Refresh monitors** — Runs all monitor scripts with 3-minute timeouts to get latest data
2. **Query database** — Pulls data from each table (newsletter_stories, reddit_posts, producthunt_posts, etc.)
3. **Deduplicate** — Removes duplicate content by URL and normalized text (first 5 words)
4. **Format sections** — Builds Telegram Markdown sections with headers, links, emoji indicators
5. **Send to Telegram** — Posts to Analytics topic #29 (auto-splits if over 4096 chars)

---

### 3. Data Deduplication Strategy

**Problem:** Newsletter aggregators often republish the same story from the same source (e.g., "OpenAI announces X" appears in 3 different newsletters).

**Solution (aggressive dedup):**

1. **URL-based:** If two items have the same URL, keep only the first one
2. **Content-based:** Normalize text (remove punctuation, lowercase), take first 5 words, hash them
3. **Source-based:** If multiple newsletters mention the same story, combine senders ("The Neuron, Ben's Bites")

**Result:** 40 raw items → 10-12 unique items in final briefing.

---

### 4. Section Breakdown

Each section is conditionally included (only if data exists):

| Section | Primary Source | Secondary Signals |
|---------|---------------|-------------------|
| **CONTENT TOPICS** | Newsletter stories (newsletter_stories table) | Multi-source indicator (🔥 emoji) |
| **NUGGETS** | Newsletter nuggets (tutorial, tool, funding, etc.) | Grouped by category, max 3 per category |
| **REDDIT** | Reddit posts (reddit_posts table) | Filtered for substantive content (25+ chars, no memes) |
| **TRENDING** | Cross-platform topics (hot_topics table) | Only if 3+ platforms mention it |
| **Product Hunt** | Top launches (producthunt_posts table) | Votes + tagline descriptions |
| **YouTube** | Tracked channels (competitor_content table) | Creator name + video title |
| **Google Trends** | Trending searches (google_trends table) | Traffic volume if available |

---

### 5. Database Schema (Key Tables)

**newsletter_stories** — Individual stories from newsletters
```sql
CREATE TABLE newsletter_stories (
  id INTEGER PRIMARY KEY,
  headline TEXT,
  description TEXT,
  article_url TEXT,
  source_name TEXT,  -- "The Neuron, Ben's Bites" if multi-source
  relevance_score INTEGER,
  created_at TIMESTAMP
)
```

**newsletter_nuggets** — Actionable items (tools, tutorials, etc.)
```sql
CREATE TABLE newsletter_nuggets (
  id INTEGER PRIMARY KEY,
  category TEXT,  -- TUTORIAL, TOOL, FUNDING, HIRING, PROMPT, TIP, INSIGHT
  content TEXT,
  url TEXT,
  source_name TEXT,
  created_at TIMESTAMP
)
```

**reddit_posts** — Keyword-matched Reddit discussions
```sql
CREATE TABLE reddit_posts (
  id INTEGER PRIMARY KEY,
  title TEXT,
  subreddit TEXT,
  score INTEGER,
  num_comments INTEGER,
  permalink TEXT,
  keywords_matched TEXT,
  created_at TIMESTAMP
)
```

**hot_topics** — Cross-platform trending topics
```sql
CREATE TABLE hot_topics (
  id INTEGER PRIMARY KEY,
  topic TEXT,
  source_count INTEGER,  -- Must be >= 3
  sources TEXT,  -- JSON array of platforms
  mentions TEXT,  -- JSON array of specific mentions
  created_at TIMESTAMP
)
```

---

### 6. Newsletter Extraction Logic

**Problem:** Newsletters are messy — HTML emails with ads, unsubscribe links, images, and inconsistent formatting.

**Solution (LLM-powered extraction):**
1. Fetch email via Gmail API (or IMAP as fallback)
2. Extract plain text + HTML body
3. Pass to Claude with extraction prompt:
   ```
   Extract all stories and nuggets from this newsletter.

   Stories = news/announcements with headlines
   Nuggets = tools, tutorials, funding, tips, prompts, etc.

   Return JSON: { stories: [...], nuggets: [...] }
   ```
4. Parse JSON response
5. Insert into database with source attribution

**Key insight:** LLMs are surprisingly good at understanding "this is the real content vs. this is newsletter boilerplate."

---

### 7. Briefing Output Example

```markdown
🌅 *Friday, February 14, 2026*
52°F, Clear in Carle Place

_Finish strong._

📬 *CONTENT TOPICS* (from your newsletters)
• 🔥 [OpenAI releases GPT-5 with 10T parameters](https://example.com) _(The Neuron, Ben's Bites)_
  _OpenAI announced GPT-5 today with massive performance improvements..._
• [Anthropic's new Claude Artifacts SDK](https://example.com) _(Ben's Bites)_

💎 *NUGGETS* (from your newsletters)
*🛠 Tools*
  • [V0.dev now supports Svelte](https://v0.dev/svelte) _(The Neuron)_
  • [Cursor adds multi-file editing](https://cursor.sh) _(Ben's Bites)_

*📖 How-To*
  • [Building an AI agent with Claude Code](https://example.com) _(The Neuron)_

🔴 *REDDIT* (AI discussions & tools)
• [I built an AI that reads my email and drafts replies](https://reddit.com/...)
  r/ChatGPT | 847⬆ 203💬

🚀 *Product Hunt* (top launches, last 24h)
• [Cortana AI Assistant](https://producthunt.com/...) (234⬆)
  _Your AI chief of staff — email triage, briefings, follow-ups_

⚙️ Systems: cron ✅

_I am your sword, I am your shield._
```

---

## Deployment

**Location:** `/root/.openclaw/workspace/scripts/morning-briefing.py`

**Cron schedule:**
```bash
30 6 * * * /usr/bin/python3 /root/.openclaw/workspace/scripts/morning-briefing.py >> /root/.openclaw/workspace/logs/cron-morning.log 2>&1
```

**Environment variables required:**
- `TELEGRAM_BOT_TOKEN` — Telegram bot auth
- `TELEGRAM_CHAT_ID` — Target chat ID
- `AIRTABLE_PAT` — Airtable Personal Access Token (optional, for content queue)

**Dependencies:**
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests
```

---

## Performance

- **Briefing generation:** ~5-10 seconds (including monitor refresh)
- **Database queries:** <100ms total
- **Telegram delivery:** <1 second
- **Total runtime:** ~10-15 seconds end-to-end

**Database size:** ~50MB (6 months of data, auto-cleanup for >30 days old)

---

## Key Design Decisions

1. **Independent monitors** — Each data source runs on its own schedule, so failures don't cascade
2. **SQLite as central store** — Simple, fast, no external dependencies
3. **Aggressive dedup** — Better to miss a duplicate than overwhelm with repetition
4. **LLM for extraction** — Pattern-matching fails on messy newsletter HTML; Claude handles it perfectly
5. **Telegram as delivery** — Native mobile notifications, threaded topics for organization
6. **No web UI** — Ben reads briefings on his phone; web UI adds complexity with no UX gain

---

## Future Improvements

1. **Personalized relevance scoring** — Learn which topics Ben clicks on, surface similar content
2. **TL;DR summaries** — Auto-summarize long newsletter descriptions into 1-2 sentences
3. **Slack integration** — Deliver briefing to Slack workspace (useful for team visibility)
4. **Voice briefing** — Text-to-speech via ElevenLabs, deliver as audio file
5. **Interactive actions** — "Save to Airtable", "Add to calendar", "Remind me later" buttons

---

_Last updated: February 2026_
