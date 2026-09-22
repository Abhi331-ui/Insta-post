from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import secrets
import io
import requests
from PIL import Image

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
    notes: Optional[str] = None
    hook: Optional[str] = None
    tone: Optional[str] = None
    dm_keyword: Optional[str] = None


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
            if s.image_path.startswith(("http://", "https://", "data:")):
                img_url = s.image_path
            else:
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
        "share_token": post.share_token,
        "share_url": f"{settings.FRONTEND_URL}/review/{post.share_token}" if post.share_token else None,
        "dm_keyword": post.dm_keyword,
        "dm_message": post.dm_message,
        "client_feedback": post.client_feedback,
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

    # Trigger everyday learning
    try:
        from backend.agents.learning_agent import learning_agent
        import asyncio
        asyncio.create_task(learning_agent.learn_from_post_event(user.id, post.id, "approved", None, db))
    except Exception:
        pass

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

    # Trigger everyday learning
    try:
        from backend.agents.learning_agent import learning_agent
        import asyncio
        asyncio.create_task(learning_agent.learn_from_post_event(user.id, post.id, "rejected", None, db))
    except Exception:
        pass

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
    from backend.services.image_generator import image_generator
    new_img = await design_agent.regenerate_single_slide(
        {"headline": slide.headline, "body_text": slide.body_text, "layout_type": slide.layout_type},
        post_id=post.id,
        slide_number=slide_number,
        brand_settings=brand_dict,
    )
    slide.image_path = image_generator.get_public_url(post_id=post.id, slide_number=slide_number) or new_img
    db.commit()

    return {"success": True, "slide_number": slide_number, "headline": slide.headline, "body_text": slide.body_text}


