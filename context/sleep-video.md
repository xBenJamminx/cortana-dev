# Context: Sleep Video Pipeline

## Interactive Pipeline
- Script: `lib/sleep_interactive.py` (step-by-step with Telegram approval gates)

## Voice Defaults by Genre
- **Stoic/Philosophy:** Frank (`V2bPluzT7MuirpucVAKH`) -- deep, wise, motivational
- **General/Nature:** Cortana (`3JY1LL2MgjJ5HtZhEkm5`) -- custom generated
- **Alternatives:** Declan (wise, deliberate), Theo (smooth storyteller)

## Background Music (royalty-free, require YouTube attribution)
- Piano (Scott Buckley - Sleep) -> calm/meditation/nature (CC-BY 4.0)
- Choir+Harp (Kevin MacLeod - Frozen Star) -> stoic/philosophy (CC-BY 3.0)
- Strings (Scott Buckley - Hiraeth) -> dramatic/epic (CC-BY 4.0)
- Use `select_music()` instead of `generate_ambient()`
- Tracks in `assets/music/`

## Audio Mixing
- Narration normalized to -16 LUFS
- Music at volume 5.0 (source tracks are quiet ~-35dB, amix halves inputs)
- amix weights=1 0.8, limiter at 0.95
- Voice starts immediately (no title card delay on audio)

## Image Generation
- Use `lib/imagegen.py` with Gemini/Imagen API
- DO NOT use 8000px Ken Burns zoompan (Imagen outputs 1408x768, causes timeouts)
- Use "still" effect (scale+crop) or 2200px max
- Crossfades between scenes provide enough visual movement

## Title Cards
- Generate SEPARATE dark image (deep navy, charcoal, no warm tones)
- Darken to 75% minimum
- Never reuse scene images for title cards

## Audio Timing
- Ambient/bg music starts at second 0
- Narration delayed by title_duration (8s) via `adelay` filter
- Scene durations account for crossfade time loss
- When pipeline handles mixing, pass `audio_pre_mixed=True` to `assemble_sleep_video()`

## Ambient Audio
- Use ElevenLabs sound generation API, NOT synthetic FFmpeg noise
