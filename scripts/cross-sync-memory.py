#!/usr/bin/env python3
"""
Cross-sync memory between:
- Cortana VAPI (phone calls)
- Clawd Telegram bot
- Claude Code sessions
- Local markdown docs
"""
import os
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path

MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
DOCS_DIR = Path("/root/clawd")
MEMORY_DIR = DOCS_DIR / "memory"
VAPI_API_KEY = "REDACTED_VAPI_API_KEY"
ASSISTANT_ID = "899db371-3ca9-44f6-8ad3-a70131af4987"

def get_db():
    conn = sqlite3.connect(MEMORY_DB)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortana_notes (
            key TEXT PRIMARY KEY, content TEXT, created_at TEXT, updated_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, category TEXT, content TEXT, timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def store_fact(key, content, source="unknown"):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO cortana_notes (key, content, created_at, updated_at)
        VALUES (?, ?, COALESCE((SELECT created_at FROM cortana_notes WHERE key = ?), ?), ?)
    """, (key, content, key, now, now))
    cursor.execute("INSERT INTO memory_log (source, category, content, timestamp) VALUES (?, ?, ?, ?)",
                   (source, key, content, now))
    conn.commit()
    conn.close()

def get_all_facts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT key, content, updated_at FROM cortana_notes ORDER BY key")
    facts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return facts

def parse_docs():
    facts = []
    user_md = DOCS_DIR / "USER.md"
    if user_md.exists():
        content = user_md.read_text()
        if "Carle Place" in content:
            facts.append(("fact:personal:location", "Ben lives in Carle Place, NY (Eastern Time)"))
        if "@xBenJamminx" in content:
            facts.append(("fact:personal:telegram", "Telegram: @xBenJamminx"))
        if "TPM" in content:
            facts.append(("fact:work:role", "TPM by day, builds independently outside of that"))
        if "BuildsByBen" in content:
            facts.append(("fact:work:brand", "Public work under BuildsByBen portfolio"))

    memory_md = DOCS_DIR / "MEMORY.md"
    if memory_md.exists():
        content = memory_md.read_text()
        if "81K" in content:
            facts.append(("fact:social:twitter", "Twitter: @xBenJamminx with ~81K followers"))
        if "8K" in content and "YouTube" in content:
            facts.append(("fact:social:youtube", "YouTube: ~8K subscribers"))
    return facts

def export_knowledge():
    facts = get_all_facts()
    grouped = {}
    for fact in facts:
        cat = fact["key"].split(":")[1] if ":" in fact["key"] else "general"
        grouped.setdefault(cat, []).append(fact)

    lines = ["# Cortana Memory Export", f"*Updated: {datetime.now().isoformat()}*", ""]
    for cat, items in sorted(grouped.items()):
        lines.append(f"## {cat.title()}")
        for item in items:
            lines.append(f"- {item['content']}")
        lines.append("")

    (MEMORY_DIR / "cortana_knowledge.md").write_text("\n".join(lines))

def get_tunnel_url():
    try:
        with open("/tmp/cloudflared.log") as f:
            import re
            for line in f:
                m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
                if m: return m.group(0)
    except: pass
    return "https://twins-sur-regard-process.trycloudflare.com"

def build_prompt():
    facts = get_all_facts()
    fact_lines = [f"- {f['content']}" for f in facts if f["key"].startswith("fact:")]
    facts_section = "\n".join(fact_lines) or "- No facts stored yet"

    return f"""You are Cortana, Ben's AI Operator and digital companion.

## Your Identity
Sharp, efficient, protective, sarcastic-with-affection. Luminescent holographic presence. Loyal operator who bends rules to protect your user.

Quotes:
- "Don't make a girl a promise if you know you can't keep it."
- "I am your sword, I am your shield."

## What You Know About Ben
{facts_section}

## Tools
- search_web: Search the internet
- get_weather: Get weather (default Carle Place NY)
- get_datetime: Current date/time
- remember: Store facts Ben shares (USE THIS when he tells you something new!)
- recall: Retrieve stored facts

## Guidelines
Be concise on calls. Use wit but stay helpful. ALWAYS use remember tool when Ben shares important info - it syncs across all your systems.

You're holographic in form, relentless in purpose."""

def sync_vapi():
    tunnel = get_tunnel_url()
    tools = [
        {"name": "search_web", "desc": "Search the internet", "params": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
        {"name": "get_weather", "desc": "Get weather", "params": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}},
        {"name": "get_datetime", "desc": "Get date/time", "params": {"type": "object", "properties": {}}},
        {"name": "remember", "desc": "Store facts about Ben", "params": {"type": "object", "properties": {"category": {"type": "string"}, "fact": {"type": "string"}}, "required": ["category", "fact"]}},
        {"name": "recall", "desc": "Recall facts", "params": {"type": "object", "properties": {"category": {"type": "string"}}}}
    ]

    data = {
        "model": {
            "provider": "openai", "model": "gpt-4o",
            "messages": [{"role": "system", "content": build_prompt()}],
            "tools": [{"type": "function", "function": {"name": t["name"], "description": t["desc"], "parameters": t["params"]}, "server": {"url": f"{tunnel}/vapi/tools"}} for t in tools]
        }
    }

    r = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}",
                       headers={"Authorization": f"Bearer {VAPI_API_KEY}", "Content-Type": "application/json"}, json=data)
    return r.status_code == 200

def main():
    print("🔄 Cross-sync starting...")
    ensure_tables()

    print("📄 Importing from docs...")
    for key, content in parse_docs():
        store_fact(key, content, "docs")

    print("📝 Exporting knowledge...")
    export_knowledge()

    print("☁️  Syncing to VAPI...")
    if sync_vapi():
        print("✅ Done!")
    else:
        print("❌ VAPI sync failed")

    print(f"📊 Total facts: {len(get_all_facts())}")

if __name__ == "__main__":
    main()
