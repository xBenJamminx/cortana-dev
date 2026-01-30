"""
Browser Automation router - wraps clawdbot browser API
"""
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

CLAWDBOT_BROWSER_URL = os.getenv("CLAWDBOT_BROWSER_URL", "http://127.0.0.1:18791")

async def browser_request(endpoint: str, method: str = "GET", data: dict = None):
    """Make request to clawdbot browser control"""
    url = f"{CLAWDBOT_BROWSER_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            resp = await client.get(url)
        else:
            resp = await client.post(url, json=data or {})
        return resp

@router.get("/status")
async def get_browser_status():
    """Get browser status"""
    try:
        resp = await browser_request("/")
        if resp.status_code == 200:
            return resp.json()
        return {"error": "Browser control unavailable", "status_code": resp.status_code}
    except Exception as e:
        return {"error": str(e), "running": False}

@router.post("/start")
async def start_browser(profile: str = "clawd"):
    """Start the browser"""
    try:
        resp = await browser_request(f"/start?profile={profile}", "POST")
        return resp.json() if resp.status_code == 200 else {"error": resp.text}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/stop")
async def stop_browser():
    """Stop the browser"""
    try:
        resp = await browser_request("/stop", "POST")
        return resp.json() if resp.status_code == 200 else {"error": resp.text}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/tabs")
async def list_tabs():
    """List open browser tabs"""
    try:
        resp = await browser_request("/tabs")
        return resp.json() if resp.status_code == 200 else {"tabs": [], "error": resp.text}
    except Exception as e:
        return {"tabs": [], "error": str(e)}

class NavigateRequest(BaseModel):
    url: str

@router.post("/navigate")
async def navigate(data: NavigateRequest):
    """Navigate to URL"""
    try:
        resp = await browser_request("/navigate", "POST", {"url": data.url})
        return resp.json() if resp.status_code == 200 else {"error": resp.text}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/screenshot")
async def take_screenshot(full_page: bool = False):
    """Take a screenshot"""
    try:
        endpoint = "/screenshot" + ("?fullPage=true" if full_page else "")
        resp = await browser_request(endpoint, "POST")
        return resp.json() if resp.status_code == 200 else {"error": resp.text}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/snapshot")
async def get_snapshot():
    """Get page snapshot (for AI analysis)"""
    try:
        resp = await browser_request("/snapshot")
        return resp.json() if resp.status_code == 200 else {"error": resp.text}
    except Exception as e:
        raise HTTPException(500, str(e))

class ClickRequest(BaseModel):
    ref: str

@router.post("/click")
async def click_element(data: ClickRequest):
    """Click an element by ref"""
    try:
        resp = await browser_request(f"/click?ref={data.ref}", "POST")
        return resp.json() if resp.status_code == 200 else {"error": resp.text}
    except Exception as e:
        raise HTTPException(500, str(e))

class TypeRequest(BaseModel):
    ref: str
    text: str
    submit: bool = False

@router.post("/type")
async def type_text(data: TypeRequest):
    """Type into an element"""
    try:
        params = f"ref={data.ref}&text={data.text}"
        if data.submit:
            params += "&submit=true"
        resp = await browser_request(f"/type?{params}", "POST")
        return resp.json() if resp.status_code == 200 else {"error": resp.text}
    except Exception as e:
        raise HTTPException(500, str(e))

class TweetRequest(BaseModel):
    text: str
    image_path: Optional[str] = None

@router.post("/twitter/post")
async def post_tweet(data: TweetRequest):
    """Post a tweet (via browser automation)"""
    # This would orchestrate: navigate to twitter, compose, post
    # For now, return a placeholder
    return {
        "status": "not_implemented",
        "message": "Use clawdbot browser commands directly for now",
        "suggested": [
            "clawdbot browser open https://twitter.com/compose/tweet",
            f"clawdbot browser type <ref> \"{data.text}\"",
            "clawdbot browser click <post-button-ref>"
        ]
    }
