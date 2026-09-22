import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.user import User, BrandSetting
from backend.models.post import Post, ScheduledPost
from backend.models.queue import TopicQueueItem
from backend.api.auth import get_current_user
from backend.pipeline.daily_pipeline import daily_pipeline

router = APIRouter(prefix="/api/queue", tags=["queue"])


class BatchQueueRequest(BaseModel):
    topics: List[str]
    start_date: Optional[str] = None  # YYYY-MM-DD format (defaults to tomorrow)
    posts_per_day: Optional[int] = 1  # 1, 2, or 3 posts per day


async def generate_post_for_queue_item(item_id: int, user_id: int, topic: str, scheduled_time: datetime):
    """Background worker that generates the carousel and links it to the queue item."""
    from backend.database import SessionLocal
    db = SessionLocal()
    try:
        item = db.query(TopicQueueItem).filter(TopicQueueItem.id == item_id).first()
        if not item:
            return

        item.status = "generating"
        db.commit()

        # Run pipeline with custom topic
        res = await daily_pipeline.run_daily_pipeline(user_id=user_id, custom_topic=topic, db=db)
        if res.get("status") == "success" and "post_id" in res:
            post_id = res["post_id"]
            item.post_id = post_id
            item.status = "ready"

            post = db.query(Post).filter(Post.id == post_id).first()
            if post:
                post.status = "scheduled"
                post.scheduled_at = scheduled_time

                # Create or update ScheduledPost
                sched = db.query(ScheduledPost).filter(ScheduledPost.post_id == post_id).first()
                if not sched:
                    sched = ScheduledPost(
                        post_id=post.id,
                        scheduled_time=scheduled_time,
                        status="pending",
                        is_published=False,
                    )
                    db.add(sched)
                else:
                    sched.scheduled_time = scheduled_time
                    sched.status = "pending"
                    sched.is_published = False

            db.commit()
        else:
            item.status = "failed"
            db.commit()
    except Exception as e:
        item = db.query(TopicQueueItem).filter(TopicQueueItem.id == item_id).first()
        if item:
            item.status = "failed"
            db.commit()
    finally:
        db.close()


