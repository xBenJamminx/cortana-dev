"""
Content Pipeline router - Airtable integration
"""
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appdFTSkXnphHLwfl")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Content Pipeline")

def get_airtable_headers():
    return {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

def get_airtable_url(record_id: str = None):
    base = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME.replace(' ', '%20')}"
    if record_id:
        return f"{base}/{record_id}"
    return base

@router.get("/")
async def list_content(status: Optional[str] = None, platform: Optional[str] = None):
    """List content pipeline items from Airtable"""
    if not AIRTABLE_API_KEY:
        raise HTTPException(500, "Airtable API key not configured")

    params = {}
    filters = []
    if status:
        filters.append(f"{{Status}}='{status}'")
    if platform:
        filters.append(f"{{Platform}}='{platform}'")
    if filters:
        params["filterByFormula"] = "AND(" + ",".join(filters) + ")"

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            get_airtable_url(),
            headers=get_airtable_headers(),
            params=params
        )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)
        data = resp.json()

    return [{
        "id": r["id"],
        "fields": r["fields"],
        "created_at": r.get("createdTime")
    } for r in data.get("records", [])]

@router.get("/{record_id}")
async def get_content(record_id: str):
    """Get single content item"""
    if not AIRTABLE_API_KEY:
        raise HTTPException(500, "Airtable API key not configured")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            get_airtable_url(record_id),
            headers=get_airtable_headers()
        )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)
        return resp.json()

class ContentCreate(BaseModel):
    content: str
    platform: str = "Twitter"
    status: str = "Draft"
    content_format: Optional[str] = None
    scheduled_date: Optional[str] = None
    notes: Optional[str] = None

@router.post("/")
async def create_content(data: ContentCreate):
    """Create new content item"""
    if not AIRTABLE_API_KEY:
        raise HTTPException(500, "Airtable API key not configured")

    fields = {
        "Content": data.content,
        "Platform": data.platform,
        "Status": data.status
    }
    if data.content_format:
        fields["Format"] = data.content_format
    if data.scheduled_date:
        fields["Scheduled Date"] = data.scheduled_date
    if data.notes:
        fields["Notes"] = data.notes

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            get_airtable_url(),
            headers=get_airtable_headers(),
            json={"fields": fields}
        )
        if resp.status_code not in [200, 201]:
            raise HTTPException(resp.status_code, resp.text)
        return resp.json()

class ContentUpdate(BaseModel):
    content: Optional[str] = None
    platform: Optional[str] = None
    status: Optional[str] = None
    content_format: Optional[str] = None
    scheduled_date: Optional[str] = None
    posted_url: Optional[str] = None
    notes: Optional[str] = None

@router.patch("/{record_id}")
async def update_content(record_id: str, data: ContentUpdate):
    """Update content item"""
    if not AIRTABLE_API_KEY:
        raise HTTPException(500, "Airtable API key not configured")

    fields = {}
    if data.content is not None:
        fields["Content"] = data.content
    if data.platform is not None:
        fields["Platform"] = data.platform
    if data.status is not None:
        fields["Status"] = data.status
    if data.content_format is not None:
        fields["Format"] = data.content_format
    if data.scheduled_date is not None:
        fields["Scheduled Date"] = data.scheduled_date
    if data.posted_url is not None:
        fields["Posted URL"] = data.posted_url
    if data.notes is not None:
        fields["Notes"] = data.notes

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            get_airtable_url(record_id),
            headers=get_airtable_headers(),
            json={"fields": fields}
        )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)
        return resp.json()

@router.delete("/{record_id}")
async def delete_content(record_id: str):
    """Delete content item"""
    if not AIRTABLE_API_KEY:
        raise HTTPException(500, "Airtable API key not configured")

    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            get_airtable_url(record_id),
            headers=get_airtable_headers()
        )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)
        return {"deleted": True}

@router.get("/stats/pipeline")
async def get_pipeline_stats():
    """Get content pipeline statistics"""
    if not AIRTABLE_API_KEY:
        raise HTTPException(500, "Airtable API key not configured")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            get_airtable_url(),
            headers=get_airtable_headers()
        )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, resp.text)

    records = resp.json().get("records", [])
    stats = {"total": len(records), "by_status": {}, "by_platform": {}, "by_format": {}}

    for r in records:
        status = r["fields"].get("Status", "Unknown")
        platform = r["fields"].get("Platform", "Unknown")
        fmt = r["fields"].get("Format", "Unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
        stats["by_format"][fmt] = stats["by_format"].get(fmt, 0) + 1

    return stats
