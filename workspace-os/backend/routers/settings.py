"""
Settings router - configuration management
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any, Optional
from database import get_db, Setting

router = APIRouter()

# Default settings
DEFAULTS = {
    "theme": "dark",
    "workspace_root": "/root/clawd",
    "auto_index": True,
    "index_interval_minutes": 5,
    "model_costs": {
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "claude-opus-4-5": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
        "gemini-2.5-flash": {"input": 0.0, "output": 0.0},
        "kimi-k2.5": {"input": 0.0, "output": 0.0}
    },
    "routing_rules": {
        "code_keywords": ["code", "function", "programming", "debug", "error", "implement"],
        "complex_threshold": 500,
        "default_model": "gemini-2.5-flash"
    }
}

@router.get("/")
async def list_settings(db: Session = Depends(get_db)):
    """Get all settings"""
    settings = db.query(Setting).all()
    result = dict(DEFAULTS)  # Start with defaults
    for s in settings:
        result[s.key] = s.value
    return result

@router.get("/{key}")
async def get_setting(key: str, db: Session = Depends(get_db)):
    """Get a specific setting"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        return {"key": key, "value": setting.value}
    if key in DEFAULTS:
        return {"key": key, "value": DEFAULTS[key], "default": True}
    raise HTTPException(404, "Setting not found")

class SettingUpdate(BaseModel):
    value: Any

@router.put("/{key}")
async def set_setting(key: str, data: SettingUpdate, db: Session = Depends(get_db)):
    """Set a setting value"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = data.value
    else:
        setting = Setting(key=key, value=data.value)
        db.add(setting)
    db.commit()
    return {"key": key, "value": data.value, "updated": True}

@router.delete("/{key}")
async def delete_setting(key: str, db: Session = Depends(get_db)):
    """Delete a setting (revert to default)"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        db.delete(setting)
        db.commit()
        return {"deleted": True, "reverted_to_default": key in DEFAULTS}
    raise HTTPException(404, "Setting not found")

@router.get("/env/check")
async def check_env():
    """Check which environment variables are set"""
    env_vars = [
        "AUTH_TOKEN",
        "WORKSPACE_ROOT",
        "CLAWDBOT_GATEWAY_URL",
        "CLAWDBOT_GATEWAY_TOKEN",
        "CLAWDBOT_BROWSER_URL",
        "AIRTABLE_API_KEY",
        "AIRTABLE_BASE_ID"
    ]
    return {
        var: bool(os.getenv(var))
        for var in env_vars
    }

@router.post("/backup")
async def backup_settings(db: Session = Depends(get_db)):
    """Export all settings as JSON"""
    settings = db.query(Setting).all()
    return {
        "backup": {s.key: s.value for s in settings},
        "defaults": DEFAULTS
    }

class RestoreRequest(BaseModel):
    settings: dict

@router.post("/restore")
async def restore_settings(data: RestoreRequest, db: Session = Depends(get_db)):
    """Import settings from backup"""
    for key, value in data.settings.items():
        setting = db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = value
        else:
            db.add(Setting(key=key, value=value))
    db.commit()
    return {"restored": len(data.settings)}
