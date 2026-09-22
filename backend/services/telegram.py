import logging
import requests
from typing import Optional, Dict, Any

from backend.config import settings

logger = logging.getLogger("PromptPulse.TelegramService")


class TelegramService:
    def __init__(self, bot_token: Optional[str] = None):
        self.default_bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.base_url = "https://api.telegram.org"

    def _get_token(self, bot_token: Optional[str] = None) -> Optional[str]:
        return bot_token or self.default_bot_token or settings.TELEGRAM_BOT_TOKEN

    def is_configured(self, bot_token: Optional[str] = None) -> bool:
        token = self._get_token(bot_token)
        return bool(token and token.strip())

    def get_bot_username(self, bot_token: Optional[str] = None) -> Optional[str]:
        """Fetch bot info via getMe endpoint."""
        token = self._get_token(bot_token)
        if not token:
            return None
        try:
            res = requests.get(f"{self.base_url}/bot{token}/getMe", timeout=10)
            data = res.json()
            if data.get("ok"):
                return data.get("result", {}).get("username")
        except Exception as e:
            logger.warning(f"Failed to fetch Telegram bot username: {e}")
        return None

    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        bot_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send formatted message to specified Telegram chat ID."""
        token = self._get_token(bot_token)
        if not token:
            logger.warning("Telegram bot token not configured. Message sending skipped.")
            return {"ok": False, "description": "Telegram bot token not configured."}

        url = f"{self.base_url}/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False,
        }

        try:
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()
            if not data.get("ok"):
                logger.error(f"Telegram API error: {data.get('description')}")
            return data
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return {"ok": False, "description": str(e)}

    def verify_chat(
        self,
        chat_id: str,
        bot_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Verifies bot can communicate with chat_id by sending a welcome test message."""
        welcome_text = (
            "🚀 <b>PromptPulse AI connected successfully!</b>\n\n"
            "You are now linked to your AI Instagram agent. You will receive:\n"
            "• 🔔 <b>Smart Refill Reminders</b> when your topic queue is running low\n"
            "• 🎉 <b>Instant confirmations</b> whenever a new carousel is published\n"
            "• 📈 <b>Virality & engagement updates</b>\n\n"
            "<i>Everything is running on autopilot. Sit back and create!</i>"
        )
        return self.send_message(chat_id=chat_id, text=welcome_text, bot_token=bot_token)

    def send_refill_reminder(
        self,
        chat_id: str,
        remaining_items: int,
        posts_per_day: int,
        days_left: float,
        bot_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends a smart queue refill reminder based on remaining coverage."""
        frontend_url = settings.FRONTEND_URL.rstrip("/")
        queue_url = f"{frontend_url}/queue"

        if days_left <= 0 or remaining_items == 0:
            urgency = "⚠️ <b>CRITICAL: Topic Queue Empty!</b>"
            status_text = "You have <b>0 topics remaining</b> in your queue. Your scheduled auto-posting is paused until you add new topics."
        elif days_left <= 2:
            urgency = "🚨 <b>URGENT: Topic Queue Running Out!</b>"
            status_text = (
                f"You only have <b>{remaining_items} topic(s) left</b> (~{days_left:.1f} day(s) of content at {posts_per_day} post/day)."
            )
        else:
            urgency = "💡 <b>Time to Refill Your Topic Queue</b>"
            status_text = (
                f"You have <b>{remaining_items} topic(s) remaining</b> in your queue (~{days_left:.1f} days left at {posts_per_day} post/day)."
            )

        text = (
            f"{urgency}\n\n"
            f"{status_text}\n\n"
            f"⚡ <b>Action needed:</b> Drop 10 new ideas into your queue to keep your uninterrupted daily streak alive!\n\n"
            f"👉 <a href=\"{queue_url}\">Open Topic Queue & Add 10 Ideas</a>"
        )
        return self.send_message(chat_id=chat_id, text=text, bot_token=bot_token)

    def send_publish_confirmation(
        self,
        chat_id: str,
        topic: str,
        post_url: Optional[str] = None,
        remaining_items: int = 0,
        bot_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sends confirmation when a carousel is published."""
        frontend_url = settings.FRONTEND_URL.rstrip("/")
        link_part = f"\n🔗 <a href=\"{post_url}\">View on Instagram</a>" if post_url else ""
        text = (
            f"🎉 <b>Carousel Published to Instagram!</b>\n\n"
            f"<b>Topic:</b> {topic}\n"
            f"<b>Remaining Queue:</b> {remaining_items} topic(s) scheduled{link_part}\n\n"
            f"👉 <a href=\"{frontend_url}/dashboard\">View Analytics & Insights</a>"
        )
        return self.send_message(chat_id=chat_id, text=text, bot_token=bot_token)


telegram_service = TelegramService()
