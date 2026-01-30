"""
Memory & Knowledge router - search and indexing
"""
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db, Memory, FileIndex

router = APIRouter()

WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/root/clawd")

@router.get("/search")
async def search_memory(q: str, limit: int = 20, db: Session = Depends(get_db)):
    """Search across memories and indexed files"""
    results = []

    # Search memories
    memories = db.query(Memory).filter(
        Memory.content.ilike(f"%{q}%")
    ).limit(limit).all()

    for m in memories:
        results.append({
            "type": "memory",
            "id": m.id,
            "content": m.content[:300] + "..." if len(m.content) > 300 else m.content,
            "source": m.source,
            "tags": m.tags or [],
            "created_at": m.created_at.isoformat()
        })

    # Search files
    files = db.query(FileIndex).filter(
        (FileIndex.name.ilike(f"%{q}%")) |
        (FileIndex.content_preview.ilike(f"%{q}%"))
    ).limit(limit).all()

    for f in files:
        results.append({
            "type": "file",
            "path": f.path,
            "name": f.name,
            "file_type": f.file_type,
            "preview": f.content_preview[:200] if f.content_preview else None
        })

    return {"query": q, "total": len(results), "results": results}

class MemoryCreate(BaseModel):
    content: str
    source: Optional[str] = "manual"
    tags: List[str] = []

@router.post("/")
async def create_memory(data: MemoryCreate, db: Session = Depends(get_db)):
    """Add a new memory entry"""
    memory = Memory(
        content=data.content,
        source=data.source,
        tags=data.tags
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return {"id": memory.id, "created": True}

@router.get("/")
async def list_memories(limit: int = 50, tag: Optional[str] = None, db: Session = Depends(get_db)):
    """List recent memories"""
    query = db.query(Memory)
    if tag:
        # SQLite JSON contains check
        query = query.filter(Memory.tags.contains([tag]))
    memories = query.order_by(Memory.created_at.desc()).limit(limit).all()

    return [{
        "id": m.id,
        "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
        "source": m.source,
        "tags": m.tags or [],
        "created_at": m.created_at.isoformat()
    } for m in memories]

@router.get("/{memory_id}")
async def get_memory(memory_id: int, db: Session = Depends(get_db)):
    """Get a specific memory"""
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(404, "Memory not found")
    return {
        "id": memory.id,
        "content": memory.content,
        "source": memory.source,
        "tags": memory.tags or [],
        "created_at": memory.created_at.isoformat()
    }

@router.delete("/{memory_id}")
async def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    """Delete a memory"""
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(404, "Memory not found")
    db.delete(memory)
    db.commit()
    return {"deleted": True}

@router.post("/import/files")
async def import_memory_files(db: Session = Depends(get_db)):
    """Import memories from /root/clawd/memory/ files"""
    memory_dir = os.path.join(WORKSPACE_ROOT, "memory")
    if not os.path.exists(memory_dir):
        return {"imported": 0, "error": "Memory directory not found"}

    imported = 0
    for filename in os.listdir(memory_dir):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(memory_dir, filename)
        try:
            with open(filepath, "r") as f:
                content = f.read()

            # Check if already imported
            existing = db.query(Memory).filter(Memory.source == filepath).first()
            if existing:
                existing.content = content
            else:
                memory = Memory(
                    content=content,
                    source=filepath,
                    tags=["imported", "daily-notes"]
                )
                db.add(memory)
                imported += 1
        except Exception as e:
            continue

    db.commit()
    return {"imported": imported}

@router.get("/tags")
async def list_tags(db: Session = Depends(get_db)):
    """List all unique tags"""
    memories = db.query(Memory.tags).all()
    all_tags = set()
    for (tags,) in memories:
        if tags:
            all_tags.update(tags)
    return {"tags": sorted(list(all_tags))}
