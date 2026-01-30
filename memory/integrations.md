# Cortana Integrations & API Access

Last updated: 2026-01-30 by Claude Code

## Model Providers (All Working)

| Provider | Auth Status | Models Available |
|----------|-------------|------------------|
| OpenRouter | ✅ Configured | openrouter/auto (smart routing), openrouter/moonshotai/kimi-k2.5 |
| Google | ✅ Configured | google/gemini-3-flash-preview, google/gemini-3-pro-preview, google/gemini-2.5-flash |
| Anthropic | ✅ Configured | anthropic/claude-sonnet-4-5, anthropic/claude-opus-4-5 |
| Moonshot | ⚠️ Suspended | moonshot/kimi-k2.5 - account suspended due to insufficient balance |

### Current Config
- Primary: openrouter/auto (smart routing with Guardrails)
- Fallbacks: google/gemini-3-flash-preview, anthropic/claude-sonnet-4-5

### Model Aliases (use these in chat)
- auto → OpenRouter Auto (smart routing)
- gemini → Google Gemini 3 Flash
- gemini3-pro → Google Gemini 3 Pro  
- sonnet → Claude Sonnet 4.5
- opus → Claude Opus 4.5 (expensive, use sparingly)
- kimi → Kimi K2.5 (direct Moonshot - SUSPENDED)
- kimi-or → Kimi K2.5 via OpenRouter

## Ready-to-Use Skills (18 total)

| Skill | Description | Status |
|-------|-------------|--------|
| bird | X/Twitter CLI - reading, searching, posting | ✅ Cookie-based |
| github | GitHub CLI (gh) - issues, PRs, repos | ✅ SSH key auth |
| goplaces | Google Places search | ✅ API key configured |
| local-places | Local place search | ✅ API key configured |
| nano-banana-pro | Gemini image generation | ✅ API key configured |
| openai-image-gen | OpenAI DALL-E image generation | ✅ API key configured |
| openai-whisper-api | Audio transcription | ✅ API key configured |
| sag | ElevenLabs text-to-speech | ✅ API key configured |
| elevenlabs | ElevenLabs TTS | ✅ API key configured |
| notion | Notion API | ⚠️ Needs setup |
| slack | Slack messaging | ✅ Configured |
| tmux | Terminal session control | ✅ Local |
| weather | Weather forecasts | ✅ No key needed |
| coding-agent | Run Codex/Claude Code | ✅ Local |
| clawdhub | Install/update skills | ✅ Local |
| mcporter | MCP server control | ✅ Local |
| skill-creator | Create new skills | ✅ Local |
| composio-tool-router | AI agent tools | ✅ Local |

## Channel Integrations

| Channel | Status | Details |
|---------|--------|---------|
| Telegram | ✅ Working | @Cortana_MoltBot |
| Slack | ✅ Working | Socket mode enabled |

## Web Tools

| Tool | Status |
|------|--------|
| Web Search | ✅ Enabled (Wolfram Alpha API) |
| Web Fetch | ✅ Enabled |
| Browser | ✅ Headless Chrome at port 18800 |

## Important Notes

1. OpenRouter Auto uses the "Cortana Auto" guardrail which limits to: Gemini 3 Flash, Kimi K2.5, Gemini 3 Pro, Nano Banana (for images)

2. Direct Moonshot is SUSPENDED - use kimi-or (via OpenRouter) instead

3. Anthropic has rate limits - if hitting 429 errors, fall back to Gemini

4. To switch models, Ben can say "use gemini" or "use opus"

## What You CAN Do

- Generate images with nano-banana-pro or openai-image-gen
- Search Twitter/X and post tweets with bird skill
- Transcribe audio with openai-whisper-api
- Text-to-speech with sag/elevenlabs
- Search places with goplaces
- Manage GitHub issues/PRs
- Search the web
- Fetch web pages
- Control terminal sessions with tmux
- Get weather forecasts
