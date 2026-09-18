from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.user import User
from backend.models.post import Post, PostSlide, ScheduledPost
from backend.api.auth import get_current_user
from backend.pipeline.daily_pipeline import daily_pipeline
from backend.agents.publishing_agent import publishing_agent
from backend.services.scheduler import scheduler_service

router = APIRouter(prefix="/api", tags=["posts"])


class CreatePostRequest(BaseModel):
    topic: str
    target_audience: Optional[List[str]] = None
    content_pillar: Optional[str] = None


class RescheduleRequest(BaseModel):
    scheduled_time: datetime
    timezone: Optional[str] = "UTC"


class UpdateCaptionRequest(BaseModel):
    caption: str
    hashtags: Optional[str] = None
    alt_text: Optional[str] = None


class UpdateSlideRequest(BaseModel):
    headline: Optional[str] = None
    body_text: Optional[str] = None


def serialize_post(post: Post) -> Dict[str, Any]:
    slides = []
    for s in sorted(post.slides, key=lambda x: x.slide_number):
        img_url = ""
        if s.image_path:
            filename = Path(s.image_path).name
            img_url = f"{settings.PUBLIC_MEDIA_BASE_URL}/slides/{filename}"

        slides.append({
            "id": s.id,
            "slide_number": s.slide_number,
            "headline": s.headline,
            "body_text": s.body_text,
            "layout_type": s.layout_type,
            "image_url": img_url,
            "regenerated_count": s.regenerated_count,
        })

    return {
        "id": post.id,
        "topic": post.topic,
        "hook": post.hook,
        "angle": post.angle,
        "freshness_category": post.freshness_category,
        "content_pillar": post.content_pillar,
        "why_today_reason": post.why_today_reason,
        "target_audience": post.target_audience or [],
        "caption": post.caption,
        "hashtags": post.hashtags,
        "alt_text": post.alt_text,
        "status": post.status,
        "instagram_post_id": post.instagram_post_id,
        "scheduled_at": post.scheduled_at.isoformat() if post.scheduled_at else None,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "sources": post.sources or [],
        "scores": post.scores or {},
        "slides": slides,
    }


@router.get("/posts")
def list_posts(
    status: Optional[str] = None,
    pillar: Optional[str] = None,
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Post).filter(Post.user_id == user.id)
    if status:
        query = query.filter(Post.status == status)
    if pillar:
        query = query.filter(Post.content_pillar == pillar)

    posts = query.order_by(Post.created_at.desc()).limit(limit).all()
    return [serialize_post(p) for p in posts]


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return serialize_post(post)


@router.post("/posts/{post_id}/approve")
def approve_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.status = "scheduled"
    if not post.scheduled_at:
        post.scheduled_at = datetime.utcnow()

    sched = db.query(ScheduledPost).filter(ScheduledPost.post_id == post.id).first()
    if not sched:
        sched = ScheduledPost(
            post_id=post.id,
            scheduled_time=post.scheduled_at,
            status="pending",
        )
        db.add(sched)
    else:
        sched.status = "pending"

    db.commit()
    return {"success": True, "status": post.status, "message": "Post approved for scheduled publication."}


@router.post("/posts/{post_id}/reject")
async def reject_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.status = "rejected"
    db.commit()

    # Trigger new autonomous discovery run in background
    background_tasks.add_task(daily_pipeline.run_daily_pipeline, user_id=user.id)
    return {"success": True, "message": "Post rejected. Autonomous discovery triggered for a fresh opportunity."}


@router.post("/posts/{post_id}/regenerate")
async def regenerate_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    topic = post.topic
    # Trigger regeneration using existing topic
    background_tasks.add_task(daily_pipeline.run_daily_pipeline, user_id=user.id, custom_topic=topic)
    return {"success": True, "message": f"Regenerating carousel for topic '{topic}'."}


@router.post("/posts/{post_id}/slides/{slide_number}/regenerate")
async def regenerate_single_slide(
    post_id: int,
    slide_number: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    res = await daily_pipeline.regenerate_single_slide_in_post(post_id, slide_number, db)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    return res


@router.post("/posts/{post_id}/publish-now")
async def publish_now(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    result = await publishing_agent.publish_to_instagram(post.id, db)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Publishing failed."))

    return result


@router.post("/posts/{post_id}/reschedule")
def reschedule_post(
    post_id: int,
    req: RescheduleRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    sched = scheduler_service.schedule_post(post.id, req.scheduled_time, db)
    return {"success": True, "scheduled_time": sched.scheduled_time.isoformat()}


@router.patch("/posts/{post_id}/caption")
def update_caption(
    post_id: int,
    req: UpdateCaptionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    post.caption = req.caption
    if req.hashtags is not None:
        post.hashtags = req.hashtags
    if req.alt_text is not None:
        post.alt_text = req.alt_text

    db.commit()
    return {"success": True, "caption": post.caption, "hashtags": post.hashtags}


@router.patch("/posts/{post_id}/slides/{slide_number}")
async def update_slide_text(
    post_id: int,
    slide_number: int,
    req: UpdateSlideRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    slide = db.query(PostSlide).filter(
        PostSlide.post_id == post_id,
        PostSlide.slide_number == slide_number,
    ).first()
    if not slide:
        raise HTTPException(status_code=404, detail=f"Slide {slide_number} not found.")

    if req.headline is not None:
        slide.headline = req.headline
    if req.body_text is not None:
        slide.body_text = req.body_text

    # Re-render the slide image with updated copy
    from backend.agents.design_agent import design_agent
    from backend.models.user import BrandSetting
    brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
    brand_dict = {
        "primary_color": brand.primary_color if brand else "#2563EB",
        "background_color": brand.background_color if brand else "#F8FAFC",
        "text_color": brand.text_color if brand else "#0F172A",
        "secondary_color": brand.secondary_color if brand else "#64748B",
        "brand_name": brand.brand_name if brand else "PromptPulse",
    }
    new_img = await design_agent.regenerate_single_slide(
        {"headline": slide.headline, "body_text": slide.body_text, "layout_type": slide.layout_type},
        post_id=post.id,
        slide_number=slide_number,
        brand_settings=brand_dict,
    )
    slide.image_path = new_img
    db.commit()

    return {"success": True, "slide_number": slide_number, "headline": slide.headline, "body_text": slide.body_text}


@router.post("/create-post")
async def create_post(
    req: CreatePostRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """Manual post creation triggered with custom user topic."""
    background_tasks.add_task(daily_pipeline.run_daily_pipeline, user_id=user.id, custom_topic=req.topic)
    return {"success": True, "message": f"Autonomous pipeline initiated for topic: '{req.topic}'."}
