import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.models.user import BrandSetting
from backend.models.post import Post, ScheduledPost

logger = logging.getLogger("PromptPulse.SchedulerService")


class SchedulerService:
    def schedule_post(self, post_id: int, target_time: datetime, db: Session) -> ScheduledPost:
        """Schedules a post for automatic publication at target_time."""
        existing = db.query(ScheduledPost).filter(ScheduledPost.post_id == post_id).first()
        if existing:
            existing.scheduled_time = target_time
            existing.status = "pending"
            existing.is_published = False
            db.commit()
            return existing

        sched = ScheduledPost(
            post_id=post_id,
            scheduled_time=target_time,
            status="pending",
            is_published=False,
        )
        db.add(sched)

        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post.status = "scheduled"
            post.scheduled_at = target_time

        db.commit()
        return sched

    def update_user_schedule_settings(
        self,
        user_id: int,
        posting_time: str,
        timezone: str,
        active_days: list,
        db: Session,
    ) -> Dict[str, Any]:
        """Updates user's preferred daily posting hour and active days."""
        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
        if not brand:
            brand = BrandSetting(user_id=user_id)
            db.add(brand)

        brand.posting_time = posting_time
        brand.timezone = timezone
        brand.active_days = active_days
        db.commit()

        return {
            "posting_time": brand.posting_time,
            "timezone": brand.timezone,
            "active_days": brand.active_days,
        }


scheduler_service = SchedulerService()
