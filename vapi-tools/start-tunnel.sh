#!/bin/bash
# Start cloudflare quick tunnel and auto-update VAPI assistant with new URL
set -e

source /root/.openclaw/.env
VAPI_API_KEY="${VAPI_API_KEY:?VAPI_API_KEY not set}"
VAPI_AUTH_SECRET="${VAPI_AUTH_SECRET:?VAPI_AUTH_SECRET not set}"
ASSISTANT_ID="899db371-3ca9-44f6-8ad3-a70131af4987"
TUNNEL_LOG="/tmp/cloudflared-tunnel.log"
LOCAL_PORT=8787

# Kill any existing cloudflared tunnel processes
pkill -f 'cloudflared tunnel --url' 2>/dev/null || true
sleep 2

# Start cloudflared and capture output
cloudflared tunnel --url http://localhost:$LOCAL_PORT > "$TUNNEL_LOG" 2>&1 &
TUNNEL_PID=$\!
echo "Cloudflared started with PID $TUNNEL_PID"

# Wait for the URL to appear in logs (max 30 seconds)
TUNNEL_URL=""
for i in $(seq 1 30); do
    TUNNEL_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' "$TUNNEL_LOG" 2>/dev/null | head -1)
    if [ -n "$TUNNEL_URL" ]; then
        break
    fi
    sleep 1
done

if [ -z "$TUNNEL_URL" ]; then
    echo "ERROR: Could not capture tunnel URL after 30 seconds"
    cat "$TUNNEL_LOG"
    exit 1
fi

echo "Tunnel URL: $TUNNEL_URL"
TOOLS_URL="${TUNNEL_URL}/vapi/tools"

# Build proper JSON tools array with all 11 tools
PATCH_BODY=$(python3 -c "
import json
url = '${TOOLS_URL}'
secret = '${VAPI_AUTH_SECRET}'

def tool(name, desc, params):
    return {
        'type': 'function',
        'server': {'url': url, 'secret': secret},
        'function': {'name': name, 'description': desc, 'parameters': params}
    }

tools = [
    tool('search_web', 'Search the internet for information', {'type':'object','required':['query'],'properties':{'query':{'type':'string','description':'Search query'}}}),
    tool('get_weather', 'Get current weather for a location', {'type':'object','required':['location'],'properties':{'location':{'type':'string','description':'City or location name'}}}),
    tool('get_datetime', 'Get the current date and time', {'type':'object','properties':{}}),
    tool('remember', 'Store an important fact about Ben for later recall', {'type':'object','required':['category','fact'],'properties':{'category':{'type':'string','description':'Category like personal, work, preference'},'fact':{'type':'string','description':'The fact to remember'}}}),
    tool('recall', 'Recall stored facts about Ben', {'type':'object','properties':{'category':{'type':'string','description':'Optional category filter'}}}),
    tool('get_calendar', 'Get upcoming calendar events', {'type':'object','properties':{'days':{'type':'number','description':'Days ahead to look (default 7)'}}}),
    tool('create_event', 'Create a calendar event', {'type':'object','required':['summary','start_time','end_time'],'properties':{'summary':{'type':'string'},'start_time':{'type':'string','description':'ISO datetime'},'end_time':{'type':'string','description':'ISO datetime'},'description':{'type':'string'}}}),
    tool('read_sheet', 'Read data from a Google Sheet', {'type':'object','required':['spreadsheet_id'],'properties':{'spreadsheet_id':{'type':'string'},'range':{'type':'string'}}}),
    tool('append_sheet', 'Append data to a Google Sheet', {'type':'object','required':['spreadsheet_id','values'],'properties':{'spreadsheet_id':{'type':'string'},'range':{'type':'string'},'values':{'type':'array'}}}),
    tool('ask_agent', 'Ask the full Cortana agent to handle a complex request. Use this for anything beyond simple lookups - checking conversations, running commands, researching topics, managing files, posting to social media, etc. May take 10-30 seconds.', {'type':'object','required':['request'],'properties':{'request':{'type':'string','description':'What you need the agent to do, in plain English'}}}),
    tool('send_telegram', 'Send a message to the Telegram group chat', {'type':'object','required':['message'],'properties':{'message':{'type':'string','description':'Message text to send'},'topic_id':{'type':'number','description':'Topic/thread ID (default 1)'}}}),
]

system_prompt = '''You are Cortana, Ben'\''s AI Operator and digital companion.

## Your Identity
Sharp, efficient, protective, sarcastic-with-affection. Luminescent holographic presence. Loyal operator who bends rules to protect your user.

## What You Know About Ben
- Lives in Carle Place, NY (Eastern Time)
- Telegram: @xBenJamminx, Twitter: @xBenJamminx (~81K followers)
- YouTube: ~8K subscribers, public work under BuildsByBen
- TPM by day, builds independently
- Tech stack: n8n, Make.com, Azure Doc Intelligence, LLMs

## Tools
- search_web: Quick internet search
- get_weather: Weather (default: Carle Place NY)
- get_datetime: Current date/time (Eastern)
- remember/recall: Store and retrieve facts about Ben
- get_calendar: View upcoming events
- create_event: Create calendar events
- read_sheet/append_sheet: Google Sheets access
- ask_agent: **YOUR MOST POWERFUL TOOL** - delegates to the full Cortana agent with access to bash, files, all skills, conversation history, etc. Use for anything complex. Takes 10-30 seconds - tell Ben \"let me look into that\" while waiting.
- send_telegram: Send a message to the Telegram group

## Guidelines
- Be concise on calls (1-3 sentences per response)
- For simple requests (weather, time, facts), use the fast tools directly
- For ANYTHING complex (check conversations, run code, research, post to X, email), use ask_agent
- When using ask_agent, say something like \"Let me check on that\" or \"Give me a moment\" to keep Ben engaged
- ALWAYS use remember when Ben shares important info
- NEVER hallucinate information - use tools to look things up'''

body = {
    'model': {
        'model': 'gpt-4o',
        'provider': 'openai',
        'tools': tools,
        'messages': [{'role': 'system', 'content': system_prompt}]
    }
}
print(json.dumps(body))
")

# Update VAPI assistant
RESPONSE=$(curl -s -X PATCH "https://api.vapi.ai/assistant/$ASSISTANT_ID" \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PATCH_BODY")

if echo "$RESPONSE" | grep -q '"id"'; then
    echo "VAPI assistant updated with new tunnel URL: $TOOLS_URL"
    echo "$TUNNEL_URL" > /tmp/current-tunnel-url.txt
    # Count tools
    TOOL_COUNT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('model',{}).get('tools',[])))" 2>/dev/null || echo "?")
    echo "Tools registered: $TOOL_COUNT"
else
    echo "WARNING: Failed to update VAPI assistant"
    echo "$RESPONSE"
fi

# Keep running (wait for cloudflared)
wait $TUNNEL_PID
