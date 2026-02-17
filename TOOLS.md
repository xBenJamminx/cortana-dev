# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics -- the stuff that's unique to your setup.

## SSH
- `openclaw` -- main server (IP in .env)
- User: root

## TTS (ElevenLabs)
- Voice ID: `3JY1LL2MgjJ5HtZhEkm5`
- Model: `eleven_multilingual_v2`
- Use `/elevenlabs_tts` or the voice tool

## Voice Calls
- ALWAYS use: `/root/.openclaw/workspace/skills/vapi-call/vapi-call <number> [message]`
- NEVER craft custom VAPI curl calls

## Image Generation
- Use: `uv run ~/.codex/skills/nano-banana-pro/scripts/generate_image.py --prompt "..." --filename "output.png"`
- NOT Hugging Face MCP (tiny quota)

## Twitter/X
- Posting: Use Composio `TWITTER_CREATION_OF_A_POST` or X OAuth
- X OAuth tokens: `/root/.config/x-oauth/tokens.json`
- Refresh: `python3 /root/.openclaw/workspace/scripts/cortana-x-oauth-setup.py --refresh`
- Bird CLI: DEAD (discontinued by author)

## Content Pipeline
- Airtable base: `appdFTSkXnphHLwfl`
- Content table: `tblvLSX7DZxIRWU5g`
- ALL content drafts go here, not local md files

## Secrets
- All API keys: `/root/.openclaw/.env`
- Source it: `source /root/.openclaw/.env`
- Python: use `_load_env()` pattern

---

Add whatever helps you do your job. This is your cheat sheet.