@router.post("/create-post")
async def create_post(
    req: CreatePostRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """Manual post creation triggered with custom user topic and preferences."""
    background_tasks.add_task(
        daily_pipeline.run_daily_pipeline,
        user_id=user.id,
        custom_topic=req.topic,
        custom_pillar=req.content_pillar,
        custom_audience=req.target_audience,
        custom_notes=req.notes,
        custom_hook=req.hook,
        custom_tone=req.tone,
        custom_dm_keyword=req.dm_keyword,
    )
    return {"success": True, "message": f"Autonomous pipeline initiated for topic: '{req.topic}'."}


class DraftSixSlotsRequest(BaseModel):
    topic: str
    tone: Optional[str] = "Technical Deep Dive"
    notes: Optional[str] = None
    dm_keyword: Optional[str] = None


class CustomSlideSlotInput(BaseModel):
    slide_number: int
    layout_type: str = "hero_editorial"
    category: Optional[str] = None
    headline_prefix: Optional[str] = None
    headline_highlight: Optional[str] = None
    headline: Optional[str] = None
    body_text: Optional[str] = None
    annotation: Optional[str] = None
    feature_pills: Optional[List[Dict[str, Any]]] = None
    features: Optional[List[Dict[str, Any]]] = None
    grid_cards: Optional[List[Dict[str, Any]]] = None
    flow_steps: Optional[List[str]] = None
    steps: Optional[List[Dict[str, Any]]] = None
    mockup_prompt: Optional[str] = None
    rows: Optional[List[Dict[str, Any]]] = None
    benefits: Optional[List[Dict[str, Any]]] = None
    dm_keyword: Optional[str] = None
    dm_message: Optional[str] = None
    cta_button_text: Optional[str] = None
    tagline_left: Optional[str] = None
    tagline_right: Optional[str] = None
    tool_name_prefix: Optional[str] = None
    tool_name: Optional[str] = None
    tool_badge: Optional[str] = None
    eyebrow: Optional[str] = None
    prompt_instruction: Optional[str] = None


class CreateCustomSlidesPostRequest(BaseModel):
    topic: str
    content_pillar: Optional[str] = "AI Workflows & Automation"
    target_audience: Optional[List[str]] = None
    tone: Optional[str] = "Technical Deep Dive"
    slides: List[CustomSlideSlotInput]


class DirectivesRequest(BaseModel):
    directives: List[str]


@router.post("/draft-6-slots")
async def draft_six_slots(
    req: DraftSixSlotsRequest,
    user: User = Depends(get_current_user),
):
    """Drafts complete content for all 6 slots so the user can customize them individually."""
    opp = {
        "topic": req.topic,
        "selected_angle": req.tone or "Technical Deep Dive",
        "hook": f"Stop doing this manually. {req.topic} changes everything.",
        "why_today": f"Latest breakthrough and essential workflows for {req.topic}.",
        "content_pillar": "AI Workflows & Automation",
        "target_audience": ["creators", "developers", "AI power-users"],
        "notes": req.notes or "",
        "tone": req.tone or "Technical Deep Dive",
        "dm_keyword": req.dm_keyword or "",
        "sources": ["https://promptpulse.ai"],
    }
    from backend.agents.content_agent import content_agent
    slides = await content_agent.write_carousel(opp)
    return {"success": True, "topic": req.topic, "slides": slides}


@router.post("/create-custom-slides-post")
async def create_custom_slides_post(
    req: CreateCustomSlidesPostRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a post from the user's custom 6-slot slide definitions."""
    topic = req.topic.strip()
    slide_1 = req.slides[0] if req.slides else None
    hook = (slide_1.headline if slide_1 else None) or f"Mastering {topic}"
    slide_6 = req.slides[5] if len(req.slides) >= 6 else None
    dm_kw = (slide_6.dm_keyword if slide_6 else None) or "GUIDE"

    post = Post(
        user_id=user.id,
        topic=topic,
        hook=hook,
        angle=req.tone or "Custom 6-Slot Studio",
        freshness_category="CUSTOM",
        content_pillar=req.content_pillar or "AI Workflows & Automation",
        why_today_reason=f"Custom 6-slot creation for {topic}.",
        target_audience=req.target_audience or ["creators", "developers"],
        caption=f"Here is how to master {topic} in 6 simple steps.\n\nComment \"{dm_kw}\" to get the full free resource pack!\n\n#aitools #productivity #workflow",
        hashtags="#aitools #productivity #workflow",
        alt_text=f"6-slide carousel breakdown of {topic}.",
        dm_keyword=dm_kw,
        dm_message=f"Hey! Here is your free {topic} resource pack: https://promptpulse.ai/toolkit - enjoy!",
        status="generating",
        sources=["https://promptpulse.ai"],
        scores={"composite_score": 9.5},
        created_at=datetime.utcnow(),
    )
    db.add(post)
    db.commit()

    slides_data = []
    for s in req.slides:
        slide_dict = s.dict(exclude_none=True)
        if not slide_dict.get("layout_type"):
            expected = ["hero_editorial", "tool_card", "showcase", "steps", "comparison", "cta"]
            slide_dict["layout_type"] = expected[min(s.slide_number - 1, 5)]

        headline = slide_dict.get("headline")
        if not headline:
            prefix = slide_dict.get("headline_prefix", "")
            highlight = slide_dict.get("headline_highlight", "")
            headline = f"{prefix} {highlight}".strip() or f"Slide {s.slide_number}"
            slide_dict["headline"] = headline

        ps = PostSlide(
            post_id=post.id,
            slide_number=s.slide_number,
            layout_type=slide_dict.get("layout_type", "hero_editorial"),
            headline=headline,
            body_text=slide_dict.get("body_text", ""),
            image_path="",
        )
        db.add(ps)
        slides_data.append(slide_dict)

    db.commit()

    async def _render_slides():
        from backend.database import SessionLocal
        from backend.agents.design_agent import design_agent
        from backend.services.image_generator import image_generator
        from backend.models.user import BrandSetting
        r_db = SessionLocal()
        try:
            r_post = r_db.query(Post).filter(Post.id == post.id).first()
            brand = r_db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
            brand_dict = {
                "primary_color": brand.primary_color if brand else "#2563EB",
                "background_color": brand.background_color if brand else "#F8FAFC",
                "text_color": brand.text_color if brand else "#0F172A",
                "secondary_color": brand.secondary_color if brand else "#64748B",
                "brand_name": brand.brand_name if brand else "PromptPulse",
            }
            for s_dict in slides_data:
                s_num = s_dict.get("slide_number", 1)
                img_path = await design_agent.regenerate_single_slide(
                    s_dict,
                    post_id=r_post.id,
                    slide_number=s_num,
                    brand_settings=brand_dict,
                )
                db_slide = r_db.query(PostSlide).filter(
                    PostSlide.post_id == r_post.id,
                    PostSlide.slide_number == s_num,
                ).first()
                if db_slide:
                    db_slide.image_path = image_generator.get_public_url(post_id=r_post.id, slide_number=s_num) or img_path

            r_post.status = "pending_approval"
            r_db.commit()

            # Trigger everyday incremental learning
            try:
                from backend.agents.learning_agent import learning_agent
                await learning_agent.learn_from_post_event(user.id, r_post.id, "created", None, r_db)
            except Exception:
                pass
        finally:
            r_db.close()

    background_tasks.add_task(_render_slides)
    return {"success": True, "post_id": post.id, "message": f"6-slot carousel creation started for '{topic}'."}


@router.get("/agent/brain")
def get_agent_brain_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns the agent's learned guidelines, winning hooks, and custom directives."""
    from backend.agents.learning_agent import learning_agent
    return learning_agent.get_agent_brain(user.id, db)


@router.post("/agent/directives")
def update_agent_directives(
    req: DirectivesRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates user-defined directives/rules for the agent to follow."""
    from backend.agents.learning_agent import learning_agent
    return learning_agent.update_custom_directives(user.id, req.directives, db)


class ReviewActionRequest(BaseModel):
    action: str  # "approve" or "request_changes"
    feedback: Optional[str] = None


@router.post("/posts/{post_id}/share-link")
def generate_or_get_share_link(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generates or retrieves a magic review link for sharing with clients."""
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    if not post.share_token:
        post.share_token = secrets.token_urlsafe(18)
        db.commit()

    share_url = f"{settings.FRONTEND_URL}/review/{post.share_token}"
    return {
        "success": True,
        "share_token": post.share_token,
        "share_url": share_url,
    }


@router.get("/posts/public/review/{token}")
def get_public_post_review(
    token: str,
    db: Session = Depends(get_db),
):
    """Public endpoint: returns carousel preview for client review without login."""
    post = db.query(Post).filter(Post.share_token == token).first()
    if not post:
        raise HTTPException(status_code=404, detail="Review link not found or expired.")

    return serialize_post(post)


@router.post("/posts/public/review/{token}/action")
def submit_public_review_action(
    token: str,
    req: ReviewActionRequest,
    db: Session = Depends(get_db),
):
    """Public endpoint: client can approve or request changes with feedback."""
    post = db.query(Post).filter(Post.share_token == token).first()
    if not post:
        raise HTTPException(status_code=404, detail="Review link not found or expired.")

    if req.action == "approve":
        post.status = "scheduled" if post.scheduled_at else "approved"
        post.client_feedback = req.feedback or "Approved by client"
        msg = "Carousel approved! It will publish at the scheduled time."
    elif req.action == "request_changes":
        post.status = "needs_changes"
        post.client_feedback = req.feedback or "Changes requested"
        msg = "Feedback received. Our team will update the carousel shortly."
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'request_changes'.")

    db.commit()
    return {"success": True, "status": post.status, "message": msg}


def _build_pdf_from_post(post: Post) -> io.BytesIO:
    """Helper to compile post slides into an in-memory PDF."""
    sorted_slides = sorted(post.slides, key=lambda x: x.slide_number)
    if not sorted_slides:
        raise HTTPException(status_code=400, detail="This post has no slides to export.")

    images: List[Image.Image] = []
    for s in sorted_slides:
        img = None
        # 1. Try local file path
        if s.image_path and Path(s.image_path).exists():
            try:
                img = Image.open(s.image_path).convert("RGB")
            except Exception:
                img = None

        # 2. Try URL if local path not found
        if not img and s.image_path:
            url = s.image_path
            if not url.startswith(("http://", "https://")):
                filename = Path(s.image_path).name
                url = f"{settings.PUBLIC_MEDIA_BASE_URL}/slides/{filename}"
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    img = Image.open(io.BytesIO(r.content)).convert("RGB")
            except Exception:
                img = None

        if img:
            images.append(img)

    if not images:
        raise HTTPException(status_code=400, detail="Could not load slide images for PDF export.")

    pdf_buffer = io.BytesIO()
    images[0].save(
        pdf_buffer,
        format="PDF",
        save_all=True,
        append_images=images[1:],
        resolution=150.0,
    )
    pdf_buffer.seek(0)
    return pdf_buffer


@router.get("/posts/{post_id}/export-pdf")
def export_post_as_pdf(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Exports all 6 carousel slides as a single high-resolution PDF for LinkedIn Document carousel."""
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    pdf_buffer = _build_pdf_from_post(post)
    clean_topic = "".join(c for c in post.topic if c.isalnum() or c in (" ", "_", "-")).rstrip()[:30]
    filename = f"carousel_{post_id}_{clean_topic.replace(' ', '_')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )


@router.get("/posts/public/review/{token}/export-pdf")
def export_public_post_as_pdf(
    token: str,
    db: Session = Depends(get_db),
):
    """Public export endpoint for clients reviewing the carousel."""
    post = db.query(Post).filter(Post.share_token == token).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    pdf_buffer = _build_pdf_from_post(post)
    clean_topic = "".join(c for c in post.topic if c.isalnum() or c in (" ", "_", "-")).rstrip()[:30]
    filename = f"carousel_{post.id}_{clean_topic.replace(' ', '_')}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
    )
