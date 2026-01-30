"""
Dashboard router - stats and activity feed
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db, Project, AICall, Activity, FileIndex, ContentItem, Idea

router = APIRouter()

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Project counts by status
    project_stats = {}
    for status in ["ideas", "in_progress", "review", "done"]:
        count = db.query(Project).filter(Project.status == status).count()
        project_stats[status] = count
    
    total_projects = sum(project_stats.values())
    
    # Content items count
    content_count = db.query(ContentItem).count()
    
    # Ideas count
    ideas_count = db.query(Idea).count()
    
    # Today's AI costs
    today_cost = db.query(func.sum(AICall.cost)).filter(
        AICall.created_at >= today
    ).scalar() or 0.0
    
    # Weekly AI costs
    weekly_cost = db.query(func.sum(AICall.cost)).filter(
        AICall.created_at >= week_ago
    ).scalar() or 0.0
    
    # Monthly AI costs (30 days)
    monthly_cost = db.query(func.sum(AICall.cost)).filter(
        AICall.created_at >= month_ago
    ).scalar() or 0.0
    
    # File counts
    file_count = db.query(FileIndex).count()
    
    # Recent activity count
    recent_activity = db.query(Activity).filter(
        Activity.created_at >= today
    ).count()
    
    return {
        "projects": total_projects,
        "project_breakdown": project_stats,
        "total_projects": total_projects,
        "content": content_count,
        "content_items": content_count,
        "ideas": ideas_count,
        "ai_costs": round(monthly_cost, 2),
        "costs": {
            "today": round(today_cost, 4),
            "weekly": round(weekly_cost, 4),
            "monthly": round(monthly_cost, 2)
        },
        "files": file_count,
        "today_activities": recent_activity
    }

@router.get("/activity")
async def get_activity(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent activity feed"""
    activities = db.query(Activity).order_by(
        Activity.created_at.desc()
    ).limit(limit).all()
    
    return [{
        "id": a.id,
        "event_type": a.event_type,
        "type": a.event_type,
        "title": a.title,
        "description": a.description,
        "metadata": a.extra_data,
        "created_at": a.created_at.isoformat(),
        "timestamp": a.created_at.isoformat()
    } for a in activities]

@router.post("/activity")
async def create_activity(
    event_type: str,
    title: str,
    description: str = None,
    metadata: dict = None,
    db: Session = Depends(get_db)
):
    """Create a new activity entry"""
    activity = Activity(
        event_type=event_type,
        title=title,
        description=description,
        extra_data=metadata or {}
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return {"id": activity.id, "created_at": activity.created_at.isoformat()}
