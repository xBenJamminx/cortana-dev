"""
Workspace OS - Comprehensive API Server
"""
import os
import asyncio
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx

# Local imports
import sys
sys.path.insert(0, os.path.dirname(__file__))
from database import (
    get_db, init_db, SessionLocal,
    Project, ProjectTask, FileIndex, AICall, Activity, Memory,
    ContentItem, Idea, TargetAccount, PerformanceLog,
    ContentTemplate, VoiceGuideline, WeeklyGoal, Setting, IntegrationStatus
)
from services.websocket_manager import WebSocketManager
from services.airtable_sync import sync_all, create_content_item, update_content_item

# Import routers
from routers import dashboard, files, projects, ai, memory, settings, system, workspace, integrations, documents, google_services, bookmarks

ws_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    print("Database initialized")

    # Initial Airtable sync
    try:
        db = SessionLocal()
        results = await sync_all(db)
        print(f"Airtable sync complete: {results}")
        db.close()
    except Exception as e:
        print(f"Airtable sync failed: {e}")

    # Index files on startup
    try:
        from routers.files import reindex_files
        db = SessionLocal()
        await reindex_files(db)
        db.close()
        print("File index complete")
    except Exception as e:
        print(f"File indexing failed: {e}")

    yield

    # Shutdown
    print("Shutting down...")

app = FastAPI(title="Workspace OS", lifespan=lifespan)

# Include routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(google_services.router, prefix="/api/google", tags=["google"])
app.include_router(bookmarks.router, prefix="/api/bookmarks", tags=["bookmarks"])

# ============ CONTENT ROUTES (Airtable-synced) ============

