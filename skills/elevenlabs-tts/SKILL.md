---
name: elevenlabs-tts
description: Text-to-speech via ElevenLabs API. Generate audio files or voice messages.
metadata: {"clawdbot":{"emoji":"🔊","requires":{"env":["ELEVENLABS_API_KEY"],"bins":["curl","jq"]},"primaryEnv":"ELEVENLABS_API_KEY"}}
---

# ElevenLabs TTS

Generate high-quality speech using ElevenLabs.

## Usage

```bash
{baseDir}/scripts/tts.sh "Hello world" /tmp/output.mp3
```

Default Voice: Cortana (3JY1LL2MgjJ5HtZhEkm5)
Default Model: eleven_multilingual_v2
