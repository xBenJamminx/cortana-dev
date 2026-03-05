# Context: Auth & API Access

## Telegram
- BOT_TOKEN + CHAT_ID in `~/.openclaw/.env`
- CHAT_ID = group `-1003856131939` (NOT Ben's DM)
- ALWAYS reply to same topic: check topic ID, use `--topic <id>`
- Topics: 20=Content, 22=Research, 26=Ideas, 29=Analytics, 31=Business
- Text: `python3 /root/.openclaw/workspace/lib/telegram.py --topic <id> "message"`
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
- `generate_image_gemini(prompt, output_path, model, aspect_ratio)` in `lib/imagegen.py`
- Models: `imagen-4.0-ultra-generate-001` ($0.06), `imagen-4.0-generate-001` ($0.04), `imagen-4.0-fast-generate-001` ($0.02), `gemini-3-pro-image-preview`
- Auth: `GEMINI_API_KEY` in `~/.openclaw/.env`
- Aspect ratios: "16:9", "9:16", "3:4", "1:1"
- Fallbacks: OpenAI DALL-E (`lib/slideshow.py`), Pexels stock (`lib/pexels.py`)

## YouTube
- OAuth in `~/.config/youtube/credentials.json` + `/root/.openclaw/google_credentials.json`

## GitHub
- Via Composio (no local gh CLI auth)

## AgentMail
- Email: cortana-ops@agentmail.to
- API key: AGENTMAIL_API_KEY in `~/.openclaw/.env`
- API base: `https://api.agentmail.to/v0`
- Endpoints: /inboxes, /inboxes/{id}/messages/send, /inboxes/{id}/messages, /inboxes/{id}/threads

## Notion (two workspaces)
- Main (benjoselson@gmail.com): NOTION_API_KEY in `~/.openclaw/.env`
- Products (bjoselson27@gmail.com): NOTION_PRODUCTS_API_KEY in `~/.openclaw/.env`
- Creator Brain DB IDs: `/tmp/creator_brain_ids.json`

## Discord
- Bot "Cortana" -- token, guild ID, app ID in `~/.openclaw/.env`
- Server: EverydayAI (799385636515086336)

## Google Calendar
- Full API access via `/root/.openclaw/google_credentials.json`

## Composio
- MCP_URL + API_KEY in `~/.openclaw/.env`
- CortanaOps connection: `2aea494d-2229-40b5-b07b-e1bbeac730af`

## Slack (smart.companion.poc)
- Bot: cortana (user_id=U0ABR0SER62, bot_id=B0ABWKXBFEG)
- Workspace: smartcompanionpoc.slack.com (team_id=T08K8GFMEEQ)
- Token: SLACK_BOT_TOKEN in ~/.openclaw/.env
- HOW TO USE: python3 lib/slack.py meeting-notes 10
- List channels: python3 lib/slack.py --list
- DO NOT use MCP tools or composio for Slack. Use lib/slack.py.
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
