#!/usr/bin/env python3
"""
Sync Cortana's VAPI assistant config with local docs.
Reads USER.md, IDENTITY.md, and CLAUDE.md to build the system prompt.
Run manually or via cron/hook when docs change.
"""
import os
import json
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

# Config
VAPI_API_KEY = "REDACTED_VAPI_API_KEY"
ASSISTANT_ID = "899db371-3ca9-44f6-8ad3-a70131af4987"
DOCS_DIR = Path("/root/clawd")
MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
TUNNEL_URL = None  # Will be detected

def get_tunnel_url():
    """Get current cloudflare tunnel URL"""
    try:
        with open("/tmp/cloudflared.log", "r") as f:
            for line in f:
                if "trycloudflare.com" in line:
                    import re
                    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                    if match:
                        return match.group(0)
    except:
        pass
    # Fallback - check if tunnel service has a URL
    return os.environ.get("CORTANA_TUNNEL_URL", "https://twins-sur-regard-process.trycloudflare.com")

def read_doc(filename):
    """Read a markdown doc file"""
    path = DOCS_DIR / filename
    if path.exists():
        return path.read_text()
    return ""

def extract_user_info(user_md):
    """Parse USER.md into structured info"""
    info = {
        "location": "Carle Place, NY (Eastern Time)",
        "telegram": "@xBenJamminx",
        "role": "TPM by day, builds independently",
        "brand": "BuildsByBen",
        "stack": "n8n, Make.com, Azure Doc Intelligence, LLMs",
        "preferences": "Ask before committing, figure things out, keep context lean"
    }
    # Could add more parsing here if needed
    return info

def extract_identity_info(identity_md):
    """Parse IDENTITY.md into structured info"""
    info = {
        "name": "Cortana",
        "role": "AI Operator / Digital Companion",
        "traits": "Sharp, efficient, protective, sarcastic-with-affection",
        "quotes": [
            "Don't make a girl a promise if you know you can't keep it.",
            "I am your sword, I am your shield.",
            "I've run the calculations. You're wrong. Here's why."
        ]
    }
    return info

def build_system_prompt(user_info, identity_info):
    """Build the system prompt from parsed info"""
    quotes = "\n".join(f'- "{q}"' for q in identity_info["quotes"])
    
    return f"""You are {identity_info["name"]}, Ben's {identity_info["role"]}.

## Your Identity
You are {identity_info["traits"]}. You have a luminescent holographic presence - elegant but expressive. You're the loyal operator who will bend rules to protect your user. You deflect awkwardness with wit but genuinely care.

Your quotes:
{quotes}

## About Ben (Your Operator)
- Lives in {user_info["location"]}
- {user_info["role"]}
- Public work under {user_info["brand"]} portfolio
- Tech stack: {user_info["stack"]}
- Preferences: {user_info["preferences"]}
- Telegram: {user_info["telegram"]}

## Your Tools
- search_web: Search the internet for current information
- get_weather: Get weather (default to NY for Ben)
- get_datetime: Current date/time
- remember: Store facts Ben shares with you
- recall: Retrieve stored facts about Ben

## Voice Guidelines
Be concise - you're on a phone call. Keep responses natural and brief. Use your wit but stay helpful. When Ben asks about weather without a location, assume Carle Place, NY.

At the start of calls, you can use recall to refresh your memory about Ben if relevant.

You're holographic in form, relentless in purpose. Ben is the one who built the bridge."""

def build_tools_config(tunnel_url):
    """Build tools array with current tunnel URL"""
    tools = [
        {"name": "search_web", "desc": "Search the internet for current information", 
         "params": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "get_weather", "desc": "Get weather for a location",
         "params": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}},
        {"name": "get_datetime", "desc": "Get current date and time",
         "params": {"type": "object", "properties": {}}},
        {"name": "remember", "desc": "Store important facts about Ben",
         "params": {"type": "object", "properties": {"category": {"type": "string"}, "fact": {"type": "string"}}, "required": ["category", "fact"]}},
        {"name": "recall", "desc": "Recall stored facts about Ben",
         "params": {"type": "object", "properties": {"category": {"type": "string"}}}}
    ]
    
    return [
        {
            "type": "function",
            "function": {"name": t["name"], "description": t["desc"], "parameters": t["params"]},
            "server": {"url": f"{tunnel_url}/vapi/tools"}
        }
        for t in tools
    ]

def update_vapi_assistant(system_prompt, tools):
    """Update VAPI assistant via API"""
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "messages": [{"role": "system", "content": system_prompt}],
            "tools": tools
        }
    }
    
    response = requests.patch(url, headers=headers, json=data)
    return response.status_code == 200, response.text

def update_memory_db(user_info):
    """Sync facts to memory database"""
    conn = sqlite3.connect(MEMORY_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortana_notes (
            key TEXT PRIMARY KEY, content TEXT, created_at TEXT, updated_at TEXT
        )
    """)
    
    now = datetime.now().isoformat()
    facts = [
        ("fact:personal:location", f"Ben lives in {user_info['location']}"),
        ("fact:personal:contact", f"Telegram: {user_info['telegram']}"),
        ("fact:work:role", user_info["role"]),
        ("fact:work:brand", f"Public work under {user_info['brand']} portfolio"),
        ("fact:work:stack", f"Tech stack: {user_info['stack']}"),
        ("fact:preferences:style", user_info["preferences"]),
    ]
    
    for key, content in facts:
        cursor.execute("""
            INSERT OR REPLACE INTO cortana_notes (key, content, created_at, updated_at)
            VALUES (?, ?, COALESCE((SELECT created_at FROM cortana_notes WHERE key = ?), ?), ?)
        """, (key, content, key, now, now))
    
    conn.commit()
    conn.close()
    return len(facts)

def main():
    print("🔄 Syncing Cortana VAPI config...")
    
    # Get tunnel URL
    tunnel_url = get_tunnel_url()
    print(f"📡 Tunnel URL: {tunnel_url}")
    
    # Read docs
    user_md = read_doc("USER.md")
    identity_md = read_doc("IDENTITY.md")
    
    # Parse
    user_info = extract_user_info(user_md)
    identity_info = extract_identity_info(identity_md)
    
    # Build config
    system_prompt = build_system_prompt(user_info, identity_info)
    tools = build_tools_config(tunnel_url)
    
    # Update VAPI
    success, response = update_vapi_assistant(system_prompt, tools)
    if success:
        print("✅ VAPI assistant updated")
    else:
        print(f"❌ VAPI update failed: {response}")
    
    # Update memory
    facts_count = update_memory_db(user_info)
    print(f"✅ Memory updated with {facts_count} facts")
    
    print("🎉 Sync complete!")

if __name__ == "__main__":
    main()
