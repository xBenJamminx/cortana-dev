# Gemini Speech Generation Notes

Source: https://ai.google.dev/gemini-api/docs/speech-generation

## Core model
- Primary current model: `gemini-3.1-flash-tts-preview`
- Input: text
- Output: audio
- Token limits: 8,192 input, 16,384 output
- Sample output handling from REST docs decodes inline base64 PCM and converts with ffmpeg using `-f s16le -ar 24000 -ac 1`

## Single-speaker control
- Use natural-language prompting for tone, pace, accent, and style
- Use inline transcript/audio tags for finer control
- There is no exhaustive supported-tag list, so experimentation matters
- English tags are recommended even when the transcript is not English

## Common tags mentioned by docs
- `[amazed]`
- `[crying]`
- `[curious]`
- `[excited]`
- `[sighs]`
- `[gasp]`
- `[giggles]`
- `[laughs]`
- `[mischievously]`
- `[panicked]`
- `[sarcastic]`
- `[serious]`
- `[shouting]`
- `[tired]`
- `[trembling]`
- `[whispers]`
- Also shown in examples: `[short pause]`, `[yawn]`, `[very fast]`, `[very slow]`, `[like dracula]`, `[like a cartoon dog]`

## Prompting guidance from docs
A strong advanced prompt can include:
1. Audio Profile
2. Scene
3. Director's Notes
4. Sample Context
5. Transcript
6. Audio Tags

Docs explicitly warn against over-specifying. Too many rigid constraints can make performance worse.

## Voice list from docs
- Zephyr — Bright
- Puck — Upbeat
- Charon — Informative
- Kore — Firm
- Fenrir — Excitable
- Leda — Youthful
- Orus — Firm
- Aoede — Breezy
- Callirrhoe — Easy-going
- Autonoe — Bright
- Enceladus — Breathy
- Iapetus — Clear
- Umbriel — Easy-going
- Algieba — Smooth
- Despina — Smooth
- Erinome — Clear
- Algenib — Gravelly
- Rasalgethi — Informative
- Laomedeia — Upbeat
- Achernar — Soft
- Alnilam — Firm
- Schedar — Even
- Gacrux — Mature
- Pulcherrima — Forward
- Achird — Friendly
- Zubenelgenubi — Casual
- Vindemiatrix — Gentle
- Sadachbia — Lively
- Sadaltager — Knowledgeable
- Sulafat — Warm

## Multi-speaker
- Supported in `gemini-3.1-flash-tts-preview`
- Up to 2 speakers shown in docs
- Speaker names in `multiSpeakerVoiceConfig` must match names used in transcript prompt

## Practical lessons learned in this workspace
- Use the correct model first. Older preview TTS models will give misleading comparisons.
- For Telegram or similar channels, send finished audio as actual attachments, not just file paths.
- If a specific line needs to sound sung, isolate it or reduce competing instructions. Too many style changes in one pass degrades compliance.
- Gemini is stronger than standard TTS at actable direction, but it can still miss one instruction in overloaded prompts.
