from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.user import User, BrandSetting, ContentPillar, InstagramAccount
from backend.api.auth import get_current_user
from backend.services.instagram import instagram_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


class PillarUpdate(BaseModel):
    id: Optional[int] = None
    name: str
    percentage: int
    description: Optional[str] = None


class SettingsUpdateRequest(BaseModel):
    primary_color: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    secondary_color: Optional[str] = None
    brand_name: Optional[str] = None
    tagline: Optional[str] = None
    niche: Optional[str] = None
    posting_time: Optional[str] = None
    timezone: Optional[str] = None
    active_days: Optional[List[str]] = None
    ai_provider: Optional[str] = None
    auto_mode_enabled: Optional[bool] = None
    posts_per_day: Optional[int] = None
    pillars: Optional[List[PillarUpdate]] = None


@router.get("")
def get_settings(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
    if not brand:
        brand = BrandSetting(user_id=user.id)
        db.add(brand)
        db.commit()
        db.refresh(brand)

    ig = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
    pillars = db.query(ContentPillar).filter(ContentPillar.user_id == user.id).all()

    return {
        "user_id": user.id,
        "email": user.email,
        "brand_name": brand.brand_name,
        "tagline": brand.tagline,
        "niche": brand.niche,
        "primary_color": brand.primary_color,
        "background_color": brand.background_color,
        "text_color": brand.text_color,
        "secondary_color": brand.secondary_color,
        "posting_time": brand.posting_time,
        "timezone": brand.timezone,
        "active_days": brand.active_days or ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
        "posts_per_day": brand.posts_per_day,
        "ai_provider": brand.ai_provider,
        "auto_mode_enabled": brand.auto_mode_enabled,
        "content_strategy": brand.content_strategy or {},
        "instagram": {
            "connected": bool(ig and ig.access_token),
            "page_name": ig.page_name if ig else None,
            "connected_at": ig.connected_at.isoformat() if ig and ig.connected_at else None,
            "token_expires_at": ig.token_expires_at.isoformat() if ig and ig.token_expires_at else None,
        },
        "pillars": [
            {"id": p.id, "name": p.name, "percentage": p.percentage, "description": p.description}
            for p in pillars
        ],
    }


@router.put("")
def update_settings(
    req: SettingsUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
    if not brand:
        brand = BrandSetting(user_id=user.id)
        db.add(brand)

    if req.primary_color is not None:
        brand.primary_color = req.primary_color
    if req.background_color is not None:
        brand.background_color = req.background_color
    if req.text_color is not None:
        brand.text_color = req.text_color
    if req.secondary_color is not None:
        brand.secondary_color = req.secondary_color
    if req.brand_name is not None:
        brand.brand_name = req.brand_name
    if req.tagline is not None:
        brand.tagline = req.tagline
    if req.niche is not None:
        brand.niche = req.niche
    if req.posting_time is not None:
        brand.posting_time = req.posting_time
    if req.timezone is not None:
        brand.timezone = req.timezone
    if req.active_days is not None:
        brand.active_days = req.active_days
    if req.ai_provider is not None:
        brand.ai_provider = req.ai_provider
    if req.auto_mode_enabled is not None:
        brand.auto_mode_enabled = req.auto_mode_enabled
    if req.posts_per_day is not None and req.posts_per_day in (1, 2, 3):
        brand.posts_per_day = req.posts_per_day

    if req.pillars is not None:
        # Update or recreate content pillars
        db.query(ContentPillar).filter(ContentPillar.user_id == user.id).delete()
        for p in req.pillars:
            db.add(ContentPillar(
                user_id=user.id,
                name=p.name,
                percentage=p.percentage,
                description=p.description,
            ))

    db.commit()
    return {"success": True, "message": "Settings saved successfully."}


@router.post("/instagram/connect")
def connect_instagram():
    """Generates Meta OAuth flow URL."""
    auth_url = instagram_service.get_auth_url()
    return {"auth_url": auth_url}


@router.get("/instagram/callback")
def instagram_callback(
    code: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handles OAuth redirect from Meta, stores long-lived token."""
    try:
        token_info = instagram_service.exchange_code_for_token(code)
        ig = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
        if not ig:
            ig = InstagramAccount(user_id=user.id)
            db.add(ig)

        ig.access_token = token_info["access_token"]
        ig.token_expires_at = token_info["expires_at"]
        ig.page_name = "PromptPulse AI Feed"
        ig.connected_at = datetime.utcnow()
        db.commit()

        # Redirect back to frontend settings page with success
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings?instagram=connected")
    except Exception as e:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings?error={str(e)}")
