import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.services.instagram import instagram_service
from backend.models.post import Post
from backend.models.analytics import Analytics

logger = logging.getLogger("PromptPulse.AnalyticsAgent")


class AnalyticsAgent:
    def __init__(self):
        self.instagram = instagram_service

    async def collect_analytics(self, post_id: int, db: Session) -> Dict[str, Any]:
        """
        Collects reach, impressions, saves, shares, likes, comments, and profile visits
        via Meta Graph API insights for a published post.
        """
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post or not post.instagram_post_id:
            return {"error": "Post not found or not yet published to Instagram."}

        metrics = self.instagram.get_post_insights(post.instagram_post_id)

        analytics_entry = Analytics(
            post_id=post.id,
            reach=metrics.get("reach", 0),
            impressions=metrics.get("impressions", 0),
            likes=metrics.get("likes", 0),
            comments=metrics.get("comments", 0),
            shares=metrics.get("shares", 0),
            saves=metrics.get("saves", 0),
            profile_visits=metrics.get("profile_visits", 0),
            follows=metrics.get("follows", 0),
            engagement_rate=metrics.get("engagement_rate", 0.0),
            collected_at=datetime.utcnow(),
        )
        db.add(analytics_entry)
        db.commit()

        return metrics

    async def collect_due_posts(self, db: Session) -> List[Dict[str, Any]]:
        """Collect analytics for all posts published in the last 7 days."""
        since = datetime.utcnow() - timedelta(days=7)
        published_posts = (
            db.query(Post)
            .filter(Post.status == "published", Post.published_at >= since)
            .all()
        )
        results = []
        for p in published_posts:
            try:
                res = await self.collect_analytics(p.id, db)
                results.append({"post_id": p.id, "metrics": res})
            except Exception as e:
                logger.error(f"Error collecting analytics for post {p.id}: {e}")

        return results


analytics_agent = AnalyticsAgent()
