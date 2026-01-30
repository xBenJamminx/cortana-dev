"""
Project/Kanban router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db, Project

router = APIRouter()

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "ideas"
    priority: str = "medium"
    due_date: Optional[datetime] = None
    tags: List[str] = []
    linked_files: List[str] = []
    linked_urls: List[str] = []

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    linked_files: Optional[List[str]] = None
    linked_urls: Optional[List[str]] = None
    position: Optional[int] = None

@router.get("/")
async def list_projects(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    projects = query.order_by(Project.position, Project.created_at.desc()).all()
    return [{
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "status": p.status,
        "priority": p.priority,
        "due_date": p.due_date.isoformat() if p.due_date else None,
        "tags": p.tags or [],
        "linked_files": p.linked_files or [],
        "linked_urls": p.linked_urls or [],
        "position": p.position,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat()
    } for p in projects]

@router.get("/board")
async def get_board(db: Session = Depends(get_db)):
    """Get all projects grouped by status for kanban board"""
    projects = db.query(Project).order_by(Project.position, Project.created_at.desc()).all()
    board = {"ideas": [], "in_progress": [], "review": [], "done": []}
    for p in projects:
        if p.status in board:
            board[p.status].append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "priority": p.priority,
                "due_date": p.due_date.isoformat() if p.due_date else None,
                "tags": p.tags or [],
                "position": p.position
            })
    return board

@router.post("/")
async def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    max_pos = db.query(Project).filter(Project.status == data.status).count()
    project = Project(
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
        tags=data.tags,
        linked_files=data.linked_files,
        linked_urls=data.linked_urls,
        position=max_pos
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "created": True}

@router.get("/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "priority": project.priority,
        "due_date": project.due_date.isoformat() if project.due_date else None,
        "tags": project.tags or [],
        "linked_files": project.linked_files or [],
        "linked_urls": project.linked_urls or [],
        "airtable_id": project.airtable_id,
        "position": project.position,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat()
    }

@router.patch("/{project_id}")
async def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    return {"id": project_id, "updated": True}

@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    db.commit()
    return {"deleted": True}

@router.post("/{project_id}/move")
async def move_project(project_id: int, status: str, position: int, db: Session = Depends(get_db)):
    """Move project to new status/position (for drag-drop)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    old_status = project.status
    project.status = status
    project.position = position

    # Reorder other projects in new status
    others = db.query(Project).filter(
        Project.status == status,
        Project.id != project_id,
        Project.position >= position
    ).all()
    for p in others:
        p.position += 1

    db.commit()
    return {"moved": True, "from": old_status, "to": status}
