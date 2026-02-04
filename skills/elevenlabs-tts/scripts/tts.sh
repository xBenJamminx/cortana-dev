#!/bin/bash
# ElevenLabs TTS Script

# Source env if not set
if [ -z "$ELEVENLABS_API_KEY" ]; then
  [ -f /root/.openclaw/.env ] && source /root/.openclaw/.env
  [ -f /root/.bashrc ] && source /root/.bashrc
fi

if [ -z "$ELEVENLABS_API_KEY" ]; then
  echo "Error: ELEVENLABS_API_KEY is not set."
  exit 1
fi

TEXT="$1"
OUT_FILE="${2:-/tmp/elevenlabs_output.mp3}"
VOICE_ID="${3:-3JY1LL2MgjJ5HtZhEkm5}"
MODEL_ID="${4:-eleven_multilingual_v2}"

if [ -z "$TEXT" ]; then
  echo "Usage: $0 \"text\" [output_file] [voice_id] [model_id]"
  exit 1
fi

curl -s -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID"      -H "xi-api-key: $ELEVENLABS_API_KEY"      -H "Content-Type: application/json"      -d "{
       \"text\": $(echo "$TEXT" | jq -R .),
       \"model_id\": \"$MODEL_ID\",
       \"voice_settings\": {
         \"stability\": 0.5,
         \"similarity_boost\": 0.75
       }
     }"      --output "$OUT_FILE"

if [ -f "$OUT_FILE" ] && [ -s "$OUT_FILE" ]; then
  echo "Audio saved to $OUT_FILE"
else
  echo "Error: Failed to generate audio"
  exit 1
fi
