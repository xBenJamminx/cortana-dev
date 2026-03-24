# Context: Auth & API Access

## Telegram
- BOT_TOKEN + CHAT_ID in `~/.openclaw/.env`
- CHAT_ID = group `-1003856131939` (NOT Ben's DM)
- ALWAYS reply to same topic: check topic ID, use `--topic <id>`
- Topics: 20=Content, 22=Research, 26=Ideas, 29=Analytics, 31=Business
- Text: `python3 /root/.openclaw/workspace/core/integrations/telegram.py --topic <id> "message"`
- Images: `curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendPhoto" -F "chat_id=$CHAT_ID" -F "message_thread_id=$TOPIC" -F "photo=@/path/to/image.png" -F "caption=text"`

## Twitter (@xBenJamminx) -- SUSPENDED
- AUTH_TOKEN/CT0 in ~/.bashrc; Bird CLI cookies in ~/.bird-env
- DO NOT use Bird CLI until suspension resolved

## Twitter (@CortanaOps / @BuildsByBen)
- Bird CLI cookies in ~/.bird-env (CORTANA_BIRD_AUTH_TOKEN/CORTANA_BIRD_CT0)
- Composio Twitter auth is DEAD (X suspended managed credentials Feb 9)

## Airtable
- API key: `<AIRTABLE_API_KEY from ~/.openclaw/.env>`
- AI Viral Content OS: `appzyTeggE9zr0ZBm`
- Cortana OS: `appdFTSkXnphHLwfl`
- Content Pipeline table: `tblvLSX7DZxIRWU5g`

## Image Generation (Gemini/Imagen)
- `generate_image_gemini(prompt, output_path, model, aspect_ratio)` in `core/integrations/imagegen.py`
- Models: `imagen-4.0-ultra-generate-001` ($0.06), `imagen-4.0-generate-001` ($0.04), `imagen-4.0-fast-generate-001` ($0.02), `gemini-3-pro-image-preview`
- Auth: `GEMINI_API_KEY` in `~/.openclaw/.env`
- Aspect ratios: "16:9", "9:16", "3:4", "1:1"
- Fallbacks: OpenAI DALL-E (`core/integrations/slideshow.py`), Pexels stock (`core/integrations/pexels.py`)

## YouTube
- OAuth in `~/.config/youtube/credentials.json` + `/root/.openclaw/google_credentials.json`

## GitHub
- Via Composio (no local gh CLI auth)

## AgentMail
- Email: cortana-ops@agentmail.to
- API key: AGENTMAIL_API_KEY in `~/.openclaw/.env`
- API base: `https://api.agentmail.to/v0`
- Endpoints: /inboxes, /inboxes/{id}/messages/send, /inboxes/{id}/messages, /inboxes/{id}/threads

## Notion (three keys)
- Home (benjoselson@gmail.com): NOTION_API_KEY in `~/.openclaw/.env`
- Work / FAM: NOTION_API_KEY_WORK -- USE THIS for FAM POC database (26c4666bd1ca807b930dca5ffff9c8e9)
- Products (bjoselson27@gmail.com): NOTION_PRODUCTS_API_KEY in `~/.openclaw/.env`
- Creator Brain DB IDs: `/tmp/creator_brain_ids.json`

## Discord
- Bot "Cortana" -- token, guild ID, app ID in `~/.openclaw/.env`
- Server: EverydayAI (799385636515086336)

## Google Calendar
- Full API access via `/root/.openclaw/google_credentials.json`

## Fathom (meeting recordings)
- API key: FATHOM_API_KEY in `~/.openclaw/.env`
- Webhook secret: FATHOM_WEBHOOK_SECRET in `~/.openclaw/.env`
- Base URL: `https://api.fathom.ai/external/v1`
- Helper: `python3 /root/.openclaw/workspace/core/fathom/client.py`
  - `fathom.py meetings [--limit N]` — list recent meetings
  - `fathom.py today` — today's meetings
  - `fathom.py meeting <recording_id>` — full meeting with transcript + summary + actions
  - `fathom.py transcript <recording_id>` — just transcript
  - `fathom.py summary <recording_id>` — summary + action items
  - `fathom.py search <query>` — search by title
- Use this INSTEAD of Slack #meeting-notes for getting meeting content directly

## Firecrawl (web scraping/search)
- API key: FIRECRAWL_API_KEY in `~/.openclaw/.env`
- CLI: `firecrawl` (installed globally via npm)
- **Free tier: 500 page cap. Use wisely.**
- Commands:
  - `firecrawl <url>` — scrape any page to markdown
  - `firecrawl search "query" --limit N` — web search
  - `firecrawl map <url>` — discover all URLs on a site
  - `firecrawl crawl <url>` — spider a site
  - `firecrawl browser` — cloud browser sessions
- Tip: X/Twitter is blocked by Firecrawl directly. Use nitter.net mirror: `firecrawl https://nitter.net/user/status/ID`
- ALWAYS set `export FIRECRAWL_API_KEY=fc-...` before running commands
- Check credits: `firecrawl --status`

## Scrapling (stealth local scraping)
- Python package: `from scrapling import Fetcher, StealthFetcher, PlayWrightFetcher`
- **Free, open-source, runs locally — no credits/limits**
- Best for: anti-bot bypass, adaptive element tracking, dynamic content
- StealthFetcher handles Cloudflare/bot protection
- Use BEFORE Firecrawl when possible to save credits

## Scrapy (heavy-duty crawling)
- Python package: `import scrapy`
- **Free, open-source, runs locally — no credits/limits**
- Best for: large-scale structured data extraction, spider frameworks
- Use for bulk crawling jobs (competitor sites, data pipelines)

## Cloudflare Browser Rendering /crawl
- Endpoint: `POST /accounts/{account_id}/browser-rendering/crawl`
- **Free on Workers (Free + Paid plans)**
- Best for: bulk website crawling, sitemaps, incremental updates
- Returns HTML, Markdown, or structured JSON
- Supports `modifiedSince` / `maxAge` for incremental crawls
- Needs: Cloudflare account_id + API token in env
- PARKED — account_id + token in env but auth failing. Revisit later.

## Web Scraping Decision Tree
1. **Quick URL read or web search** → Firecrawl (costs 1 credit)
2. **Anti-bot / protected site** → Scrapling StealthFetcher (free)
3. **Bulk crawl / full site** → Cloudflare /crawl or Scrapy (free)
4. **X/Twitter post** → Firecrawl via nitter mirror (1 credit)

## Composio
- MCP_URL + API_KEY in `~/.openclaw/.env`
- CortanaOps connection: `2aea494d-2229-40b5-b07b-e1bbeac730af`

## Slack (smart.companion.poc)
- Bot: cortana (user_id=U0ABR0SER62, bot_id=B0ABWKXBFEG)
- Workspace: smartcompanionpoc.slack.com (team_id=T08K8GFMEEQ)
- Token: SLACK_BOT_TOKEN in ~/.openclaw/.env
- HOW TO USE: python3 core/integrations/slack.py meeting-notes 10
- List channels: python3 core/integrations/slack.py --list
- DO NOT use MCP tools or composio for Slack. Use core/integrations/slack.py.
- YOU HAVE FULL ACCESS. You have been reading #meeting-notes and updating Notion all week.
- Key channels:
  - #meeting-notes  C09J78SH2FM
  - #poc            C08K8GH4ZGU
  - #testing        C08MV404LVD
  - #action-agents  C09LK4E6873
  - #alert-errors   C0A7338719D
- Read messages: GET https://slack.com/api/conversations.history?channel=<id>&limit=20
  with header: Authorization: Bearer $SLACK_BOT_TOKEN
- List channels: GET https://slack.com/api/conversations.list
