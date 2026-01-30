"""
File manager router
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, FileIndex, Activity

router = APIRouter()

WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", "/root/clawd")
EXCLUDE_DIRS = os.getenv("WATCH_EXCLUDE", ".clawdbot,clawdbot.json,workspace-os").split(",")

def get_file_type(ext):
    ext = ext.lower().lstrip(".")
    if ext in ["py", "js", "ts", "jsx", "tsx", "go", "rs", "java", "sh"]:
        return "code"
    elif ext in ["md", "txt", "rst", "pdf"]:
        return "doc"
    elif ext in ["png", "jpg", "jpeg", "gif", "svg", "webp"]:
        return "image"
    elif ext in ["json", "yaml", "yml", "toml", "ini", "env"]:
        return "config"
    return "other"

def should_exclude(path):
    return any(exc in path for exc in EXCLUDE_DIRS)

@router.get("/tree")
async def get_file_tree(path: str = ""):
    base_path = os.path.join(WORKSPACE_ROOT, path)
    if not os.path.exists(base_path):
        raise HTTPException(404, "Path not found")
    if not base_path.startswith(WORKSPACE_ROOT):
        raise HTTPException(403, "Access denied")

    items = []
    for entry in os.scandir(base_path):
        if should_exclude(entry.path):
            continue
        rel_path = os.path.relpath(entry.path, WORKSPACE_ROOT)
        stat = entry.stat()
        item = {
            "name": entry.name,
            "path": rel_path,
            "is_dir": entry.is_dir(),
            "size": stat.st_size if entry.is_file() else None,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
        if entry.is_file():
            ext = Path(entry.name).suffix
            item["extension"] = ext
            item["type"] = get_file_type(ext)
        items.append(item)

    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    return {"path": path, "items": items}

@router.get("/read")
async def read_file(path: str):
    full_path = os.path.join(WORKSPACE_ROOT, path)
    if not os.path.exists(full_path):
        raise HTTPException(404, "File not found")
    if os.path.isdir(full_path):
        raise HTTPException(400, "Path is a directory")

    ext = Path(full_path).suffix.lower()
    file_type = get_file_type(ext)

    if file_type == "image":
        return FileResponse(full_path)

    try:
        with open(full_path, "r") as f:
            content = f.read()
        return {
            "path": path,
            "name": os.path.basename(path),
            "content": content,
            "type": file_type,
            "size": os.path.getsize(full_path)
        }
    except UnicodeDecodeError:
        return {"path": path, "content": None, "type": "binary"}

class FileWrite(BaseModel):
    path: str
    content: str

@router.post("/write")
async def write_file(data: FileWrite, db: Session = Depends(get_db)):
    full_path = os.path.join(WORKSPACE_ROOT, data.path)
    if not full_path.startswith(WORKSPACE_ROOT):
        raise HTTPException(403, "Access denied")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    is_new = not os.path.exists(full_path)
    with open(full_path, "w") as f:
        f.write(data.content)
    event = "file_created" if is_new else "file_modified"
    title = f"{'Created' if is_new else 'Modified'}: {os.path.basename(data.path)}"
    activity = Activity(
        event_type=event,
        title=title,
        description=data.path,
        extra_data={"path": data.path}
    )
    db.add(activity)
    db.commit()
    return {"success": True, "path": data.path}

@router.delete("/delete")
async def delete_file(path: str, db: Session = Depends(get_db)):
    full_path = os.path.join(WORKSPACE_ROOT, path)
    if not os.path.exists(full_path):
        raise HTTPException(404, "Path not found")
    if os.path.isdir(full_path):
        shutil.rmtree(full_path)
    else:
        os.remove(full_path)
    activity = Activity(
        event_type="file_deleted",
        title=f"Deleted: {os.path.basename(path)}",
        description=path,
        extra_data={"path": path}
    )
    db.add(activity)
    db.commit()
    return {"success": True, "deleted": path}

@router.post("/mkdir")
async def create_directory(path: str, db: Session = Depends(get_db)):
    full_path = os.path.join(WORKSPACE_ROOT, path)
    if not full_path.startswith(WORKSPACE_ROOT):
        raise HTTPException(403, "Access denied")
    os.makedirs(full_path, exist_ok=True)
    return {"success": True, "path": path}

@router.get("/search")
async def search_files(q: str, db: Session = Depends(get_db)):
    results = db.query(FileIndex).filter(
        (FileIndex.name.ilike(f"%{q}%")) |
        (FileIndex.content_preview.ilike(f"%{q}%"))
    ).limit(50).all()
    return {"query": q, "results": [{"path": f.path, "name": f.name, "type": f.file_type} for f in results]}

@router.post("/index")
async def reindex_files(db: Session = Depends(get_db)):
    count = 0
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
        for name in files:
            full_path = os.path.join(root, name)
            if should_exclude(full_path):
                continue
            rel_path = os.path.relpath(full_path, WORKSPACE_ROOT)
            ext = Path(name).suffix
            file_type = get_file_type(ext)

            content_preview = None
            if file_type in ["code", "doc", "config"]:
                try:
                    with open(full_path, "r") as f:
                        content_preview = f.read(1000)
                except:
                    pass

            stat = os.stat(full_path)
            existing = db.query(FileIndex).filter(FileIndex.path == rel_path).first()
            if existing:
                existing.content_preview = content_preview
                existing.modified_at = datetime.fromtimestamp(stat.st_mtime)
            else:
                db.add(FileIndex(
                    path=rel_path,
                    name=name,
                    extension=ext,
                    file_type=file_type,
                    size=stat.st_size,
                    content_preview=content_preview,
                    modified_at=datetime.fromtimestamp(stat.st_mtime)
                ))
            count += 1
    db.commit()
    return {"indexed": count}
