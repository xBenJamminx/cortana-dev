"""
Bookmarks API - Search and manage X/Twitter bookmarks
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import get_db, Bookmark

router = APIRouter()

class BookmarkResponse(BaseModel):
    id: int
    tweet_id: Optional[str]
    content: str
    author: Optional[str]
    author_handle: Optional[str]
    likes: int
    retweets: int
    category: Optional[str]
    url: Optional[str]
    status: str
    bookmarked_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class BookmarkSearchResponse(BaseModel):
    results: List[BookmarkResponse]
    total: int
    page: int
    per_page: int
    has_more: bool

@router.get("/search", response_model=BookmarkSearchResponse)
async def search_bookmarks(
    q: Optional[str] = Query(None, description="Search keyword"),
    author: Optional[str] = Query(None, description="Filter by author"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (unread, read, archived)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search bookmarks by keyword, author, or category.
    Returns paginated results.
    """
    query = db.query(Bookmark)
    
    # Keyword search across content, author, notes
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                Bookmark.content.ilike(search_term),
                Bookmark.author.ilike(search_term),
                Bookmark.author_handle.ilike(search_term),
                Bookmark.notes.ilike(search_term)
            )
        )
    
    # Filter by author
    if author:
        author_term = f"%{author}%"
        query = query.filter(
            or_(
                Bookmark.author.ilike(author_term),
                Bookmark.author_handle.ilike(author_term)
            )
        )
    
    # Filter by category
    if category:
        query = query.filter(Bookmark.category.ilike(f"%{category}%"))
    
    # Filter by status
    if status:
        query = query.filter(Bookmark.status == status)
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    results = query.order_by(Bookmark.bookmarked_at.desc()).offset(offset).limit(per_page).all()
    
    return BookmarkSearchResponse(
        results=results,
        total=total,
        page=page,
        per_page=per_page,
        has_more=(offset + len(results)) < total
    )

@router.get("/", response_model=BookmarkSearchResponse)
async def list_bookmarks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all bookmarks with pagination."""
    return await search_bookmarks(page=page, per_page=per_page, db=db)

@router.get("/categories")
async def list_categories(db: Session = Depends(get_db)):
    """Get list of all bookmark categories."""
    categories = db.query(Bookmark.category).distinct().filter(Bookmark.category.isnot(None)).all()
    return [c[0] for c in categories if c[0]]

@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    """Get a single bookmark by ID."""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark

@router.patch("/{bookmark_id}/status")
async def update_bookmark_status(
    bookmark_id: int,
    status: str = Query(..., description="New status: unread, read, archived"),
    db: Session = Depends(get_db)
):
    """Update bookmark status."""
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
    if not bookmark:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Bookmark not found")
    bookmark.status = status
    db.commit()
    return {"success": True, "status": status}
