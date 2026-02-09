#!/bin/bash
# Start cloudflare quick tunnel and auto-update VAPI assistant with new URL
# This script captures the ephemeral tunnel URL and patches the VAPI assistant config

set -e

source /root/.openclaw/.env
VAPI_API_KEY="${VAPI_API_KEY:?VAPI_API_KEY not set}"
ASSISTANT_ID="899db371-3ca9-44f6-8ad3-a70131af4987"
TUNNEL_LOG="/tmp/cloudflared-tunnel.log"
LOCAL_PORT=8787

# Kill any existing cloudflared tunnel processes
pkill -f 'cloudflared tunnel --url' 2>/dev/null || true
sleep 2

# Start cloudflared and capture output
cloudflared tunnel --url http://localhost:$LOCAL_PORT > "$TUNNEL_LOG" 2>&1 &
TUNNEL_PID=$!
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
    echo "Log contents:"
    cat "$TUNNEL_LOG"
    exit 1
fi

echo "Tunnel URL: $TUNNEL_URL"
TOOLS_URL="${TUNNEL_URL}/vapi/tools"

# Build the tools array with the new URL
TOOLS_JSON=$(cat <<'TOOLS'
[
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:search_web,parameters:{type:object,required:[query],properties:{query:{type:string}}},description:Search the internet}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:get_weather,parameters:{type:object,required:[location],properties:{location:{type:string}}},description:Get weather}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:get_datetime,parameters:{type:object,properties:{}},description:Get date/time}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:remember,parameters:{type:object,required:[category,fact],properties:{fact:{type:string},category:{type:string}}},description:Store facts about Ben}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:recall,parameters:{type:object,properties:{category:{type:string}}},description:Recall facts}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:get_calendar,parameters:{type:object,properties:{days:{type:number},max_results:{type:number}}},description:Get calendar events}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:create_event,parameters:{type:object,required:[summary,start_time,end_time],properties:{summary:{type:string},start_time:{type:string},end_time:{type:string},description:{type:string}}},description:Create calendar event}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:read_sheet,parameters:{type:object,required:[spreadsheet_id],properties:{spreadsheet_id:{type:string},range:{type:string}}},description:Read Google Sheet}},
  {type:function,server:{url:__URL__,secret:__SECRET__},function:{name:append_sheet,parameters:{type:object,required:[spreadsheet_id,values],properties:{spreadsheet_id:{type:string},range:{type:string},values:{type:array}}},description:Append to Google Sheet}}
]
TOOLS
)

# Replace placeholders with actual values
TOOLS_JSON=$(echo "$TOOLS_JSON" | sed "s|__URL__|$TOOLS_URL|g")
TOOLS_JSON=$(echo "$TOOLS_JSON" | sed "s|__SECRET__|${VAPI_AUTH_SECRET}|g")

# Update VAPI assistant with new tool URLs
RESPONSE=$(curl -s -X PATCH "https://api.vapi.ai/assistant/$ASSISTANT_ID"   -H "Authorization: Bearer $VAPI_API_KEY"   -H "Content-Type: application/json"   -d "{\"model\": {\"tools\": $TOOLS_JSON}}")

if echo "$RESPONSE" | grep -q '"id"'; then
    echo "VAPI assistant updated with new tunnel URL: $TOOLS_URL"
    echo "$TUNNEL_URL" > /tmp/current-tunnel-url.txt
else
    echo "WARNING: Failed to update VAPI assistant"
    echo "$RESPONSE"
fi

# Keep running (wait for cloudflared)
wait $TUNNEL_PID
