import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.notification import Notification
from backend.models.queue import TopicQueueItem
from backend.models.post import Post
from backend.models.user import BrandSetting

logger = logging.getLogger("PromptPulse.NotificationService")


class NotificationService:
    def send_post_publish_reminder(
        self,
        post_id: int,
        user_id: int,
        db: Session,
        simulated: bool = False,
    ) -> Notification:
        """
        Triggered immediately after publishing a carousel.
        Calculates queue coverage and reminds user to prepare the next 10 ideas.
        Dispatches both in-app notification and external webhook (Discord/Slack/Telegram) if configured.
        """
        post = db.query(Post).filter(Post.id == post_id).first()
        topic_title = post.topic if post else "Daily AI Discovery"

        # Calculate remaining queue coverage
        now = datetime.utcnow()
        remaining_items = (
            db.query(TopicQueueItem)
            .filter(
                TopicQueueItem.user_id == user_id,
                TopicQueueItem.scheduled_date > now,
                TopicQueueItem.status != "published",
            )
            .count()
        )

        title = f"🎉 Carousel Published: {topic_title[:50]}"
        sim_note = " (Simulated Mode)" if simulated else ""
        message = (
            f"Your daily carousel '{topic_title}' has been successfully published to Instagram!{sim_note} 🚀\n\n"
            f"📅 Queue Status: You have {remaining_items} day(s) of content scheduled.\n"
            f"⚡ Reminder: Make ready your next 10 trending ideas in the Topic Queue to maintain your uninterrupted daily streak!"
        )

        notif = Notification(
            user_id=user_id,
            type="post_published",
            title=title,
            message=message,
            link="/queue",
            is_read=False,
            created_at=datetime.utcnow(),
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        # Dispatch external webhook if configured in BrandSettings
        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
        if brand and brand.webhook_url:
            self._dispatch_webhook(brand.webhook_url, title, message, link="/queue")

        logger.info(f"Post-publish reminder notification created for user {user_id}: {title}")
        return notif

    def _dispatch_webhook(self, webhook_url: str, title: str, message: str, link: str = "/queue"):
        """Dispatches notification to Discord, Slack, or generic webhook relay."""
        try:
            frontend_base = settings.FRONTEND_URL.rstrip("/")
            payload = {
                "username": "PromptPulse Bot",
                "content": f"**{title}**\n\n{message}\n\n👉 [Open Topic Queue]({frontend_base}{link})",
                "embeds": [
                    {
                        "title": title,
                        "description": message,
                        "color": 0x2563EB,  # PromptPulse primary blue
                        "url": f"{frontend_base}{link}",
                    }
                ],
            }
            requests.post(webhook_url, json=payload, timeout=5)
        except Exception as e:
            logger.warning(f"Failed to dispatch external webhook notification: {e}")


notification_service = NotificationService()