@router.post("/batch")
async def submit_topic_batch(
    req: BatchQueueRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accepts up to 10 trending topics, schedules them across consecutive calendar days,
    and initiates autonomous carousel generation.
    """
    clean_topics = [t.strip() for t in req.topics if t and t.strip()]
    if not clean_topics:
        raise HTTPException(status_code=400, detail="Please provide at least 1 trending topic.")
    if len(clean_topics) > 10:
        clean_topics = clean_topics[:10]

    # Fetch user's preferred daily posting hour
    brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
    posting_time_str = brand.posting_time if brand and brand.posting_time else "09:00"
    try:
        post_hour, post_minute = map(int, posting_time_str.split(":"))
    except Exception:
        post_hour, post_minute = 9, 0

    # Determine base start date
    now = datetime.utcnow()
    if req.start_date:
        try:
            parsed = datetime.strptime(req.start_date, "%Y-%m-%d")
            base_date = datetime(parsed.year, parsed.month, parsed.day, post_hour, post_minute)
        except Exception:
            base_date = (now + timedelta(days=1)).replace(hour=post_hour, minute=post_minute, second=0, microsecond=0)
    else:
        # Defaults to tomorrow morning at posting time
        base_date = (now + timedelta(days=1)).replace(hour=post_hour, minute=post_minute, second=0, microsecond=0)

    posts_per_day = req.posts_per_day or 1
    if posts_per_day not in (1, 2, 3):
        posts_per_day = 1

    # Use user-configured posting times from BrandSetting, falling back to optimal defaults
    user_posting_times = brand.posting_times if brand and brand.posting_times else None
    if isinstance(user_posting_times, str):
        try:
            import json
            user_posting_times = json.loads(user_posting_times)
        except Exception:
            user_posting_times = None
    if user_posting_times and isinstance(user_posting_times, list) and len(user_posting_times) >= posts_per_day:
        slot_hours = []
        for t in user_posting_times[:posts_per_day]:
            try:
                h, m = map(int, t.split(":"))
                slot_hours.append((h, m))
            except Exception:
                slot_hours.append((post_hour, post_minute))
    else:
        # Optimal Instagram time slot defaults:
        # 1 post / day:  [user's primary time] (Morning prime)
        # 2 posts / day: [user's primary time, 18:00] (Morning & Evening prime)
        # 3 posts / day: [user's primary time, 13:00, 20:00] (Morning, Lunchtime, Evening prime)
        if posts_per_day == 1:
            slot_hours = [(post_hour, post_minute)]
        elif posts_per_day == 2:
            slot_hours = [(post_hour, post_minute), (18, 0)]
        elif posts_per_day == 3:
            slot_hours = [(post_hour, post_minute), (13, 0), (20, 0)]
        else:
            slot_hours = [(post_hour, post_minute)]

    batch_id = f"batch_{int(now.timestamp())}_{uuid.uuid4().hex[:6]}"
    created_items = []

    for idx, topic in enumerate(clean_topics):
        day_offset = idx // posts_per_day
        slot_idx = idx % posts_per_day
        slot_h, slot_m = slot_hours[slot_idx]
        target_day = base_date + timedelta(days=day_offset)
        scheduled_time = target_day.replace(hour=slot_h, minute=slot_m, second=0, microsecond=0)

        queue_item = TopicQueueItem(
            user_id=user.id,
            batch_id=batch_id,
            topic=topic,
            scheduled_date=scheduled_time,
            day_index=day_offset + 1,
            status="pending",
        )
        db.add(queue_item)
        db.flush()
        created_items.append({
            "id": queue_item.id,
            "topic": topic,
            "day_index": day_offset + 1,
            "slot_index": slot_idx + 1,
            "scheduled_date": scheduled_time.isoformat(),
        })

    db.commit()

    # Launch background generation for each queued topic
    for item in created_items:
        background_tasks.add_task(
            generate_post_for_queue_item,
            item_id=item["id"],
            user_id=user.id,
            topic=item["topic"],
            scheduled_time=datetime.fromisoformat(item["scheduled_date"]),
        )

    return {
        "success": True,
        "batch_id": batch_id,
        "count": len(clean_topics),
        "start_date": base_date.isoformat(),
        "items": created_items,
        "message": f"Successfully queued {len(clean_topics)} topics across consecutive days. Generation started.",
    }


@router.get("")
def get_queue(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns current active queue items, scheduled dates, statuses,
    and 5-day refill countdown indicator.
    """
    items = (
        db.query(TopicQueueItem)
        .filter(TopicQueueItem.user_id == user.id)
        .order_by(TopicQueueItem.scheduled_date.asc())
        .all()
    )

    now = datetime.utcnow()
    future_items = [it for it in items if it.scheduled_date >= now or it.status != "published"]

    # Calculate days of coverage
    days_covered = len(future_items)
    # Refill rule: every 5 days, recommend refilling when coverage drops below 5 days
    refill_due_in = max(0, min(5, days_covered - 5)) if days_covered > 5 else 0

    serialized = []
    for it in items:
        img_url = None
        post_status = None
        hook = None
        pillar = "AI Workflows & Automation"
        slides_list = []
        if it.post:
            post_status = it.post.status
            hook = it.post.hook
            pillar = it.post.content_pillar or pillar
            if it.post.slides:
                for s in sorted(it.post.slides, key=lambda x: x.slide_number):
                    if s.image_path:
                        if s.image_path.startswith(("http://", "https://", "data:")):
                            slide_img_url = s.image_path
                        else:
                            fn = Path(s.image_path).name
                            slide_img_url = f"{settings.PUBLIC_MEDIA_BASE_URL}/slides/{fn}"
                        slides_list.append({
                            "slide_number": s.slide_number,
                            "headline": s.headline,
                            "layout_type": s.layout_type,
                            "image_url": slide_img_url,
                        })
                if slides_list:
                    img_url = slides_list[0]["image_url"]

        serialized.append({
            "id": it.id,
            "batch_id": it.batch_id,
            "topic": it.topic,
            "day_index": it.day_index,
            "scheduled_date": it.scheduled_date.isoformat(),
            "date_display": it.scheduled_date.strftime("%b %d, %Y"),
            "time_display": it.scheduled_date.strftime("%I:%M %p"),
            "status": it.status,
            "post_id": it.post_id,
            "post_status": post_status,
            "hook": hook,
            "content_pillar": pillar,
            "preview_image_url": img_url,
            "slides_count": len(slides_list),
            "slides": slides_list,
            "created_at": it.created_at.isoformat(),
        })

    return {
        "items": serialized,
        "stats": {
            "total_queued": len(future_items),
            "days_covered": days_covered,
            "refill_due_in_days": refill_due_in,
            "refill_recommended": days_covered <= 5,
        },
    }


@router.delete("/{item_id}")
def delete_queue_item(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Removes a queued topic and cancels its scheduled publication."""
    item = db.query(TopicQueueItem).filter(
        TopicQueueItem.id == item_id,
        TopicQueueItem.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found.")

    if item.post:
        item.post.status = "cancelled"
        sched = db.query(ScheduledPost).filter(ScheduledPost.post_id == item.post.id).first()
        if sched:
            sched.status = "cancelled"

    db.delete(item)
    db.commit()
    return {"success": True, "message": f"Topic '{item.topic}' removed from queue."}


@router.post("/{item_id}/generate")
async def generate_single_queue_item(
    item_id: int,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually triggers generation or re-generation for an individual queued topic."""
    item = db.query(TopicQueueItem).filter(
        TopicQueueItem.id == item_id,
        TopicQueueItem.user_id == user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found.")

    background_tasks.add_task(
        generate_post_for_queue_item,
        item_id=item.id,
        user_id=user.id,
        topic=item.topic,
        scheduled_time=item.scheduled_date,
    )

    return {"success": True, "message": f"Generation started for '{item.topic}'."}
