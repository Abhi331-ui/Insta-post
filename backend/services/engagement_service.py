import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.user import User, InstagramAccount, BrandSetting
from backend.models.post import Post
from backend.models.interaction import InstagramInteraction
from backend.services.instagram import instagram_service, InstagramService
from backend.services.telegram import telegram_service

logger = logging.getLogger("PromptPulse.EngagementService")


class EngagementService:
    def __init__(self):
        self.default_instagram = instagram_service

    def process_user_interactions(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Polls comments and DMs for the user's connected Instagram account.
        - Auto-detects lead-magnet keywords (e.g. 'TOOLKIT', 'GUIDE', 'PROMPT')
        - Sends automated private DM with resource link
        - Posts friendly comment reply
        - Notifies account owner via Telegram
        """
        ig_acc = db.query(InstagramAccount).filter(InstagramAccount.user_id == user_id).first()
        if not ig_acc or not ig_acc.access_token:
            return {"processed_comments": 0, "processed_dms": 0, "status": "instagram_not_connected"}

        insta_svc = InstagramService(
            access_token=ig_acc.access_token,
            instagram_user_id=ig_acc.instagram_user_id or "sim_user",
        )

        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()

        # 1. Fetch published posts in the last 14 days
        cutoff = datetime.utcnow() - timedelta(days=14)
        posts = (
            db.query(Post)
            .filter(
                Post.user_id == user_id,
                Post.status == "published",
                Post.created_at >= cutoff,
            )
            .all()
        )

        processed_comments = 0
        new_dms_sent = 0

        for post in posts:
            ig_post_id = post.instagram_post_id or f"ig_sim_{post.id}"
            comments = insta_svc.get_post_comments(ig_post_id, access_token=ig_acc.access_token)
            keyword = (post.dm_keyword or "TOOLKIT").strip().upper()

            for cmt in comments:
                cmt_id = cmt.get("id")
                if not cmt_id:
                    continue

                # Check if interaction already recorded
                existing = (
                    db.query(InstagramInteraction)
                    .filter(InstagramInteraction.external_id == cmt_id)
                    .first()
                )
                if existing:
                    continue

                text = cmt.get("text", "")
                sender = cmt.get("from", {})
                sender_username = sender.get("username", "user")
                sender_id = sender.get("id", "")

                # Check for keyword match
                is_match = keyword in text.upper() or any(
                    k in text.upper() for k in ["GUIDE", "TOOLKIT", "PROMPT", "LINK", "SEND", "CHECKLIST", "INFO"]
                )

                interaction = InstagramInteraction(
                    user_id=user_id,
                    post_id=post.id,
                    type="comment",
                    sender_username=sender_username,
                    sender_id=sender_id,
                    content=text,
                    is_keyword_match=is_match,
                    matched_keyword=keyword if is_match else None,
                    external_id=cmt_id,
                    status="pending",
                    created_at=datetime.utcnow(),
                )
                db.add(interaction)
                db.commit()
                db.refresh(interaction)

                processed_comments += 1

                # If keyword matches, trigger automated Private Reply + Comment Reply
                if is_match:
                    dm_body = (
                        post.dm_message
                        or f"Hey @{sender_username}! Here is the resource pack from today's post: {settings.FRONTEND_URL}/review/{post.share_token or 'latest'} - let me know what you think! 🚀"
                    )

                    # 1. Send private DM via Meta Private Replies
                    insta_svc.send_private_reply(
                        comment_id=cmt_id,
                        message=dm_body,
                        access_token=ig_acc.access_token,
                    )

                    # 2. Reply to comment publicly
                    reply_text = f"Sent you a DM @{sender_username}! Check your message requests 🚀"
                    insta_svc.reply_to_comment(
                        comment_id=cmt_id,
                        message=reply_text,
                        access_token=ig_acc.access_token,
                    )

                    interaction.status = "dm_sent"
                    interaction.dm_sent = True
                    interaction.reply_content = reply_text
                    db.commit()

                    new_dms_sent += 1

                    # 3. Notify owner on Telegram
                    if brand and brand.telegram_connected and brand.telegram_chat_id:
                        try:
                            clean_topic = post.topic[:40]
                            telegram_service.send_message(
                                chat_id=brand.telegram_chat_id,
                                text=(
                                    f"💬 <b>New Instagram Lead Generated!</b>\n\n"
                                    f"<b>User:</b> @{sender_username}\n"
                                    f"<b>Post:</b> {clean_topic}\n"
                                    f"<b>Comment:</b> \"{text}\"\n\n"
                                    f"✅ <b>Auto-DM sent</b> with your resource link!\n"
                                    f"<i>PromptPulse Lead Engine running on autopilot.</i>"
                                ),
                                bot_token=brand.telegram_bot_token,
                            )
                        except Exception as e:
                            logger.warning(f"Failed to send Telegram interaction alert: {e}")

        # 2. Check incoming direct messages (DMs)
        dms = insta_svc.get_direct_messages(
            access_token=ig_acc.access_token,
            instagram_user_id=ig_acc.instagram_user_id,
        )
        processed_dms = 0

        for msg in dms:
            msg_id = msg.get("id")
            if not msg_id:
                continue

            existing = (
                db.query(InstagramInteraction)
                .filter(InstagramInteraction.external_id == msg_id)
                .first()
            )
            if existing:
                continue

            sender_username = msg.get("sender_username", "user")
            sender_id = msg.get("sender_id", "")
            content = msg.get("message", "")

            interaction = InstagramInteraction(
                user_id=user_id,
                type="dm",
                sender_username=sender_username,
                sender_id=sender_id,
                content=content,
                is_keyword_match=False,
                external_id=msg_id,
                status="pending",
                created_at=datetime.utcnow(),
            )
            db.add(interaction)
            db.commit()
            processed_dms += 1

        return {
            "processed_comments": processed_comments,
            "new_dms_sent": new_dms_sent,
            "processed_dms": processed_dms,
            "status": "success",
        }

    def process_all_users(self, db: Session):
        """Runs interaction check for all active users."""
        users = db.query(User).all()
        for u in users:
            try:
                self.process_user_interactions(u.id, db)
            except Exception as e:
                logger.error(f"Error processing interactions for user {u.id}: {e}")


engagement_service = EngagementService()
