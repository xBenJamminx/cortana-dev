#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import wave
from pathlib import Path

import requests

API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
MODEL = 'gemini-3.1-flash-tts-preview'
API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'


def build_payload(text: str, voice: str, multi: str | None = None) -> dict:
    speech_config = {
        'voiceConfig': {
            'prebuiltVoiceConfig': {
                'voiceName': voice,
            }
        }
    }
    if multi:
        speaker_configs = []
        for item in multi.split(','):
            speaker, speaker_voice = item.split('=', 1)
            speaker_configs.append({
                'speaker': speaker.strip(),
                'voiceConfig': {
                    'prebuiltVoiceConfig': {
                        'voiceName': speaker_voice.strip()
                    }
                }
            })
        speech_config = {
            'multiSpeakerVoiceConfig': {
                'speakerVoiceConfigs': speaker_configs
            }
        }
    return {
        'contents': [{'parts': [{'text': text}]}],
        'generationConfig': {
            'responseModalities': ['AUDIO'],
            'speechConfig': speech_config,
        },
    }


def save_audio(raw: bytes, output_path: Path, mime: str | None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if mime and 'wav' in mime:
        output_path.write_bytes(raw)
        return
    with wave.open(str(output_path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(raw)


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate speech with Gemini 3.1 Flash TTS Preview')
    parser.add_argument('--text', help='Inline transcript/prompt text')
    parser.add_argument('--text-file', help='Path to text file containing transcript/prompt')
    parser.add_argument('--voice', default='Puck', help='Single-speaker Gemini voice name')
    parser.add_argument('--multi', help='Comma-separated speaker=Voice pairs, e.g. Joe=Kore,Jane=Puck')
    parser.add_argument('--output', required=True, help='Output wav path')
    args = parser.parse_args()

    if not API_KEY:
        raise RuntimeError('Missing GEMINI_API_KEY or GOOGLE_API_KEY')
    if not args.text and not args.text_file:
        raise RuntimeError('Provide --text or --text-file')

    text = args.text or Path(args.text_file).read_text()
    payload = build_payload(text=text.strip(), voice=args.voice, multi=args.multi)
    resp = requests.post(
        API_URL,
        headers={'x-goog-api-key': API_KEY, 'Content-Type': 'application/json'},
        data=json.dumps(payload),
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()

    audio_b64 = None
    mime = None
    for part in data.get('candidates', [{}])[0].get('content', {}).get('parts', []):
        if 'inlineData' in part:
            audio_b64 = part['inlineData']['data']
            mime = part['inlineData'].get('mimeType')
            break
    if not audio_b64:
        raise RuntimeError(f'No audio returned: {json.dumps(data)[:4000]}')

    raw = base64.b64decode(audio_b64)
    output_path = Path(args.output)
    save_audio(raw, output_path, mime)
    print(output_path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
