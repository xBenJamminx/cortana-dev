"""
Push proactivity examples from docs/agent-proactivity-examples.md to Google Sheets
via Composio API.
"""

import json
import subprocess
import sys
import os

MARKDOWN_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "docs",
    "agent-proactivity-examples.md",
)

API_URL = "https://backend.composio.dev/api/v2/actions/GOOGLESHEETS_BATCH_UPDATE/execute"
API_KEY = "ak_UjBg3sflMbHRQgr_qzwr"
CONNECTED_ACCOUNT_ID = "c42f121c-9abe-406e-a4f7-b1dd3a6c1314"
SPREADSHEET_ID = "1TfblNSRCTqkKJFIxPpIlb8b-iE9cSeR16Lu4gMZ0Qio"
SHEET_RANGE = "Proactivity!A1:G68"

HEADERS = ["#", "Action", "Trigger", "Sample Message", "Agent", "Feasibility", "Priority"]


def parse_table(filepath: str) -> list[list[str]]:
    """Parse the main proactivity table from the markdown file."""
    rows = []
    in_table = False

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            # Detect the header row of the main table
            if not in_table:
                if line.startswith("| # |") and "Action" in line and "Trigger" in line:
                    in_table = True
                continue

            # Skip separator rows (|---|---|...)
            if set(line.replace("|", "").replace("-", "").strip()) == set() or \
               all(c in "|- " for c in line):
                continue

            # Stop if we hit an empty line or non-table line
            if not line.startswith("|"):
                break

            # Parse the row: split on | and strip
            cells = line.split("|")
            # First and last elements are empty strings from leading/trailing |
            cells = [c.strip() for c in cells[1:-1]]

            if len(cells) != 7:
                print(f"WARNING: Skipping row with {len(cells)} columns: {line[:80]}")
                continue

            # Strip surrounding quotes from Sample Message (index 3)
            msg = cells[3]
            if msg.startswith('"') and msg.endswith('"'):
                msg = msg[1:-1]
            # Also handle smart quotes
            if msg.startswith('\u201c') and msg.endswith('\u201d'):
                msg = msg[1:-1]
            cells[3] = msg

            rows.append(cells)

    return rows


def push_to_sheets(values: list[list[str]]) -> None:
    """POST the values to Google Sheets via Composio API using curl."""
    body = {
        "connectedAccountId": CONNECTED_ACCOUNT_ID,
        "input": {
            "spreadsheet_id": SPREADSHEET_ID,
            "sheet_name": "Proactivity",
            "range": "A1:G68",
            "values": values,
        },
    }

    body_json = json.dumps(body)

    cmd = [
        "curl",
        "-s",
        "-X", "POST",
        API_URL,
        "-H", "Content-Type: application/json",
        "-H", f"x-api-key: {API_KEY}",
        "-d", body_json,
    ]

    print(f"Sending {len(values)} rows (including header) to Google Sheets...")
    print(f"Range: {SHEET_RANGE}")
    print(f"Spreadsheet: {SPREADSHEET_ID}")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        print(f"ERROR: curl exited with code {result.returncode}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    # Parse and display the response
    try:
        response = json.loads(result.stdout)
        print("Response:")
        print(json.dumps(response, indent=2))
    except json.JSONDecodeError:
        print("Raw response:")
        print(result.stdout)


def main():
    print(f"Reading: {MARKDOWN_PATH}")
    rows = parse_table(MARKDOWN_PATH)
    print(f"Parsed {len(rows)} data rows from markdown table.")

    if not rows:
        print("ERROR: No rows parsed. Check the markdown file.")
        sys.exit(1)

    # Prepend header row
    all_values = [HEADERS] + rows

    print(f"Total rows (with header): {len(all_values)}")
    print()

    # Preview first few rows
    for i, row in enumerate(all_values[:4]):
        print(f"  Row {i}: {row}")
    if len(all_values) > 4:
        print(f"  ... ({len(all_values) - 4} more rows)")
    print()

    push_to_sheets(all_values)


if __name__ == "__main__":
    main()
