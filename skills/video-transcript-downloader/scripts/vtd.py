#!/usr/bin/env python3
"""Video Transcript Downloader - download videos, audio, subtitles, and transcripts.

Usage:
    python3 vtd.py transcript --url "https://youtube.com/..."
    python3 vtd.py transcript --url "https://youtube.com/..." --timestamps
    python3 vtd.py download --url "https://youtube.com/..." --output-dir ~/Downloads
    python3 vtd.py audio --url "https://youtube.com/..." --output-dir ~/Downloads
    python3 vtd.py subs --url "https://youtube.com/..." --output-dir ~/Downloads
    python3 vtd.py formats --url "https://youtube.com/..."
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile


def get_transcript(url, lang="en", timestamps=False, keep_brackets=False):
    """Get transcript using yt-dlp subtitle extraction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "yt-dlp", "--write-auto-sub", "--skip-download",
            "--sub-lang", lang, "--sub-format", "vtt",
            "-o", os.path.join(tmpdir, "%(id)s.%(ext)s"),
            url
        ]
        subprocess.run(cmd, capture_output=True, text=True)

        vtt_files = [f for f in os.listdir(tmpdir) if f.endswith(".vtt")]
        if not vtt_files:
            cmd[2] = "--write-sub"
            subprocess.run(cmd, capture_output=True, text=True)
            vtt_files = [f for f in os.listdir(tmpdir) if f.endswith(".vtt")]

        if not vtt_files:
            print("No subtitles found for this video.", file=sys.stderr)
            sys.exit(1)

        vtt_path = os.path.join(tmpdir, vtt_files[0])
        with open(vtt_path, "r") as f:
            content = f.read()

        lines = []
        current_time = None
        seen = set()
        for line in content.split("\n"):
            line = line.strip()
            if "-->" in line:
                current_time = line.split(" --> ")[0]
                continue
            if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:") or line.isdigit():
                continue
            clean = re.sub(r"<[^>]+>", "", line)
            if not keep_brackets:
                clean = re.sub(r"\[.*?\]", "", clean)
            clean = clean.strip()
            if clean and clean not in seen:
                seen.add(clean)
                if timestamps and current_time:
                    lines.append(f"[{current_time}] {clean}")
                else:
                    lines.append(clean)

        if timestamps:
            return "\n".join(lines)
        else:
            return " ".join(lines)


def download_video(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cmd = ["yt-dlp", "-o", os.path.join(output_dir, "%(title)s.%(ext)s"), url]
    subprocess.run(cmd)


def download_audio(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "yt-dlp", "-x", "--audio-format", "mp3",
        "-o", os.path.join(output_dir, "%(title)s.%(ext)s"), url
    ]
    subprocess.run(cmd)


def download_subs(url, output_dir, lang="en"):
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "yt-dlp", "--write-auto-sub", "--write-sub", "--skip-download",
        "--sub-lang", lang, "-o", os.path.join(output_dir, "%(title)s.%(ext)s"), url
    ]
    subprocess.run(cmd)


def list_formats(url):
    cmd = ["yt-dlp", "--list-formats", url]
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="Video Transcript Downloader")
    parser.add_argument("action", choices=["transcript", "download", "audio", "subs", "formats"])
    parser.add_argument("--url", required=True)
    parser.add_argument("--output-dir", default=".")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--timestamps", action="store_true")
    parser.add_argument("--keep-brackets", action="store_true")
    args = parser.parse_args()

    if args.action == "transcript":
        print(get_transcript(args.url, args.lang, args.timestamps, args.keep_brackets))
    elif args.action == "download":
        download_video(args.url, args.output_dir)
    elif args.action == "audio":
        download_audio(args.url, args.output_dir)
    elif args.action == "subs":
        download_subs(args.url, args.output_dir, args.lang)
    elif args.action == "formats":
        list_formats(args.url)


if __name__ == "__main__":
    main()
