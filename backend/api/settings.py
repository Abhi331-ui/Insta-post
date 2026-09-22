import re
from datetime import datetime, timedelta
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
from backend.services.telegram import telegram_service

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
    posting_times: Optional[List[str]] = None  # Array of HH:MM strings, one per posting slot
    timezone: Optional[str] = None
    active_days: Optional[List[str]] = None
    ai_provider: Optional[str] = None
    auto_mode_enabled: Optional[bool] = None
    posts_per_day: Optional[int] = None
    pillars: Optional[List[PillarUpdate]] = None


class ExchangeCodeRequest(BaseModel):
    code: str


class ManualInstagramConnectRequest(BaseModel):
    instagram_user_id: str
    access_token: str
    page_name: Optional[str] = "PromptPulse AI Feed"


class TelegramConnectRequest(BaseModel):
    chat_id: str
    bot_token: Optional[str] = None


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

    # Ensure posting_times and active_days are always clean Python lists
    effective_posting_times = brand.posting_times or [brand.posting_time or "09:00"]
    if isinstance(effective_posting_times, str):
        try:
            import json
            effective_posting_times = json.loads(effective_posting_times)
        except Exception:
            effective_posting_times = [brand.posting_time or "09:00"]
    if not isinstance(effective_posting_times, list):
        effective_posting_times = [brand.posting_time or "09:00"]

    effective_active_days = brand.active_days or ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    if isinstance(effective_active_days, str):
        try:
            import json
            effective_active_days = json.loads(effective_active_days)
        except Exception:
            effective_active_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    if not isinstance(effective_active_days, list):
        effective_active_days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    # Fetch/update Instagram username if connected and not yet cached
    ig_username = ig.username if ig else None
    ig_pic = ig.profile_picture_url if ig else None
    if ig and ig.access_token and not ig_username:
        try:
            profile_data = instagram_service.get_account_profile(
                access_token=ig.access_token,
                instagram_user_id=ig.instagram_user_id,
            )
            if profile_data.get("username"):
                ig.username = profile_data["username"]
                ig.profile_picture_url = profile_data.get("profile_picture_url")
                if profile_data.get("name") and not ig.page_name:
                    ig.page_name = profile_data["name"]
                db.commit()
                ig_username = ig.username
                ig_pic = ig.profile_picture_url
        except Exception:
            pass

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
        "posting_times": effective_posting_times,
        "timezone": brand.timezone,
        "active_days": effective_active_days,
        "posts_per_day": brand.posts_per_day,
        "ai_provider": brand.ai_provider,
        "auto_mode_enabled": brand.auto_mode_enabled,
        "content_strategy": brand.content_strategy or {},
        "instagram": {
            "connected": bool(ig and ig.access_token),
            "username": ig_username,
            "profile_picture_url": ig_pic,
            "page_name": ig.page_name if ig else None,
            "connected_at": ig.connected_at.isoformat() if ig and ig.connected_at else None,
            "token_expires_at": ig.token_expires_at.isoformat() if ig and ig.token_expires_at else None,
            "instagram_user_id": ig.instagram_user_id if ig else None,
            "meta_app_id_configured": bool(settings.META_APP_ID and settings.META_APP_SECRET),
        },
        "telegram": {
            "connected": bool(brand.telegram_connected and brand.telegram_chat_id),
            "chat_id": brand.telegram_chat_id,
            "bot_username": settings.TELEGRAM_BOT_USERNAME or (telegram_service.get_bot_username() if telegram_service.is_configured() else None),
            "configured": telegram_service.is_configured() or bool(brand.telegram_bot_token),
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

    # Handle posting_times: validate and persist the per-slot time array
    if req.posting_times is not None:
        hhmm_re = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
        valid_times = []
        for t in req.posting_times:
            t = t.strip()
            if not hhmm_re.match(t):
                raise HTTPException(status_code=400, detail=f"Invalid time format '{t}'. Use HH:MM (24-hour).")
            valid_times.append(t)
        if len(valid_times) != len(set(valid_times)):
            raise HTTPException(status_code=400, detail="Each posting time must be unique. Remove duplicate times.")
        expected_count = req.posts_per_day if req.posts_per_day is not None else brand.posts_per_day
        if len(valid_times) != expected_count:
            raise HTTPException(
                status_code=400,
                detail=f"Number of posting times ({len(valid_times)}) must match posts per day ({expected_count}).",
            )
        brand.posting_times = valid_times
        # Keep legacy posting_time synced with slot 0
        brand.posting_time = valid_times[0]
    elif req.posting_time is not None:
        # Legacy single-time update: also update posting_times[0]
        current_times = brand.posting_times or [brand.posting_time or "09:00"]
        current_times[0] = req.posting_time
        brand.posting_times = current_times

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
    if not settings.META_APP_ID or not settings.META_APP_SECRET:
        raise HTTPException(
            status_code=400,
            detail="META_APP_ID or META_APP_SECRET is not configured in .env. Please configure your Meta credentials or connect using Manual/Test mode.",
        )
    auth_url = instagram_service.get_auth_url()
    return {"auth_url": auth_url}


@router.post("/instagram/exchange-code")
def exchange_instagram_code(
    req: ExchangeCodeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Exchanges OAuth code for long-lived access token and links Instagram account."""
    try:
        token_info = instagram_service.exchange_code_for_token(req.code)
        ig = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
        if not ig:
            ig = InstagramAccount(user_id=user.id)
            db.add(ig)

        ig.access_token = token_info["access_token"]
        ig.token_expires_at = token_info["expires_at"]
        if token_info.get("instagram_user_id"):
            ig.instagram_user_id = token_info["instagram_user_id"]
        if token_info.get("page_name"):
            ig.page_name = token_info["page_name"]
        if token_info.get("username"):
            ig.username = token_info["username"]
        if token_info.get("profile_picture_url"):
            ig.profile_picture_url = token_info["profile_picture_url"]
        ig.connected_at = datetime.utcnow()
        db.commit()

        return {"success": True, "message": "Instagram connected successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/instagram/manual")
def connect_instagram_manual(
    req: ManualInstagramConnectRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually connects Instagram using User ID and Access Token."""
    if not req.instagram_user_id.strip() or not req.access_token.strip():
        raise HTTPException(status_code=400, detail="Instagram User ID and Access Token are required.")

    ig = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
    if not ig:
        ig = InstagramAccount(user_id=user.id)
        db.add(ig)

    ig.instagram_user_id = req.instagram_user_id.strip()
    ig.access_token = req.access_token.strip()
    ig.page_name = req.page_name or "PromptPulse AI Feed"
    ig.token_expires_at = datetime.utcnow() + timedelta(days=60)
    ig.connected_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Instagram account connected successfully."}


@router.post("/instagram/test-connect")
def connect_instagram_test(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Connect a simulated test Instagram Business account for testing."""
    ig = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
    if not ig:
        ig = InstagramAccount(user_id=user.id)
        db.add(ig)

    ig.instagram_user_id = "test_instagram_business_id"
    ig.access_token = "test_long_lived_access_token_promptpulse"
    ig.page_name = "PromptPulse AI (Simulated Business Feed)"
    ig.token_expires_at = datetime.utcnow() + timedelta(days=60)
    ig.connected_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Simulated Instagram Business account connected!"}


@router.post("/instagram/disconnect")
def disconnect_instagram(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disconnects the linked Instagram account."""
    ig = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
    if ig:
        db.delete(ig)
        db.commit()
    return {"success": True, "message": "Instagram account disconnected."}


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
        if token_info.get("instagram_user_id"):
            ig.instagram_user_id = token_info["instagram_user_id"]
        if token_info.get("page_name"):
            ig.page_name = token_info["page_name"]
        if token_info.get("username"):
            ig.username = token_info["username"]
        if token_info.get("profile_picture_url"):
            ig.profile_picture_url = token_info["profile_picture_url"]
        ig.connected_at = datetime.utcnow()
        db.commit()

        # Redirect back to frontend settings page with success
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings?instagram=connected")
    except Exception as e:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/settings?error={str(e)}")


@router.post("/telegram/connect")
def connect_telegram(
    req: TelegramConnectRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifies Telegram chat ID and connects Telegram notifications."""
    chat_id = req.chat_id.strip()
    if not chat_id:
        raise HTTPException(status_code=400, detail="Telegram Chat ID is required.")

    brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
    if not brand:
        brand = BrandSetting(user_id=user.id)
        db.add(brand)

    token_to_use = req.bot_token.strip() if req.bot_token else brand.telegram_bot_token

    # Verify connection by sending welcome test message
    res = telegram_service.verify_chat(chat_id=chat_id, bot_token=token_to_use)
    if not res.get("ok"):
        err = res.get("description", "Could not reach Telegram chat. Please make sure you sent /start to the bot first.")
        raise HTTPException(status_code=400, detail=f"Telegram verification failed: {err}")

    brand.telegram_chat_id = chat_id
    if req.bot_token:
        brand.telegram_bot_token = req.bot_token.strip()
    brand.telegram_connected = True
    db.commit()

    return {"success": True, "message": "Telegram connected and verification message sent!"}


@router.post("/telegram/disconnect")
def disconnect_telegram(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disconnects Telegram notifications."""
    brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
    if brand:
        brand.telegram_connected = False
        brand.telegram_chat_id = None
        brand.telegram_bot_token = None
        db.commit()
    return {"success": True, "message": "Telegram disconnected."}


@router.post("/telegram/test")
def test_telegram(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sends a test message to the user's connected Telegram chat."""
    brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
    if not brand or not brand.telegram_connected or not brand.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram is not connected. Please connect your Chat ID first.")

    res = telegram_service.send_message(
        chat_id=brand.telegram_chat_id,
        text=(
            "🧪 <b>Test Notification from PromptPulse</b>\n\n"
            "Your Telegram alerts are active and running properly! "
            "You will receive queue refill reminders and post-publish confirmations here. 🚀"
        ),
        bot_token=brand.telegram_bot_token,
    )
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=f"Failed to send test message: {res.get('description')}")

    return {"success": True, "message": "Test notification sent to Telegram!"}