@app.get("/api/content/")
async def list_content(
    status: str = None,
    account: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List content items with optional filtering"""
    query = db.query(ContentItem)
    if status:
        query = query.filter(ContentItem.status == status)
    if account:
        query = query.filter(ContentItem.account == account)
    items = query.order_by(ContentItem.updated_at.desc()).limit(limit).all()
    return [{
        "id": i.id,
        "airtable_id": i.airtable_id,
        "title": i.title,
        "content": i.content,
        "status": i.status,
        "content_type": i.content_type,
        "account": i.account,
        "scheduled": i.scheduled.isoformat() if i.scheduled else None,
        "posted_url": i.posted_url,
        "notes": i.notes,
        "updated_at": i.updated_at.isoformat()
    } for i in items]

@app.get("/api/content/kanban")
async def get_content_kanban(db: Session = Depends(get_db)):
    """Get content items grouped by status for Kanban view"""
    items = db.query(ContentItem).order_by(ContentItem.updated_at.desc()).all()
    kanban = {
        "idea": [],
        "draft": [],
        "review": [],
        "approved": [],
        "posted": [],
        "rejected": []
    }
    for item in items:
        status = item.status or "idea"
        if status in kanban:
            char_count = len(item.content) if item.content else 0
            kanban[status].append({
                "id": item.id,
                "airtable_id": item.airtable_id,
                "title": item.title,
                "content": item.content,
                "content_preview": item.content[:150] + "..." if item.content and len(item.content) > 150 else item.content,
                "content_type": item.content_type,
                "account": item.account,
                "scheduled": item.scheduled.isoformat() if item.scheduled else None,
                "posted_url": item.posted_url,
                "notes": item.notes,
                "char_count": char_count,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            })
    return kanban

@app.post("/api/content/")
async def create_content(
    title: str,
    content: str = None,
    status: str = "idea",
    content_type: str = None,
    account: str = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Create new content item (syncs to Airtable)"""
    data = {
        "title": title,
        "content": content,
        "status": status,
        "content_type": content_type,
        "account": account,
        "notes": notes
    }

    # Create in Airtable
    result = await create_content_item(data)
    if result:
        airtable_id = result["id"]
    else:
        airtable_id = None

    # Create locally
    item = ContentItem(
        airtable_id=airtable_id,
        title=title,
        content=content,
        status=status,
        content_type=content_type,
        account=account,
        notes=notes
    )
    db.add(item)
    db.commit()

    # Log activity
    activity = Activity(
        event_type="content_created",
        category="content",
        title=f"Created: {title}",
        icon="📝",
        color="blue"
    )
    db.add(activity)
    db.commit()

    await ws_manager.broadcast({"type": "content_update", "action": "created", "id": item.id})
    return {"id": item.id, "airtable_id": airtable_id}

from pydantic import BaseModel
from typing import Optional

class ContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    posted_url: Optional[str] = None

@app.patch("/api/content/{item_id}")
async def update_content(
    item_id: int,
    updates: ContentUpdate,
    db: Session = Depends(get_db)
):
    title = updates.title
    content = updates.content
    status = updates.status
    notes = updates.notes
    posted_url = updates.posted_url
    """Update content item (syncs to Airtable)"""
    item = db.query(ContentItem).filter(ContentItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Content item not found")

    update_data = {}
    if title is not None:
        item.title = title
        update_data["title"] = title
    if content is not None:
        item.content = content
        update_data["content"] = content
    if status is not None:
        old_status = item.status
        item.status = status
        update_data["status"] = status
    if notes is not None:
        item.notes = notes
        update_data["notes"] = notes
    if posted_url is not None:
        item.posted_url = posted_url
        update_data["posted_url"] = posted_url

    item.updated_at = datetime.utcnow()
    db.commit()

    # Sync to Airtable
    if item.airtable_id and update_data:
        await update_content_item(item.airtable_id, update_data)

    # Log activity
    activity = Activity(
        event_type="content_updated",
        category="content",
        title=f"Updated: {item.title}",
        description=f"Status: {status}" if status else None,
        icon="✏️",
        color="yellow"
    )
    db.add(activity)
    db.commit()

    await ws_manager.broadcast({"type": "content_update", "action": "updated", "id": item.id})
    return {"success": True}

# ============ IDEAS ROUTES ============

@app.get("/api/ideas/")
async def list_ideas(
    priority: str = None,
    used: bool = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List ideas from inbox"""
    query = db.query(Idea)
    if priority:
        query = query.filter(Idea.priority == priority)
    if used is not None:
        query = query.filter(Idea.used == used)
    ideas = query.order_by(Idea.created_at.desc()).limit(limit).all()
    return [{
        "id": i.id,
        "idea": i.idea,
        "source": i.source,
        "priority": i.priority,
        "used": i.used,
        "source_url": i.source_url,
        "notes": i.notes
    } for i in ideas]

# ============ TARGETS ROUTES ============

@app.get("/api/targets/")
async def list_targets(
    category: str = None,
    priority: str = None,
    db: Session = Depends(get_db)
):
    """List target accounts"""
    query = db.query(TargetAccount)
    if category:
        query = query.filter(TargetAccount.category == category)
    if priority:
        query = query.filter(TargetAccount.engage_priority == priority)
    targets = query.order_by(TargetAccount.followers.desc()).all()
    return [{
        "id": t.id,
        "handle": t.handle,
        "name": t.name,
        "category": t.category,
        "followers": t.followers,
        "engage_priority": t.engage_priority,
        "last_engaged": t.last_engaged.isoformat() if t.last_engaged else None,
        "profile_url": t.profile_url
    } for t in targets]

# ============ PERFORMANCE ROUTES ============

@app.get("/api/performance/")
async def list_performance(
    platform: str = None,
    grade: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List performance logs"""
    query = db.query(PerformanceLog)
    if platform:
        query = query.filter(PerformanceLog.platform == platform)
    if grade:
        query = query.filter(PerformanceLog.grade == grade)
    logs = query.order_by(PerformanceLog.posted_date.desc()).limit(limit).all()
    return [{
        "id": p.id,
        "post_title": p.post_title,
        "platform": p.platform,
        "account": p.account,
        "posted_date": p.posted_date.isoformat() if p.posted_date else None,
        "impressions": p.impressions,
        "engagements": p.engagements,
        "followers_gained": p.followers_gained,
        "post_url": p.post_url,
        "grade": p.grade
    } for p in logs]

@app.get("/api/performance/stats")
async def get_performance_stats(days: int = 30, db: Session = Depends(get_db)):
    """Get aggregated performance stats"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    logs = db.query(PerformanceLog).filter(PerformanceLog.posted_date >= cutoff).all()

    total_impressions = sum(p.impressions or 0 for p in logs)
    total_engagements = sum(p.engagements or 0 for p in logs)
    total_followers = sum(p.followers_gained or 0 for p in logs)

    grade_counts = {}
    for log in logs:
        grade = log.grade or "unknown"
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    return {
        "period_days": days,
        "total_posts": len(logs),
        "total_impressions": total_impressions,
        "total_engagements": total_engagements,
        "total_followers_gained": total_followers,
        "avg_engagement_rate": round(total_engagements / total_impressions * 100, 2) if total_impressions > 0 else 0,
        "grade_breakdown": grade_counts
    }

# ============ TEMPLATES ROUTES ============

@app.get("/api/templates/")
async def list_templates(db: Session = Depends(get_db)):
    """List content templates"""
    templates = db.query(ContentTemplate).order_by(ContentTemplate.times_used.desc()).all()
    return [{
        "id": t.id,
        "name": t.name,
        "format_type": t.format_type,
        "structure": t.structure,
        "example": t.example,
        "best_for": t.best_for,
        "times_used": t.times_used,
        "avg_performance": t.avg_performance
    } for t in templates]

# ============ VOICE ROUTES ============

@app.get("/api/voice/")
async def list_voice_guidelines(db: Session = Depends(get_db)):
    """List voice guidelines"""
    guidelines = db.query(VoiceGuideline).all()
    return [{
        "id": v.id,
        "account_name": v.account_name,
        "tone": v.tone,
        "do_list": v.do_list,
        "dont_list": v.dont_list,
        "example_good": v.example_good,
        "example_bad": v.example_bad,
        "topics": v.topics,
        "emoji_style": v.emoji_style
    } for v in guidelines]

# ============ GOALS ROUTES ============

@app.get("/api/goals/")
async def list_goals(limit: int = 10, db: Session = Depends(get_db)):
    """List weekly goals"""
    goals = db.query(WeeklyGoal).order_by(WeeklyGoal.week_of.desc()).limit(limit).all()
    return [{
        "id": g.id,
        "week_of": g.week_of.isoformat() if g.week_of else None,
        "tweets_goal": g.tweets_goal,
        "tweets_actual": g.tweets_actual,
        "replies_goal": g.replies_goal,
        "replies_actual": g.replies_actual,
        "followers_start": g.followers_start,
        "followers_end": g.followers_end,
        "followers_gained": (g.followers_end or 0) - (g.followers_start or 0),
        "top_post_url": g.top_post_url,
        "learnings": g.learnings
    } for g in goals]

# ============ SYNC ROUTES ============

@app.post("/api/sync/airtable")
async def trigger_airtable_sync(db: Session = Depends(get_db)):
    """Manually trigger Airtable sync"""
    try:
        results = await sync_all(db)
        activity = Activity(
            event_type="sync_complete",
            category="system",
            title="Airtable sync completed",
            description=str(results),
            icon="🔄",
            color="green"
        )
        db.add(activity)
        db.commit()
        await ws_manager.broadcast({"type": "sync_complete", "results": results})
        return {"success": True, "synced": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============ INTEGRATIONS STATUS ============

@app.get("/api/integrations/")
async def get_integration_status(db: Session = Depends(get_db)):
    """Get status of all integrations"""
    statuses = {}

    # Check Airtable
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.airtable.com/v0/meta/whoami",
                headers={"Authorization": f"Bearer {os.getenv('AIRTABLE_API_KEY')}"}
            )
            statuses["airtable"] = {
                "status": "connected" if resp.status_code == 200 else "error",
                "last_check": datetime.utcnow().isoformat()
            }
    except:
        statuses["airtable"] = {"status": "disconnected"}

    # Check Gateway
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{os.getenv('CLAWDBOT_GATEWAY_URL', 'http://127.0.0.1:18789')}/health")
            statuses["gateway"] = {
                "status": "connected" if resp.status_code == 200 else "error",
                "last_check": datetime.utcnow().isoformat()
            }
    except:
        statuses["gateway"] = {"status": "disconnected"}

    # Check Browser Relay
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{os.getenv('CLAWDBOT_BROWSER_URL', 'http://127.0.0.1:18791')}/health")
            statuses["browser"] = {
                "status": "connected" if resp.status_code == 200 else "error",
                "last_check": datetime.utcnow().isoformat()
            }
    except:
        statuses["browser"] = {"status": "disconnected"}

    return statuses

# ============ IDENTITY ROUTES ============

@app.get("/api/identity/")
async def get_identity_docs():
    """Get identity documents (SOUL, USER, IDENTITY, MEMORY)"""
    workspace = os.getenv("WORKSPACE_ROOT", "/root/clawd")
    docs = {}

    for doc in ["SOUL.md", "USER.md", "IDENTITY.md", "MEMORY.md", "AGENTS.md"]:
        path = os.path.join(workspace, doc)
        if os.path.exists(path):
            with open(path, "r") as f:
                docs[doc] = f.read()

    return docs

@app.put("/api/identity/{doc_name}")
async def update_identity_doc(doc_name: str, content: str, db: Session = Depends(get_db)):
    """Update an identity document"""
    workspace = os.getenv("WORKSPACE_ROOT", "/root/clawd")
    allowed = ["SOUL.md", "USER.md", "IDENTITY.md", "MEMORY.md"]

    if doc_name not in allowed:
        raise HTTPException(400, f"Document must be one of: {allowed}")

    path = os.path.join(workspace, doc_name)
    with open(path, "w") as f:
        f.write(content)

    activity = Activity(
        event_type="identity_updated",
        category="system",
        title=f"Updated {doc_name}",
        icon="🪪",
        color="purple"
    )
    db.add(activity)
    db.commit()

    return {"success": True}

# ============ WEBSOCKET ============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    # Accept all connections for local use
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# ============ STATIC FILES ============

# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 3000)))
