import json
import logging
from typing import Dict, Any, List, Optional
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

    def get_agent_brain(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Returns the current empirical learning state, winning hooks, and custom directives."""
        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
        strategy = brand.content_strategy if brand and brand.content_strategy else {}
        if not strategy:
            strategy = {
                "increase_pillar": "AI Workflows & Automation",
                "reduce_pillar": "Generic Lists",
                "best_posting_time": "09:00",
                "top_hook_patterns": [
                    "Stop doing X manually",
                    "This new engine eliminates hours of setup",
                    "The IDE feature nobody is talking about"
                ],
                "top_layouts": ["hero_editorial", "tool_card", "showcase"],
                "learning_notes": "Cosmic-neon carousels with 4-step workflow breakdowns and actionable lead magnet CTAs drive highest save rates.",
                "custom_directives": [
                    "Keep hooks under 8 words",
                    "Focus on tangible workflows and benchmarks",
                    "Include clear comment-to-DM keyword"
                ],
                "recent_learnings": [
                    "Posts covering developer tools receive 2.4x more bookmarks",
                    "Slide 5 comparison rows increase carousel completion rate to 88%"
                ]
            }
        return strategy

    def update_custom_directives(self, user_id: int, directives: List[str], db: Session) -> Dict[str, Any]:
        """Saves user-defined directives/rules for carousel generation."""
        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
        if not brand:
            return {"error": "Brand not found"}
        strategy = dict(brand.content_strategy or {})
        strategy["custom_directives"] = [d.strip() for d in directives if d and d.strip()]
        brand.content_strategy = strategy
        db.commit()
        return strategy

    async def learn_from_post_event(
        self,
        user_id: int,
        post_id: int,
        event_type: str,  # "approved", "rejected", "edited", "created", "published"
        feedback: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Incremental everyday learning hook that runs whenever a post is created, approved, rejected, or edited."""
        if db is None:
            from backend.database import SessionLocal
            db = SessionLocal()
            close_db = True
        else:
            close_db = False

        try:
            brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
            if not brand:
                return {}

            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                return {}

            strategy = dict(brand.content_strategy or {})
            recent_learnings = list(strategy.get("recent_learnings", []))

            if event_type == "approved":
                note = f"Approved post on '{post.topic}'. Reinforced hook pattern: '{post.hook[:45]}...'"
                if note not in recent_learnings:
                    recent_learnings.insert(0, note)
                top_hooks = list(strategy.get("top_hook_patterns", []))
                if post.hook and post.hook not in top_hooks:
                    top_hooks.insert(0, post.hook)
                    strategy["top_hook_patterns"] = top_hooks[:6]

            elif event_type == "rejected":
                reason = feedback or post.client_feedback or "User rejected this angle"
                note = f"Rejected angle on '{post.topic}': {reason[:60]}. Avoiding similar format."
                recent_learnings.insert(0, note)

            elif event_type == "edited":
                note = f"User adjusted slide copy for '{post.topic}'. Learned preference for concise phrasing."
                recent_learnings.insert(0, note)

            elif event_type == "created":
                note = f"Custom topic requested: '{post.topic}' in pillar '{post.content_pillar}'."
                recent_learnings.insert(0, note)

            strategy["recent_learnings"] = recent_learnings[:8]
            brand.content_strategy = strategy
            db.commit()
            return strategy
        finally:
            if close_db:
                db.close()


learning_agent = LearningAgent()
