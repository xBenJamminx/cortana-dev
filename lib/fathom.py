#!/usr/bin/env python3
"""Fathom meeting helper — pull meetings, transcripts, summaries, action items.

Usage:
    python3 lib/fathom.py meetings [--limit N]
    python3 lib/fathom.py transcript <recording_id>
    python3 lib/fathom.py summary <recording_id>
    python3 lib/fathom.py meeting <recording_id>          # full meeting with transcript + summary + actions
    python3 lib/fathom.py today                            # today's meetings
    python3 lib/fathom.py search <query>                   # search meeting titles
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Load env
env_path = Path.home() / ".openclaw" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key = key.strip().lstrip("export").strip()
            os.environ.setdefault(key, val.strip())

API_KEY = os.environ.get("FATHOM_API_KEY", "")
BASE_URL = "https://api.fathom.ai/external/v1"


def api_get(path, params=None):
    url = f"{BASE_URL}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    req = Request(url, headers={"X-Api-Key": API_KEY})
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def list_meetings(limit=10, created_after=None):
    params = {"include_transcript": "false"}
    if created_after:
        params["created_after"] = created_after
    data = api_get("/meetings", params)
    items = data.get("items", [])[:limit]
    return items


def get_meeting_full(recording_id):
    params = {"include_transcript": "true"}
    data = api_get("/meetings", params)
    for m in data.get("items", []):
        if str(m.get("recording_id")) == str(recording_id):
            return m
    return None


def get_transcript(recording_id):
    data = api_get(f"/recordings/{recording_id}/transcript")
    return data


def get_summary(recording_id):
    data = api_get(f"/recordings/{recording_id}/summary")
    return data


def format_meeting_short(m):
    title = m.get("meeting_title") or m.get("title", "Untitled")
    rid = m.get("recording_id", "?")
    created = m.get("created_at", "")[:10]
    start = m.get("recording_start_time", "")
    end = m.get("recording_end_time", "")
    duration = ""
    if start and end:
        try:
            s = datetime.fromisoformat(start.replace("Z", "+00:00"))
            e = datetime.fromisoformat(end.replace("Z", "+00:00"))
            mins = int((e - s).total_seconds() / 60)
            duration = f" ({mins} min)"
        except Exception:
            pass
    invitees = [i.get("name", i.get("email", "")) for i in m.get("calendar_invitees", [])]
    inv_str = ", ".join(invitees[:5]) if invitees else ""
    return f"[{rid}] {created} — {title}{duration}\n    Participants: {inv_str}"


def format_transcript(transcript):
    if not transcript:
        return "(no transcript)"
    lines = []
    for entry in transcript:
        speaker = entry.get("speaker_display_name", entry.get("speaker", "Unknown"))
        # speaker might be a dict with display_name
        if isinstance(speaker, dict):
            speaker = speaker.get("display_name", speaker.get("name", "Unknown"))
        text = entry.get("text", "")
        ts = entry.get("start_time", "")
        lines.append(f"[{ts}] {speaker}: {text}")
    return "\n".join(lines)


def format_action_items(items):
    if not items:
        return "(no action items)"
    lines = []
    for i, item in enumerate(items, 1):
        text = item if isinstance(item, str) else item.get("text", item.get("content", str(item)))
        lines.append(f"  {i}. {text}")
    return "\n".join(lines)


def cmd_meetings(args):
    meetings = list_meetings(limit=args.limit)
    if not meetings:
        print("No meetings found.")
        return
    for m in meetings:
        print(format_meeting_short(m))
        print()


def cmd_today(args):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    meetings = list_meetings(limit=20, created_after=today)
    if not meetings:
        print("No meetings today.")
        return
    print(f"=== Today's Meetings ({len(meetings)}) ===\n")
    for m in meetings:
        print(format_meeting_short(m))
        print()


def cmd_transcript(args):
    try:
        data = get_transcript(args.recording_id)
        if isinstance(data, list):
            print(format_transcript(data))
        elif isinstance(data, dict) and "transcript" in data:
            print(format_transcript(data["transcript"]))
        else:
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        # Fallback: get from meeting data
        m = get_meeting_full(args.recording_id)
        if m and m.get("transcript"):
            print(format_transcript(m["transcript"]))
        else:
            print("Could not retrieve transcript.")


def cmd_summary(args):
    try:
        data = get_summary(args.recording_id)
        if isinstance(data, dict):
            if "summary" in data:
                print(data["summary"])
            else:
                print(json.dumps(data, indent=2))
        else:
            print(data)
    except Exception:
        m = get_meeting_full(args.recording_id)
        if m:
            if m.get("default_summary"):
                print(m["default_summary"])
            if m.get("action_items"):
                print("\nAction Items:")
                print(format_action_items(m["action_items"]))
        else:
            print("Could not retrieve summary.")


def cmd_meeting(args):
    m = get_meeting_full(args.recording_id)
    if not m:
        print(f"Meeting {args.recording_id} not found.")
        return
    print(f"Title: {m.get('meeting_title', m.get('title', 'Untitled'))}")
    print(f"Date: {m.get('created_at', '')[:10]}")
    print(f"Recording ID: {m.get('recording_id')}")
    print(f"URL: {m.get('url', '')}")
    print(f"Share URL: {m.get('share_url', '')}")
    invitees = [i.get("name", i.get("email", "")) for i in m.get("calendar_invitees", [])]
    print(f"Participants: {', '.join(invitees)}")
    print()
    if m.get("default_summary"):
        print("=== Summary ===")
        print(m["default_summary"])
        print()
    if m.get("action_items"):
        print("=== Action Items ===")
        print(format_action_items(m["action_items"]))
        print()
    if m.get("transcript"):
        print("=== Transcript ===")
        print(format_transcript(m["transcript"]))


def cmd_search(args):
    query = args.query.lower()
    # Pull recent meetings and filter
    all_meetings = []
    data = api_get("/meetings", {"include_transcript": "false"})
    all_meetings.extend(data.get("items", []))
    cursor = data.get("next_cursor")
    # Get a few more pages
    for _ in range(3):
        if not cursor:
            break
        data = api_get("/meetings", {"include_transcript": "false", "cursor": cursor})
        all_meetings.extend(data.get("items", []))
        cursor = data.get("next_cursor")

    matches = [m for m in all_meetings
               if query in (m.get("meeting_title") or m.get("title", "")).lower()]
    if not matches:
        print(f"No meetings matching '{args.query}'")
        return
    print(f"=== {len(matches)} matches for '{args.query}' ===\n")
    for m in matches:
        print(format_meeting_short(m))
        print()


def main():
    parser = argparse.ArgumentParser(description="Fathom meeting helper")
    sub = parser.add_subparsers(dest="cmd")

    p_meetings = sub.add_parser("meetings", help="List recent meetings")
    p_meetings.add_argument("--limit", type=int, default=10)

    p_today = sub.add_parser("today", help="Today's meetings")

    p_transcript = sub.add_parser("transcript", help="Get transcript")
    p_transcript.add_argument("recording_id")

    p_summary = sub.add_parser("summary", help="Get summary + action items")
    p_summary.add_argument("recording_id")

    p_meeting = sub.add_parser("meeting", help="Full meeting details")
    p_meeting.add_argument("recording_id")

    p_search = sub.add_parser("search", help="Search by title")
    p_search.add_argument("query")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(1)

    if not API_KEY:
        print("FATHOM_API_KEY not set in ~/.openclaw/.env", file=sys.stderr)
        sys.exit(1)

    cmds = {
        "meetings": cmd_meetings,
        "today": cmd_today,
        "transcript": cmd_transcript,
        "summary": cmd_summary,
        "meeting": cmd_meeting,
        "search": cmd_search,
    }
    cmds[args.cmd](args)


if __name__ == "__main__":
    main()
