"""
Comprehensive database models for Workspace OS
"""
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import text
import enum

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./workspace.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="idea")
    priority = Column(Integer, default=0)
    tags = Column(JSON, default=list)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tasks = relationship("ProjectTask", back_populates="project", cascade="all, delete-orphan")

class ProjectTask(Base):
    __tablename__ = "project_tasks"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", back_populates="tasks")

class FileIndex(Base):
    __tablename__ = "file_index"
    id = Column(Integer, primary_key=True)
    path = Column(String(512), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    extension = Column(String(50))
    file_type = Column(String(50))
    size = Column(Integer)
    content_preview = Column(Text)
    git_status = Column(String(20))
    modified_at = Column(DateTime)
    indexed_at = Column(DateTime, default=datetime.utcnow)

class AICall(Base):
    __tablename__ = "ai_calls"
    id = Column(Integer, primary_key=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    prompt_preview = Column(Text)
    response_preview = Column(Text)
    success = Column(Boolean, default=True)
    error = Column(Text)
    duration_ms = Column(Integer)
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)
    category = Column(String(50))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(20))
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"
    id = Column(Integer, primary_key=True)
    memory_type = Column(String(50), nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    source = Column(String(100))
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentItem(Base):
    __tablename__ = "content_items"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    status = Column(String(50), default="idea")
    content_type = Column(String(50))
    account = Column(String(50))
    scheduled = Column(DateTime)
    posted_url = Column(String(500))
    notes = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    idea = Column(Text, nullable=False)
    source = Column(String(50))
    priority = Column(String(20))
    used = Column(Boolean, default=False)
    source_url = Column(String(500))
    notes = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class TargetAccount(Base):
    __tablename__ = "target_accounts"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    handle = Column(String(100), nullable=False)
    name = Column(String(255))
    category = Column(String(50))
    followers = Column(Integer)
    engage_priority = Column(String(20))
    last_engaged = Column(DateTime)
    profile_url = Column(String(500))
    notes = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

class PerformanceLog(Base):
    __tablename__ = "performance_logs"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    post_title = Column(String(255))
    platform = Column(String(50))
    account = Column(String(50))
    posted_date = Column(DateTime)
    impressions = Column(Integer, default=0)
    engagements = Column(Integer, default=0)
    followers_gained = Column(Integer, default=0)
    post_url = Column(String(500))
    what_worked = Column(Text)
    grade = Column(String(20))
    synced_at = Column(DateTime, default=datetime.utcnow)

class ContentTemplate(Base):
    __tablename__ = "content_templates"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    name = Column(String(255), nullable=False)
    format_type = Column(String(50))
    structure = Column(Text)
    example = Column(Text)
    best_for = Column(Text)
    times_used = Column(Integer, default=0)
    avg_performance = Column(String(20))
    synced_at = Column(DateTime, default=datetime.utcnow)

class VoiceGuideline(Base):
    __tablename__ = "voice_guidelines"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    account_name = Column(String(100), nullable=False)
    tone = Column(Text)
    do_list = Column(Text)
    dont_list = Column(Text)
    example_good = Column(Text)
    example_bad = Column(Text)
    topics = Column(Text)
    emoji_style = Column(String(100))
    synced_at = Column(DateTime, default=datetime.utcnow)

class WeeklyGoal(Base):
    __tablename__ = "weekly_goals"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    week_of = Column(DateTime, nullable=False)
    tweets_goal = Column(Integer, default=0)
    tweets_actual = Column(Integer, default=0)
    replies_goal = Column(Integer, default=0)
    replies_actual = Column(Integer, default=0)
    followers_start = Column(Integer, default=0)
    followers_end = Column(Integer, default=0)
    top_post_url = Column(String(500))
    learnings = Column(Text)
    next_week_focus = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class IntegrationStatus(Base):
    __tablename__ = "integration_status"
    id = Column(Integer, primary_key=True)
    service = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="unknown")
    last_check = Column(DateTime)
    last_error = Column(Text)
    extra_data = Column(JSON, default=dict)

def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True)
    airtable_id = Column(String(50), unique=True)
    tweet_id = Column(String(50))
    content = Column(Text, nullable=False)
    author = Column(String(100))
    author_handle = Column(String(100))
    likes = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    category = Column(String(100))
    url = Column(String(500))
    status = Column(String(50), default="unread")
    notes = Column(Text)
    bookmarked_at = Column(DateTime)
    synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
