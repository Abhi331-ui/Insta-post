import os
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.config import settings
from backend.services.instagram import instagram_service
from backend.models.post import Post, ScheduledPost, PublishingLog

logger = logging.getLogger("PromptPulse.PublishingAgent")


class PublishingAgent:
    def __init__(self):
        self.instagram = instagram_service

    async def publish_to_instagram(self, post_id: int, db: Session) -> Dict[str, Any]:
        """
        Executes idempotent publishing via Meta Graph API:
        1. Checks scheduled_posts.is_published flag
        2. Resolves public media URLs for all 6 slides
        3. Invokes 3-step carousel container publish
        4. Logs attempt details to publishing_logs
        5. Updates post status to published or failed
        """
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return {"success": False, "error": f"Post {post_id} not found."}

        sched = db.query(ScheduledPost).filter(ScheduledPost.post_id == post_id).first()
        if sched and sched.is_published:
            return {
                "success": True,
                "already_published": True,
                "instagram_post_id": post.instagram_post_id,
                "message": "Post was already published (idempotency guard triggered).",
            }

        # Resolve public Supabase URLs for each slide
        image_urls = []

        for slide in sorted(post.slides, key=lambda s: s.slide_number):
            if not slide.image_path:
                continue

            # image_path now contains the public Supabase Storage URL
            image_urls.append(slide.image_path)

        if len(image_urls) != 6:
            return {
                "success": False,
                "error": f"Post {post_id} has {len(image_urls)} slides ready. Expected exactly 6.",
            }

        caption_text = f"{post.caption}\n\n{post.hashtags}" if post.hashtags else post.caption

        # Resolve Instagram credentials: user connected account takes priority
        from backend.models.user import InstagramAccount
        from backend.services.instagram import InstagramService
        ig_acc = db.query(InstagramAccount).filter(InstagramAccount.user_id == post.user_id).first()
        if ig_acc and ig_acc.access_token and ig_acc.instagram_user_id:
            insta_svc = InstagramService(
                access_token=ig_acc.access_token,
                instagram_user_id=ig_acc.instagram_user_id,
            )
        else:
            insta_svc = self.instagram

        # Execute Instagram API publish
        result = await insta_svc.publish_carousel(
            image_urls=image_urls,
            caption=caption_text or "",
            max_retries=3,
        )

        # Log attempt in DB
        log_entry = PublishingLog(
            post_id=post_id,
            attempt_number=result.get("attempt_count", 1),
            status="success" if result.get("success") else "failed",
            error_message=result.get("error"),
            instagram_response=result,
            attempted_at=datetime.utcnow(),
        )
        db.add(log_entry)

        if result.get("success"):
            post.status = "published"
            post.published_at = datetime.utcnow()
            post.instagram_post_id = result.get("instagram_post_id")

            if sched:
                sched.is_published = True
                sched.status = "published"
                sched.published_at = datetime.utcnow()

            db.commit()

            # Trigger immediate post-publish reminder notification
            try:
                from backend.services.notification import notification_service
                notification_service.send_post_publish_reminder(
                    post_id=post.id,
                    user_id=post.user_id,
                    db=db,
                    simulated=result.get("simulated", False),
                )
            except Exception as e:
                logger.warning(f"Failed to dispatch post-publish reminder notification: {e}")

            return {
                "success": True,
                "instagram_post_id": post.instagram_post_id,
                "simulated": result.get("simulated", False),
            }
        else:
            post.status = "failed"
            if sched:
                sched.status = "failed"
                sched.error_message = result.get("error")
            db.commit()
            return {
                "success": False,
                "error": result.get("error"),
            }


publishing_agent = PublishingAgent()
