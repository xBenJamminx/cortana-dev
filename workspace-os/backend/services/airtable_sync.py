"""
Airtable sync service for Workspace OS
Syncs all 7 tables from Cortana OS base
"""
import os
import httpx
from datetime import datetime
from typing import Optional
import asyncio

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "appdFTSkXnphHLwfl")

# Table IDs from schema
TABLES = {
    "content": "tblvLSX7DZxIRWU5g",
    "ideas": "tblyPJiNrhJfnXq51",
    "targets": "tblh6eZ6ZUeF9MArq",
    "performance": "tbl9kbia6vjKy6apE",
    "templates": "tblJsWbgZrDgXd9Gr",
    "voice": "tblx8U83MGuLPa56u",
    "goals": "tblMZ4PR7s4fIKUi9"
}

HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

async def fetch_table(table_id: str, offset: Optional[str] = None) -> dict:
    """Fetch records from an Airtable table"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_id}"
    params = {"pageSize": 100}
    if offset:
        params["offset"] = offset

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=HEADERS, params=params)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": resp.text, "records": []}

async def fetch_all_records(table_id: str) -> list:
    """Fetch all records from a table (handles pagination)"""
    all_records = []
    offset = None

    while True:
        data = await fetch_table(table_id, offset)
        if "error" in data:
            break
        all_records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break

    return all_records

def parse_content_item(record: dict) -> dict:
    """Parse content pipeline record"""
    fields = record.get("fields", {})
    status_map = {
        "💡 Idea": "idea",
        "📝 Draft": "draft",
        "👀 Review": "review",
        "✅ Approved": "approved",
        "📤 Posted": "posted",
        "❌ Rejected": "rejected"
    }
    type_map = {
        "Original": "original",
        "Reply": "reply",
        "QT": "qt",
        "Thread": "thread"
    }
    format_map = {
        "Tweet/Post": "tweet",
        "Thread": "thread",
        "Short Video": "short_video",
        "Long Video": "long_video",
        "Article": "article",
        "Carousel": "carousel"
    }
    account_map = {
        "Cortana": "cortana",
        "Ben": "ben"
    }
    return {
        "airtable_id": record["id"],
        "title": fields.get("Title", "Untitled"),
        "content": fields.get("Content"),
        "status": status_map.get(fields.get("Status"), "idea"),
        "content_type": type_map.get(fields.get("Type")),
        "content_format": format_map.get(fields.get("Format")),
        "account": account_map.get(fields.get("Account")),
        "scheduled": fields.get("Scheduled"),
        "posted_url": fields.get("Posted URL"),
        "notes": fields.get("Notes"),
        "synced_at": datetime.utcnow()
    }

def parse_idea(record: dict) -> dict:
    """Parse ideas inbox record"""
    fields = record.get("fields", {})
    source_map = {
        "Observation": "observation",
        "Conversation": "conversation",
        "Article/Tweet": "article",
        "Analytics": "analytics",
        "Request": "request"
    }
    priority_map = {
        "🔥 Hot": "hot",
        "📌 Save": "save",
        "💭 Maybe": "maybe"
    }
    return {
        "airtable_id": record["id"],
        "idea": fields.get("Idea", ""),
        "source": source_map.get(fields.get("Source")),
        "priority": priority_map.get(fields.get("Priority")),
        "used": fields.get("Used", False),
        "source_url": fields.get("Source URL"),
        "notes": fields.get("Notes"),
        "synced_at": datetime.utcnow()
    }

def parse_target(record: dict) -> dict:
    """Parse target account record"""
    fields = record.get("fields", {})
    category_map = {
        "AI/ML": "ai_ml",
        "Indie Hackers": "indie_hackers",
        "Automation": "automation",
        "Crypto/Web3": "crypto",
        "Creator": "creator",
        "Tech": "tech"
    }
    priority_map = {
        "🔥 Daily": "daily",
        "📅 Weekly": "weekly",
        "👀 Watch": "watch"
    }
    return {
        "airtable_id": record["id"],
        "handle": fields.get("Handle", ""),
        "name": fields.get("Name"),
        "category": category_map.get(fields.get("Category")),
        "followers": fields.get("Followers"),
        "engage_priority": priority_map.get(fields.get("Engage Priority")),
        "last_engaged": fields.get("Last Engaged"),
        "profile_url": fields.get("Profile URL"),
        "notes": fields.get("Notes"),
        "synced_at": datetime.utcnow()
    }

def parse_performance(record: dict) -> dict:
    """Parse performance log record"""
    fields = record.get("fields", {})
    platform_map = {
        "Twitter": "twitter",
        "YouTube": "youtube",
        "TikTok": "tiktok",
        "LinkedIn": "linkedin"
    }
    grade_map = {
        "🔥 Banger": "banger",
        "✅ Solid": "solid",
        "😐 Meh": "meh",
        "❌ Flop": "flop"
    }
    return {
        "airtable_id": record["id"],
        "post_title": fields.get("Post"),
        "platform": platform_map.get(fields.get("Platform")),
        "account": fields.get("Account"),
        "posted_date": fields.get("Posted Date"),
        "impressions": fields.get("Impressions", 0),
        "engagements": fields.get("Engagements", 0),
        "followers_gained": fields.get("Followers Gained", 0),
        "post_url": fields.get("Post URL"),
        "what_worked": fields.get("What Worked"),
        "grade": grade_map.get(fields.get("Grade")),
        "synced_at": datetime.utcnow()
    }

def parse_template(record: dict) -> dict:
    """Parse content template record"""
    fields = record.get("fields", {})
    format_map = {
        "Hot Take": "hot_take",
        "Tutorial": "tutorial",
        "Behind the Scenes": "behind_scenes",
        "Thread": "thread",
        "Story": "story",
        "Observation": "observation",
        "Question": "question"
    }
    perf_map = {
        "🔥 High": "high",
        "✅ Medium": "medium",
        "😐 Low": "low"
    }
    return {
        "airtable_id": record["id"],
        "name": fields.get("Template Name", ""),
        "format_type": format_map.get(fields.get("Format Type")),
        "structure": fields.get("Structure"),
        "example": fields.get("Example"),
        "best_for": fields.get("Best For"),
        "times_used": fields.get("Times Used", 0),
        "avg_performance": perf_map.get(fields.get("Avg Performance")),
        "synced_at": datetime.utcnow()
    }

def parse_voice(record: dict) -> dict:
    """Parse voice guideline record"""
    fields = record.get("fields", {})
    return {
        "airtable_id": record["id"],
        "account_name": fields.get("Account Name", ""),
        "tone": fields.get("Tone"),
        "do_list": fields.get("Do"),
        "dont_list": fields.get("Dont"),
        "example_good": fields.get("Example Good"),
        "example_bad": fields.get("Example Bad"),
        "topics": fields.get("Topics"),
        "emoji_style": fields.get("Emoji Style"),
        "synced_at": datetime.utcnow()
    }

def parse_goal(record: dict) -> dict:
    """Parse weekly goal record"""
    fields = record.get("fields", {})
    return {
        "airtable_id": record["id"],
        "week_of": fields.get("Week Of"),
        "tweets_goal": fields.get("Tweets Goal", 0),
        "tweets_actual": fields.get("Tweets Actual", 0),
        "replies_goal": fields.get("Replies Goal", 0),
        "replies_actual": fields.get("Replies Actual", 0),
        "followers_start": fields.get("Followers Start", 0),
        "followers_end": fields.get("Followers End", 0),
        "top_post_url": fields.get("Top Post"),
        "learnings": fields.get("Learnings"),
        "next_week_focus": fields.get("Next Week Focus"),
        "synced_at": datetime.utcnow()
    }

async def sync_all(db_session) -> dict:
    """Sync all Airtable tables to local database"""
    from database import (ContentItem, Idea, TargetAccount, PerformanceLog,
                         ContentTemplate, VoiceGuideline, WeeklyGoal)

    results = {}

    # Content Pipeline
    records = await fetch_all_records(TABLES["content"])
    for record in records:
        data = parse_content_item(record)
        existing = db_session.query(ContentItem).filter_by(airtable_id=data["airtable_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db_session.add(ContentItem(**data))
    results["content"] = len(records)

    # Ideas
    records = await fetch_all_records(TABLES["ideas"])
    for record in records:
        data = parse_idea(record)
        existing = db_session.query(Idea).filter_by(airtable_id=data["airtable_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db_session.add(Idea(**data))
    results["ideas"] = len(records)

    # Targets
    records = await fetch_all_records(TABLES["targets"])
    for record in records:
        data = parse_target(record)
        existing = db_session.query(TargetAccount).filter_by(airtable_id=data["airtable_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db_session.add(TargetAccount(**data))
    results["targets"] = len(records)

    # Performance
    records = await fetch_all_records(TABLES["performance"])
    for record in records:
        data = parse_performance(record)
        existing = db_session.query(PerformanceLog).filter_by(airtable_id=data["airtable_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db_session.add(PerformanceLog(**data))
    results["performance"] = len(records)

    # Templates
    records = await fetch_all_records(TABLES["templates"])
    for record in records:
        data = parse_template(record)
        existing = db_session.query(ContentTemplate).filter_by(airtable_id=data["airtable_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db_session.add(ContentTemplate(**data))
    results["templates"] = len(records)

    # Voice Guidelines
    records = await fetch_all_records(TABLES["voice"])
    for record in records:
        data = parse_voice(record)
        existing = db_session.query(VoiceGuideline).filter_by(airtable_id=data["airtable_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db_session.add(VoiceGuideline(**data))
    results["voice"] = len(records)

    # Weekly Goals
    records = await fetch_all_records(TABLES["goals"])
    for record in records:
        data = parse_goal(record)
        existing = db_session.query(WeeklyGoal).filter_by(airtable_id=data["airtable_id"]).first()
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db_session.add(WeeklyGoal(**data))
    results["goals"] = len(records)

    db_session.commit()
    return results

async def create_content_item(data: dict) -> Optional[dict]:
    """Create a new content item in Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLES['content']}"

    status_map = {
        "idea": "💡 Idea",
        "draft": "📝 Draft",
        "review": "👀 Review",
        "approved": "✅ Approved",
        "posted": "📤 Posted",
        "rejected": "❌ Rejected"
    }
    type_map = {
        "original": "Original",
        "reply": "Reply",
        "qt": "QT",
        "thread": "Thread"
    }
    format_map = {
        "tweet": "Tweet/Post",
        "thread": "Thread",
        "short_video": "Short Video",
        "long_video": "Long Video",
        "article": "Article",
        "carousel": "Carousel"
    }
    account_map = {
        "cortana": "Cortana",
        "ben": "Ben"
    }

    fields = {
        "Title": data.get("title"),
        "Content": data.get("content"),
        "Status": status_map.get(data.get("status"), "💡 Idea"),
        "Notes": data.get("notes")
    }
    if data.get("content_type"):
        fields["Type"] = type_map.get(data["content_type"])
    if data.get("content_format"):
        fields["Format"] = format_map.get(data["content_format"])
    if data.get("account"):
        fields["Account"] = account_map.get(data["account"])

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=HEADERS, json={"fields": fields})
        if resp.status_code == 200:
            return resp.json()
        return None

async def update_content_item(airtable_id: str, data: dict) -> Optional[dict]:
    """Update a content item in Airtable"""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLES['content']}/{airtable_id}"

    status_map = {
        "idea": "💡 Idea",
        "draft": "📝 Draft",
        "review": "👀 Review",
        "approved": "✅ Approved",
        "posted": "📤 Posted",
        "rejected": "❌ Rejected"
    }

    format_map = {
        "tweet": "Tweet/Post",
        "thread": "Thread",
        "short_video": "Short Video",
        "long_video": "Long Video",
        "article": "Article",
        "carousel": "Carousel"
    }

    fields = {}
    if "title" in data:
        fields["Title"] = data["title"]
    if "content" in data:
        fields["Content"] = data["content"]
    if "status" in data:
        fields["Status"] = status_map.get(data["status"])
    if "content_format" in data:
        fields["Format"] = format_map.get(data["content_format"])
    if "notes" in data:
        fields["Notes"] = data["notes"]
    if "posted_url" in data:
        fields["Posted URL"] = data["posted_url"]

    async with httpx.AsyncClient() as client:
        resp = await client.patch(url, headers=HEADERS, json={"fields": fields})
        if resp.status_code == 200:
            return resp.json()
        return None
