"""
AI Command Center router - model routing, image gen, cost tracking
"""
import os
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from database import get_db, AICall

router = APIRouter()

CLAWDBOT_GATEWAY_URL = os.getenv("CLAWDBOT_GATEWAY_URL", "http://127.0.0.1:18789")
CLAWDBOT_GATEWAY_TOKEN = os.getenv("CLAWDBOT_GATEWAY_TOKEN")

async def call_clawdbot(endpoint: str, method: str = "GET", data: dict = None):
    """Call clawdbot gateway API"""
    url = f"{CLAWDBOT_GATEWAY_URL}{endpoint}"
    params = {"token": CLAWDBOT_GATEWAY_TOKEN} if CLAWDBOT_GATEWAY_TOKEN else {}

    async with httpx.AsyncClient(timeout=60.0) as client:
        if method == "GET":
            resp = await client.get(url, params=params)
        else:
            resp = await client.post(url, params=params, json=data)
        return resp

@router.get("/models")
async def list_models():
    """List available models from clawdbot config"""
    resp = await call_clawdbot("/api/models")
    if resp.status_code != 200:
        return {"models": [], "error": "Could not fetch models"}
    return resp.json()

@router.get("/routing/test")
async def test_routing(prompt: str):
    """Test which model would be selected for a prompt using smart router"""
    import sys
    sys.path.insert(0, "/root/clawd")
    try:
        from model_router import route, classify_complexity
        choice = route(prompt)
        complexity = classify_complexity(prompt)
        return {
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "complexity": complexity,
            "suggested_model": choice.model,
            "reason": choice.reason,
            "cost_per_1m": choice.cost_per_1m,
            "prompt_length": len(prompt)
        }
    except Exception as e:
        return {"error": str(e), "default": "google/gemini-2.5-flash"}

class ImageGenRequest(BaseModel):
    prompt: str
    complexity: str = "standard"  # simple, standard, complex
    save_to: Optional[str] = None

@router.post("/image/generate")
async def generate_image(data: ImageGenRequest, db: Session = Depends(get_db)):
    """Generate image via clawdbot"""
    # Map complexity to provider
    provider_map = {
        "simple": "gemini",
        "standard": "openai",
        "complex": "openai"
    }

    # Call clawdbot's image generation
    resp = await call_clawdbot("/api/ai/image", "POST", {
        "prompt": data.prompt,
        "provider": provider_map.get(data.complexity, "openai")
    })

    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Image generation failed")

    result = resp.json()

    # Log the call
    ai_call = AICall(
        provider="openai" if data.complexity != "simple" else "google",
        model="dall-e-3" if data.complexity != "simple" else "imagen",
        input_tokens=len(data.prompt.split()),
        output_tokens=0,
        cost=0.04 if data.complexity == "complex" else 0.02,
        prompt_preview=data.prompt[:200],
        response_preview=result.get("url", "")[:200],
        success=True
    )
    db.add(ai_call)
    db.commit()

    return result

@router.get("/costs")
async def get_costs(days: int = 7, db: Session = Depends(get_db)):
    """Get AI cost summary"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Total costs
    total = db.query(func.sum(AICall.cost)).filter(
        AICall.created_at >= cutoff
    ).scalar() or 0.0

    # By provider
    by_provider = {}
    results = db.query(
        AICall.provider,
        func.sum(AICall.cost),
        func.count(AICall.id)
    ).filter(
        AICall.created_at >= cutoff
    ).group_by(AICall.provider).all()

    for provider, cost, count in results:
        by_provider[provider] = {"cost": round(cost or 0, 4), "calls": count}

    # By day
    by_day = {}
    results = db.query(
        func.date(AICall.created_at),
        func.sum(AICall.cost)
    ).filter(
        AICall.created_at >= cutoff
    ).group_by(func.date(AICall.created_at)).all()

    for day, cost in results:
        by_day[str(day)] = round(cost or 0, 4)

    return {
        "period_days": days,
        "total_cost": round(total, 4),
        "by_provider": by_provider,
        "by_day": by_day
    }

@router.get("/logs")
async def get_ai_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent AI call logs"""
    calls = db.query(AICall).order_by(AICall.created_at.desc()).limit(limit).all()
    return [{
        "id": c.id,
        "provider": c.provider,
        "model": c.model,
        "input_tokens": c.input_tokens,
        "output_tokens": c.output_tokens,
        "cost": c.cost,
        "prompt_preview": c.prompt_preview,
        "success": c.success,
        "error": c.error,
        "created_at": c.created_at.isoformat()
    } for c in calls]

@router.post("/log")
async def log_ai_call(
    provider: str,
    model: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost: float = 0.0,
    prompt_preview: str = None,
    response_preview: str = None,
    success: bool = True,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Log an AI API call"""
    ai_call = AICall(
        provider=provider,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        prompt_preview=prompt_preview,
        response_preview=response_preview,
        success=success,
        error=error
    )
    db.add(ai_call)
    db.commit()
    return {"logged": True, "id": ai_call.id}
