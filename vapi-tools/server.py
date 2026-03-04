#!/usr/bin/env python3
"""VAPI Tools Server for Cortana v3.0 — with OpenClaw Bridge"""
import os, json, sqlite3, subprocess, asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
from dotenv import load_dotenv

load_dotenv("/root/.openclaw/.env")
app = FastAPI(title="Cortana VAPI Tools", version="3.0.0")

# ============= CONFIG =============
VAPI_AUTH_SECRET = os.getenv("VAPI_AUTH_SECRET", "")
MEMORY_DB = "/root/.openclaw/memory/main.sqlite"
GOOGLE_CREDS_FILE = "/root/.openclaw/google_credentials.json"
TELEGRAM_BOT_TOKEN = "8553187574:AAFDKi7lik8TXLIbed3rWcPsLry8E4MuJyg"
TELEGRAM_CHAT_ID = "-1003856131939"
WORKSPACE_DIR = "/root/.openclaw/workspace"
VOICE_SESSION_FILE = "/tmp/cortana-voice-session-id.txt"
PUBLIC_PATHS = {"/health", "/health/simple", "/"}

# ============= AUTH MIDDLEWARE =============
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    vapi_secret = request.headers.get("x-vapi-secret", "")
    auth_header = request.headers.get("authorization", "")
    bearer_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    if VAPI_AUTH_SECRET and (vapi_secret == VAPI_AUTH_SECRET or bearer_token == VAPI_AUTH_SECRET):
        return await call_next(request)
    if not VAPI_AUTH_SECRET:
        return await call_next(request)
    return JSONResponse({"error": "Unauthorized"}, status_code=401)

# ============= FAST TOOLS (low latency) =============

def search_web(query: str, max_results: int = 5) -> List[Dict]:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [{"title": r.get("title",""), "body": r.get("body",""), "url": r.get("href","")} for r in results]
    except Exception as e:
        return [{"error": str(e)}]

def get_weather(location: str) -> Dict:
    try:
        r = requests.get(f"https://wttr.in/{location}?format=j1", timeout=10)
        c = r.json().get("current_condition", [{}])[0]
        return {"location": location, "temp_f": c.get("temp_F"), "condition": c.get("weatherDesc",[{}])[0].get("value"), "humidity": c.get("humidity")}
    except Exception as e:
        return {"error": str(e)}

def get_current_datetime() -> Dict:
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/New_York"))
    return {"date": now.strftime("%A, %B %d, %Y"), "time": now.strftime("%I:%M %p"), "timezone": "Eastern"}

def get_memory_db():
    return sqlite3.connect(MEMORY_DB)

def remember_fact(category: str, fact: str) -> Dict:
    try:
        conn = get_memory_db()
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS cortana_notes (key TEXT PRIMARY KEY, content TEXT, created_at TEXT, updated_at TEXT)")
        now = datetime.now().isoformat()
        key = f"fact:{category}"
        cursor.execute("INSERT OR REPLACE INTO cortana_notes VALUES (?, ?, COALESCE((SELECT created_at FROM cortana_notes WHERE key=?), ?), ?)", (key, fact, key, now, now))
        conn.commit()
        conn.close()
        return {"status": "saved", "key": key}
    except Exception as e:
        return {"error": str(e)}

