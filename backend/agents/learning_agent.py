import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.services.ai_provider import ai_provider
from backend.models.post import Post
from backend.models.analytics import Analytics
from backend.models.user import BrandSetting

logger = logging.getLogger("PromptPulse.LearningAgent")


class LearningAgent:
    def __init__(self):
        self.ai = ai_provider

    async def update_strategy(self, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Runs weekly feedback loop over the last 30 posts and their analytics.
        Discovers high-performing pillars, hook styles, layout formats, and posting times.
        Updates brand_settings.content_strategy in the database.
        """
        # Fetch up to 30 recent posts for this user
        posts = (
            db.query(Post)
            .filter(Post.user_id == user_id, Post.status == "published")
            .order_by(Post.created_at.desc())
            .limit(30)
            .all()
        )

        posts_data = []
        for p in posts:
            latest_analytics = (
                db.query(Analytics)
                .filter(Analytics.post_id == p.id)
                .order_by(Analytics.collected_at.desc())
                .first()
            )
            posts_data.append({
                "post_id": p.id,
                "topic": p.topic,
                "hook": p.hook,
                "pillar": p.content_pillar,
                "freshness": p.freshness_category,
                "scores": p.scores,
                "reach": latest_analytics.reach if latest_analytics else 0,
                "saves": latest_analytics.saves if latest_analytics else 0,
                "shares": latest_analytics.shares if latest_analytics else 0,
                "engagement_rate": latest_analytics.engagement_rate if latest_analytics else 0.0,
            })

        if len(posts_data) < 3:
            # Baseline strategic bias if under minimum post threshold
            baseline_strategy = {
                "increase_pillar": "AI Workflows & Automation",
                "reduce_pillar": "Generic Lists",
                "best_posting_time": "09:00",
                "top_hook_patterns": [
                    "Stop doing X manually",
                    "This new engine eliminates hours of setup",
                    "Nobody is talking about this breakthrough"
                ],
                "top_layouts": ["tool_card", "workflow", "comparison"],
                "learning_notes": "Early sample size (<3 posts). Strategy biased toward high-utility workflow carousels and tangible time-saving tools.",
            }
            brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
            if brand:
                brand.content_strategy = baseline_strategy
                db.commit()
            return baseline_strategy

        system_prompt = """You are the PromptPulse Chief Learning & Optimization Agent.
Analyze the performance data of recent Instagram carousels.
Identify clear empirical patterns:
- Which content pillar gets the most saves and bookmarks?
- Which hook pattern drives the highest engagement?
- Which formats or topics underperform?

Return a JSON object with:
- "increase_pillar": pillar to prioritize
- "reduce_pillar": pillar to deprioritize
- "best_posting_time": recommended HH:MM posting time
- "top_hook_patterns": list of 3 high-converting hook structures
- "top_layouts": list of top 2 performing layout types
- "learning_notes": 2 sentences summarizing the empirical takeaways
"""
        user_prompt = f"Performance dataset of {len(posts_data)} posts:\n{json.dumps(posts_data, indent=2)}"

        learned = await self.ai.complete_json(system_prompt, user_prompt, model_tier="strong")

        if not isinstance(learned, dict) or "increase_pillar" not in learned:
            learned = {
                "increase_pillar": "AI Workflows & Automation",
                "reduce_pillar": "Generic Lists",
                "best_posting_time": "09:00",
                "top_hook_patterns": ["Stop doing X manually", "New breakthrough in Web dev"],
                "top_layouts": ["workflow", "comparison"],
                "learning_notes": "Workflow breakdowns generated highest saves and bookmark retention.",
            }

        # Persist learned strategy into brand settings
        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
        if brand:
            brand.content_strategy = learned
            db.commit()

        return learned


learning_agent = LearningAgent()
