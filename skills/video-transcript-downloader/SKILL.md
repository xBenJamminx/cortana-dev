---
name: video-transcript-downloader
description: Download videos, audio, subtitles, and clean paragraph-style transcripts from YouTube and any other yt-dlp supported site. Use when asked to "download this video", "save this clip", "rip audio", "get subtitles", "get transcript", or to troubleshoot yt-dlp/ffmpeg and formats/playlists.
---

# Video Transcript Downloader

`python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py` can:
- Print a transcript as a clean paragraph (timestamps optional).
- Download video/audio/subtitles.

Uses `yt-dlp` + `ffmpeg` (both installed).

## Transcript (default: clean paragraph)

```bash
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py transcript --url 'https://...'
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py transcript --url 'https://...' --lang en
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py transcript --url 'https://...' --timestamps
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py transcript --url 'https://...' --keep-brackets
```

## Download video / audio / subtitles

```bash
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py download --url 'https://...' --output-dir ~/Downloads
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py audio --url 'https://...' --output-dir ~/Downloads
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py subs --url 'https://...' --output-dir ~/Downloads --lang en
```

## Formats (list + choose)

```bash
python3 /root/.openclaw/workspace/skills/video-transcript-downloader/scripts/vtd.py formats --url 'https://...'
```

## Notes

- Default transcript output is a single paragraph. Use `--timestamps` only when asked.
- Bracketed cues like `[Music]` are stripped by default; keep them via `--keep-brackets`.
- Dependencies: `yt-dlp` (/usr/local/bin/yt-dlp) and `ffmpeg` (/usr/bin/ffmpeg) are installed.