def recall_facts(category: Optional[str] = None) -> List[Dict]:
    try:
        conn = get_memory_db()
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT key, content FROM cortana_notes WHERE key LIKE ? ORDER BY updated_at DESC", (f"fact:{category}%",))
        else:
            cursor.execute("SELECT key, content FROM cortana_notes WHERE key LIKE 'fact:%' ORDER BY updated_at DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        return [{"category": r[0].replace("fact:", ""), "fact": r[1]} for r in rows]
    except Exception as e:
        return [{"error": str(e)}]

# ============= GOOGLE FUNCTIONS =============
def get_google_creds():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GRequest
    with open(GOOGLE_CREDS_FILE) as f:
        d = json.load(f)
    creds = Credentials(token=d.get("token"), refresh_token=d.get("refresh_token"), token_uri=d.get("token_uri"),
                        client_id=d.get("client_id"), client_secret=d.get("client_secret"), scopes=d.get("scopes"))
    if creds.expired and creds.refresh_token:
        creds.refresh(GRequest())
        d["token"] = creds.token
        with open(GOOGLE_CREDS_FILE, "w") as f:
            json.dump(d, f, indent=2)
    return creds

def get_calendar_events(days: int = 7, max_results: int = 10) -> List[Dict]:
    try:
        from googleapiclient.discovery import build
        creds = get_google_creds()
        service = build("calendar", "v3", credentials=creds)
        now = datetime.utcnow().isoformat() + "Z"
        end = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
        result = service.events().list(calendarId="primary", timeMin=now, timeMax=end, maxResults=max_results, singleEvents=True, orderBy="startTime").execute()
        return [{"summary": e.get("summary","No title"), "start": e.get("start",{}).get("dateTime", e.get("start",{}).get("date")),
                 "end": e.get("end",{}).get("dateTime"), "location": e.get("location")} for e in result.get("items", [])]
    except Exception as e:
        return [{"error": str(e)}]

def create_calendar_event(summary: str, start_time: str, end_time: str, description: str = None) -> Dict:
    try:
        from googleapiclient.discovery import build
        creds = get_google_creds()
        service = build("calendar", "v3", credentials=creds)
        event = {"summary": summary, "start": {"dateTime": start_time, "timeZone": "America/New_York"}, "end": {"dateTime": end_time, "timeZone": "America/New_York"}}
        if description: event["description"] = description
        result = service.events().insert(calendarId="primary", body=event).execute()
        return {"status": "created", "id": result.get("id"), "link": result.get("htmlLink")}
    except Exception as e:
        return {"error": str(e)}

def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1!A1:Z100") -> Dict:
    try:
        from googleapiclient.discovery import build
        creds = get_google_creds()
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        return {"values": result.get("values", [])[:20], "range": result.get("range")}
    except Exception as e:
        return {"error": str(e)}

def append_to_sheet(spreadsheet_id: str, range_name: str, values: List[List]) -> Dict:
    try:
        from googleapiclient.discovery import build
        creds = get_google_creds()
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption="USER_ENTERED", body={"values": values}).execute()
        return {"status": "appended", "updates": result.get("updates", {})}
    except Exception as e:
        return {"error": str(e)}

# ============= BRIDGE TOOL: ask_agent =============

def _get_voice_session_id() -> Optional[str]:
    """Read the persistent voice session ID if it exists."""
    try:
        if os.path.exists(VOICE_SESSION_FILE):
            with open(VOICE_SESSION_FILE) as f:
                sid = f.read().strip()
                if sid and len(sid) == 36:  # UUID length
                    return sid
    except:
        pass
    return None

def _save_voice_session_id(sid: str):
    """Save the voice session ID for future resume."""
    try:
        with open(VOICE_SESSION_FILE, "w") as f:
            f.write(sid)
    except:
        pass

async def ask_agent(request_text: str) -> Dict:
    """
    Bridge to the full OpenClaw/Claude Code agent.
    Runs `claude -p` with the request and returns the response.
    This gives voice Cortana access to ALL skills — bash, files, web, memory, etc.
    """
    try:
        # Build command
        cmd = ["claude", "-p", "--output-format", "json", "--max-turns", "3"]

        # Try to resume voice session for continuity
        session_id = _get_voice_session_id()
        if session_id:
            cmd.extend(["--resume", session_id])

        # Prefix the request so the agent knows it's coming from a voice call
        prompt = f"[VOICE CALL] Cortana is on a phone call with Ben. Answer concisely (1-3 sentences, suitable for speaking aloud). Request: {request_text}"

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=WORKSPACE_DIR,
            env={**os.environ, "CLAUDE_CODE_ENTRYPOINT": "vapi-tools"}
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=prompt.encode()),
            timeout=80  # 80s timeout (VAPI tool timeout is ~120s)
        )

        output = stdout.decode().strip()
        if not output:
            return {"error": "Agent returned empty response", "stderr": stderr.decode()[:200]}

        # Parse JSON output - may have multiple lines, take the last valid one
        response_text = ""
        new_session_id = None
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "result":
                    response_text = data.get("result", "")
                    new_session_id = data.get("session_id")
                elif data.get("type") == "assistant":
                    # Streaming message chunks
                    content = data.get("message", {}).get("content", "")
                    if isinstance(content, list):
                        for block in content:
                            if block.get("type") == "text":
                                response_text = block.get("text", "")
                    elif isinstance(content, str):
                        response_text = content
            except json.JSONDecodeError:
                continue

        # Save session ID for continuity
        if new_session_id:
            _save_voice_session_id(new_session_id)

        if response_text:
            return {"response": response_text}
        else:
            return {"response": output[:500]}

    except asyncio.TimeoutError:
        return {"error": "Agent took too long to respond (80s timeout). Try a simpler request."}
    except Exception as e:
        return {"error": f"Agent bridge failed: {str(e)}"}

