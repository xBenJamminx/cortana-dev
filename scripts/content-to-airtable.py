#!/usr/bin/env python3
"""
Content-to-Airtable Tool - Enforces content workflow
Replaces file-based content saving with Airtable integration
"""
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Config
AIRTABLE_BASE_ID = "appgqpqWgN7BcvKQ1"  # Content OS base
AIRTABLE_TABLE = "Content Ideas"
COMPOSIO_SCRIPT = "/root/clawd/skills/composio/composio-tool.py"
LOG_FILE = Path("/var/log/clawd/content-workflow.log")

def log(msg):
    """Log to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, file=sys.stderr)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def composio_create_record(title, content, status="Draft", content_type="Article"):
    """Create Airtable record via Composio"""
    try:
        cmd = [
            COMPOSIO_SCRIPT,
            "--action", "AIRTABLE_CREATE_RECORD",
            "--params", json.dumps({
                "baseId": AIRTABLE_BASE_ID,
                "tableIdOrName": AIRTABLE_TABLE,
                "fields": {
                    "Title": title,
                    "Content": content,
                    "Status": status,
                    "Type": content_type,
                    "Created": datetime.now().isoformat()
                }
            })
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            # Parse JSON response from stdout
            for line in result.stdout.strip().split("\n"):
                try:
                    data = json.loads(line)
                    if data.get("success"):
                        return data.get("data", {}).get("id")
                except:
                    pass

        log(f"Composio error: {result.stderr}")
        return None

    except Exception as e:
        log(f"Failed to create Airtable record: {e}")
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: content-to-airtable.py <title> <content> [status] [type]")
        print("\nThis tool REPLACES file-based content saving.")
        print("Content ALWAYS goes to Airtable content pipeline.")
        sys.exit(1)

    title = sys.argv[1]
    content = sys.argv[2]
    status = sys.argv[3] if len(sys.argv) > 3 else "Draft"
    content_type = sys.argv[4] if len(sys.argv) > 4 else "Article"

    log(f"Creating content: {title} [{status}]")

    record_id = composio_create_record(title, content, status, content_type)

    if record_id:
        print(json.dumps({
            "success": True,
            "record_id": record_id,
            "message": f"✅ Content saved to Airtable: {title}",
            "url": f"https://airtable.com/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE}/{record_id}"
        }))
        log(f"✅ Created record: {record_id}")
    else:
        print(json.dumps({
            "success": False,
            "error": "Failed to create Airtable record",
            "message": "❌ Content NOT saved - Airtable creation failed"
        }))
        log("❌ Failed to create record")
        sys.exit(1)

if __name__ == "__main__":
    main()
