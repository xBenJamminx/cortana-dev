"""ElevenLabs API client for text-to-speech voiceovers."""

import json
import os
import urllib.request

API_BASE = "https://api.elevenlabs.io/v1"

# Popular voices
VOICES = {
    "cortana": "3JY1LL2MgjJ5HtZhEkm5",   # Custom generated — Cortana
    "frank": "V2bPluzT7MuirpucVAKH",      # Wise, deep, motivational storyteller
    "declan": "kqVT88a5QfII1HNAEPTJ",     # Wise, deliberate, captivating
    "theo": "lnbHqRFwMGU7M66Bf2ny",       # Smooth southern storyteller
    "rachel": "21m00Tcm4TlvDq8ikWAM",     # Female, calm
    "adam": "pNInz6obpgDQGcFmaJgB",       # Male, deep
    "sam": "yoZ06aMxZJJ28mfd3POQ",        # Male, narrative
    "josh": "TxGEqnHWrfWFTfGW9XjX",      # Male, young
    "bella": "EXAVITQu4vr4xnSDxMaL",     # Female, soft
}


def _get_key():
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        with open("/root/.openclaw/.env") as f:
            for line in f:
                if line.startswith("ELEVENLABS_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    break
    return key


def text_to_speech(text, output_path, voice="adam", model="eleven_multilingual_v2",
                   stability=0.5, similarity_boost=0.75):
    """Generate speech from text and save to file.

    Args:
        text: The text to speak
        output_path: Path to save the MP3 file
        voice: Voice name (rachel, adam, sam, josh, bella) or voice ID
        model: ElevenLabs model ID
        stability: Voice stability (0-1)
        similarity_boost: Voice similarity boost (0-1)

    Returns:
        output_path on success
    """
    key = _get_key()
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY not found")

    voice_id = VOICES.get(voice, voice)
    url = f"{API_BASE}/text-to-speech/{voice_id}"

    data = json.dumps({
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
        },
    }).encode()

    req = urllib.request.Request(url, data=data, headers={
        "xi-api-key": key,
        "Content-Type": "application/json",
    })

    resp = urllib.request.urlopen(req, timeout=120)
    with open(output_path, "wb") as f:
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            f.write(chunk)
    return output_path


def get_voices():
    """List all available voices."""
    key = _get_key()
    req = urllib.request.Request(f"{API_BASE}/voices", headers={"xi-api-key": key})
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read())
    return [{"id": v["voice_id"], "name": v["name"], "category": v.get("category", "")}
            for v in data.get("voices", [])]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python elevenlabs.py <text> <output.mp3> [voice]")
        sys.exit(1)
    text = sys.argv[1]
    out = sys.argv[2]
    voice = sys.argv[3] if len(sys.argv) > 3 else "adam"
    text_to_speech(text, out, voice=voice)
    print(f"Saved to {out}")
