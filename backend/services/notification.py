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
from backend.services.telegram import telegram_service

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
        Dispatches in-app notification, Telegram message, and external webhook if configured.
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

        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()

        # Dispatch via Telegram if connected
        if brand and brand.telegram_connected and brand.telegram_chat_id:
            try:
                telegram_service.send_publish_confirmation(
                    chat_id=brand.telegram_chat_id,
                    topic=topic_title,
                    post_url=post.instagram_permalink if post and hasattr(post, "instagram_permalink") else None,
                    remaining_items=remaining_items,
                    bot_token=brand.telegram_bot_token,
                )
            except Exception as e:
                logger.warning(f"Failed to dispatch Telegram post-publish notification: {e}")

        # Dispatch external webhook if configured in BrandSettings
        if brand and brand.webhook_url:
            self._dispatch_webhook(brand.webhook_url, title, message, link="/queue")

        logger.info(f"Post-publish reminder notification created for user {user_id}: {title}")
        return notif

    def send_refill_reminder(
        self,
        user_id: int,
        remaining_items: int,
        posts_per_day: int,
        days_left: float,
        db: Session,
    ) -> Notification:
        """
        Sends smart queue refill reminder when topics in queue are running low.
        E.g. for 1 post/day, reminds when <= 5 topics left.
        For 2 posts/day, reminds when <= 2-3 days (4-6 topics) left.
        Dispatches in-app, Telegram, and webhook.
        """
        if days_left <= 0:
            title = "⚠️ Topic Queue Empty — Action Required"
            message = (
                f"Your topic queue is empty! Auto-publishing will be paused until you add new topics.\n"
                f"⚡ Add 10 new ideas in your Topic Queue now to keep your streak alive!"
            )
        elif days_left <= 2:
            title = f"🚨 Topic Queue Low: Only {remaining_items} Ideas Left"
            message = (
                f"You have only {remaining_items} topic(s) remaining in your queue (~{days_left:.1f} days of content).\n"
                f"⚡ Add your next 10 ideas now so the AI can generate and schedule carousels on time!"
            )
        else:
            title = f"💡 Refill Reminder: {remaining_items} Topics Remaining"
            message = (
                f"You have {remaining_items} topic(s) remaining in your queue (~{days_left:.1f} days left).\n"
                f"Add 10 new ideas to ensure your content pipeline stays full and active!"
            )

        notif = Notification(
            user_id=user_id,
            type="queue_refill_reminder",
            title=title,
            message=message,
            link="/queue",
            is_read=False,
            created_at=datetime.utcnow(),
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()

        # Dispatch via Telegram if connected
        if brand and brand.telegram_connected and brand.telegram_chat_id:
            try:
                telegram_service.send_refill_reminder(
                    chat_id=brand.telegram_chat_id,
                    remaining_items=remaining_items,
                    posts_per_day=posts_per_day,
                    days_left=days_left,
                    bot_token=brand.telegram_bot_token,
                )
            except Exception as e:
                logger.warning(f"Failed to dispatch Telegram refill reminder: {e}")

        # Dispatch webhook if configured
        if brand and brand.webhook_url:
            self._dispatch_webhook(brand.webhook_url, title, message, link="/queue")

        logger.info(f"Refill reminder notification created for user {user_id}: {title}")
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
                        "color": 0x7C3AED,  # PromptPulse primary purple
                        "url": f"{frontend_base}{link}",
                    }
                ],
            }
            requests.post(webhook_url, json=payload, timeout=5)
        except Exception as e:
            logger.warning(f"Failed to dispatch external webhook notification: {e}")


notification_service = NotificationService()