# ============= TELEGRAM BRIDGE =============

def send_telegram_message(message: str, topic_id: int = 1) -> Dict:
    """Send a message to the Telegram group from Cortana."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "message_thread_id": topic_id,
            "parse_mode": "Markdown"
        }
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        if data.get("ok"):
            return {"status": "sent", "message_id": data["result"]["message_id"]}
        else:
            return {"error": data.get("description", "Unknown error")}
    except Exception as e:
        return {"error": str(e)}

# ============= HEALTH CHECKS =============

def check_gateway_status() -> Dict:
    try:
        result = subprocess.run(["systemctl", "is-active", "openclaw-gateway"], capture_output=True, text=True, timeout=5)
        return {"status": "ok" if result.stdout.strip() == "active" else "down"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_memory_db() -> Dict:
    try:
        conn = get_memory_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cortana_notes")
        count = cursor.fetchone()[0]
        conn.close()
        return {"status": "ok", "notes_count": count}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ============= VAPI ENDPOINT =============
@app.post("/vapi/tools")
async def handle_vapi_tools(request: Request):
    try:
        body = await request.json()
        tool_calls = body.get("message", {}).get("toolCallList", [])
        results = []
        for call in tool_calls:
            tool_id = call.get("id", "")
            tool_name = call.get("name", "")
            args = call.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except:
                    args = {}

            # Fast tools
            if tool_name == "search_web":
                result = search_web(args.get("query", ""), args.get("max_results", 5))
            elif tool_name == "get_weather":
                result = get_weather(args.get("location", "Carle Place NY"))
            elif tool_name == "get_datetime":
                result = get_current_datetime()
            elif tool_name == "remember":
                result = remember_fact(args.get("category", "general"), args.get("fact", ""))
            elif tool_name == "recall":
                result = recall_facts(args.get("category"))
            # Google tools
            elif tool_name == "get_calendar":
                result = get_calendar_events(args.get("days", 7), args.get("max_results", 10))
            elif tool_name == "create_event":
                result = create_calendar_event(args.get("summary", ""), args.get("start_time", ""), args.get("end_time", ""), args.get("description"))
            elif tool_name == "read_sheet":
                result = read_sheet(args.get("spreadsheet_id", ""), args.get("range", "Sheet1!A1:Z100"))
            elif tool_name == "append_sheet":
                result = append_to_sheet(args.get("spreadsheet_id", ""), args.get("range", "Sheet1"), args.get("values", []))
            # Bridge tools
            elif tool_name == "ask_agent":
                result = await ask_agent(args.get("request", ""))
            elif tool_name == "send_telegram":
                result = send_telegram_message(args.get("message", ""), args.get("topic_id", 1))
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            results.append({
                "toolCallId": tool_id,
                "result": json.dumps(result) if isinstance(result, (dict, list)) else str(result)
            })
        return JSONResponse({"results": results})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
async def health():
    checks = {"gateway": check_gateway_status(), "memory_db": check_memory_db()}
    all_ok = all(c.get("status") == "ok" for c in checks.values())
    return {"status": "healthy" if all_ok else "degraded", "version": "3.0.0", "timestamp": datetime.now().isoformat(), "checks": checks}

@app.get("/health/simple")
async def health_simple():
    return {"status": "ok", "version": "3.0.0"}

@app.get("/")
async def root():
    return {"service": "Cortana VAPI Tools", "version": "3.0.0",
            "tools": ["search_web", "get_weather", "get_datetime", "remember", "recall",
                       "get_calendar", "create_event", "read_sheet", "append_sheet",
                       "ask_agent", "send_telegram"]}

# ============= VOICE WEBHOOK PROXY =============
@app.api_route("/voice/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_voice_webhook(path: str, request: Request):
    import httpx
    target = f"http://127.0.0.1:3334/voice/{path}"
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(method=request.method, url=target, content=body, headers=headers, params=dict(request.query_params))
            return JSONResponse(content=resp.json() if resp.headers.get("content-type","").startswith("application/json") else {"raw": resp.text}, status_code=resp.status_code)
    except Exception as e:
        return JSONResponse({"error": f"Voice proxy failed: {str(e)}"}, status_code=502)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8787)
