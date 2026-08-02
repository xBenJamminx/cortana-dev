# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics -- the stuff that's unique to your setup.

## SSH
- `openclaw` -- legacy-named main server alias retained for compatibility (host details stay outside the repository)
- User: root

## TTS (ElevenLabs)
- Voice ID: `3JY1LL2MgjJ5HtZhEkm5`
- Model: `eleven_multilingual_v2`
- Use `/elevenlabs_tts` or the voice tool

## Voice Calls
- From the repository root use: `skills/vapi-call/vapi-call <number> [message]`
- NEVER craft custom VAPI curl calls

## Image Generation
- Use the installed Hermes image-generation tool/skill. Repository fallback: `skills/nano-banana-pro/`.
- NOT Hugging Face MCP (tiny quota)

## Twitter/X
- Posting: Use Composio `TWITTER_CREATION_OF_A_POST` or X OAuth
- X OAuth tokens: `/root/.config/x-oauth/tokens.json`
- Refresh from the repository root: `python3 scripts/cortana-x-oauth-setup.py --refresh`
- Bird CLI: DEAD (discontinued by author)

## Content Pipeline
- Airtable base: `appdFTSkXnphHLwfl`
- Content table: `tblvLSX7DZxIRWU5g`
- ALL content drafts go here, not local md files

## Secrets
- Runtime API keys: `~/.hermes/.env` or the integration's secure credential store
- Source only when a local script requires it: `set -a; source ~/.hermes/.env; set +a`
- Python: use `_load_env()` pattern (`lib/env.py`)
- Saving a key: edit the secrets file directly. See `context/auth.md`. Never commit it.

---

Add whatever helps you do your job. This is your cheat sheet.
