---
name: gemini-speech
description: This skill should be used when working with Gemini speech generation, especially for promptable TTS, transcript tags, multi-speaker audio, style direction, or building reliable Gemini 3.1 Flash TTS preview workflows.
---

# Gemini Speech

Use this skill for Gemini speech generation work based on the official speech-generation docs.

## Purpose

Generate Gemini TTS audio reliably with the correct model, usable prompting structure, and directable transcript tags. Avoid the common failure mode of using the wrong preview model or overloading one prompt with too many competing directions.

## When to use

Use this skill when the task involves any of the following:
- generating speech with Gemini TTS
- comparing Gemini speech against another provider
- steering tone, pacing, accent, or delivery with prompts
- using transcript tags like `[whispers]`, `[shouting]`, `[excited]`, or `[short pause]`
- building multi-speaker Gemini speech
- testing whether Gemini can hit specific performance beats, like a sung final line

## Core rules

1. Use `gemini-3.1-flash-tts-preview` unless the user explicitly asks for another model.
2. Send finished audio as actual attachments on chat surfaces when the user needs to listen.
3. Keep transcript tags in English, even for non-English transcripts, unless a test proves otherwise.
4. Do not overload one prompt with too many stage directions. If a specific line matters, isolate it or simplify the surrounding directions.
5. Match the voice to the intended performance. Use the voice list in `references/speech-generation-notes.md`.
6. For multi-speaker generation, ensure speaker names in config exactly match speaker names in transcript text.

## Practical workflow

### 1. Choose the prompt strategy

Use the lightest strategy that can work:
- For simple tone changes, use natural-language direction only.
- For inline delivery control, use transcript tags.
- For complex acting, combine a short advanced prompt with selective tags.
- For critical moments, isolate the key line into a separate request instead of making one overloaded mega-prompt.

### 2. Structure the prompt correctly

For simple single-speaker prompts:
- Start with brief performance direction.
- Put the transcript after it.
- Add tags only where the delivery needs to change.

For advanced prompts, use this shape:
- Audio Profile
- Scene
- Director's Notes
- Sample Context
- Transcript
- Audio Tags

Do not overspecify every detail. The docs explicitly warn that too many strict rules can hurt performance.

### 3. Generate with the bundled script

Use:

```bash
python3 /root/.openclaw/workspace/skills/gemini-speech/scripts/generate_gemini_speech.py \
  --text-file /path/to/transcript.txt \
  --voice Puck \
  --output /path/to/output.wav
```

Inline text also works:

```bash
python3 /root/.openclaw/workspace/skills/gemini-speech/scripts/generate_gemini_speech.py \
  --text "[whispers] test line" \
  --voice Puck \
  --output /path/to/output.wav
```

For multi-speaker:

```bash
python3 /root/.openclaw/workspace/skills/gemini-speech/scripts/generate_gemini_speech.py \
  --text-file /path/to/dialogue.txt \
  --multi "Joe=Kore,Jane=Puck" \
  --output /path/to/dialogue.wav
```

## Recommended testing pattern

For comparison work, generate small targeted tests instead of one giant sample:
- baseline read
- tag-driven expressive read
- isolated difficult line
- alternate Gemini voice
- multi-speaker if relevant

This makes failures obvious and keeps iteration fast.

## Bundled resources

- Script: `scripts/generate_gemini_speech.py`
- Reference notes: `references/speech-generation-notes.md`

Read the reference file when choosing voices, tags, or advanced prompting structure.
