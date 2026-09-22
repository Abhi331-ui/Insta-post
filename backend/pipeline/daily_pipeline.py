import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models.user import User, BrandSetting
from backend.models.post import Post, PostSlide, ScheduledPost
from backend.models.agent_run import AgentRun
from backend.agents.research_agent import research_agent
from backend.agents.trend_agent import trend_agent
from backend.agents.strategy_agent import strategy_agent
from backend.agents.content_agent import content_agent
from backend.agents.design_agent import design_agent
from backend.agents.factcheck_agent import factcheck_agent
from backend.agents.qa_agent import qa_agent
from backend.agents.publishing_agent import publishing_agent
from backend.services.image_generator import image_generator

logger = logging.getLogger("PromptPulse.DailyPipeline")

# Global pipeline progress tracker for SSE streaming
current_pipeline_state: Dict[str, Any] = {
    "status": "idle",
    "current_step": "",
    "step_index": 0,
    "total_steps": 10,
    "message": "System ready",
    "updated_at": datetime.utcnow().isoformat(),
}


def update_pipeline_progress(step_index: int, step_name: str, message: str, status: str = "running"):
    global current_pipeline_state
    current_pipeline_state = {
        "status": status,
        "current_step": step_name,
        "step_index": step_index,
        "total_steps": 10,
        "message": message,
        "updated_at": datetime.utcnow().isoformat(),
    }
ALL_HERO_VARIANTS = [
    "hero",
    "hero_editorial",
    "hero_terminal",
    "hero_badge",
    "hero_minimal_bold",
    "hero_grid_matrix",
    "hero_magazine",
    "hero_blueprint",
    "hero_gradient_punch",
    "hero_duotone",
]


def select_hero_variant_for_post(
    db: Session,
    user_id: int,
    post_id: int,
    topic: str = "",
    content_pillar: str = "",
    exclude_variants: Optional[List[str]] = None,
) -> str:
    """
    Selects a distinct hero design for Slide 1 that is guaranteed not to repeat
    recent posts and aligns with the topic/content pillar.
    """
    exclude_set = set(exclude_variants or [])

    # 1. Fetch recent hero layouts used by this user (last 8 posts)
    recent_slides = (
        db.query(PostSlide.layout_type)
        .join(Post, PostSlide.post_id == Post.id)
        .filter(Post.user_id == user_id, PostSlide.slide_number == 1)
        .order_by(Post.id.desc())
        .limit(8)
        .all()
    )
    recent_heroes = [s[0] for s in recent_slides if s[0]]
    blocked = set(recent_heroes).union(exclude_set)

    # 2. Topic/pillar preference mapping
    topic_lower = (topic or "").lower()
    pillar_lower = (content_pillar or "").lower()

    preferred: List[str] = []
    if any(k in topic_lower or k in pillar_lower for k in ["code", "developer", "terminal", "ide", "cli", "cursor", "repo", "git", "runtime", "software", "stack"]):
        preferred = ["hero_terminal", "hero_blueprint", "hero_grid_matrix"]
    elif any(k in topic_lower or k in pillar_lower for k in ["workflow", "automation", "agent", "pipeline", "architecture", "system"]):
        preferred = ["hero_blueprint", "hero_grid_matrix", "hero_minimal_bold"]
    elif any(k in topic_lower or k in pillar_lower for k in ["breakthrough", "benchmark", "fastest", "billion", "model", "record", "vs", "versus"]):
        preferred = ["hero_badge", "hero_gradient_punch", "hero"]
    elif any(k in topic_lower or k in pillar_lower for k in ["video", "image", "audio", "creative", "multimedia", "canvas", "design"]):
        preferred = ["hero_gradient_punch", "hero_duotone", "hero_editorial"]
    elif any(k in topic_lower or k in pillar_lower for k in ["trend", "industry", "future", "work", "strategy", "opinion", "deep dive"]):
        preferred = ["hero_editorial", "hero_magazine", "hero_minimal_bold"]

    # 3. Anti-repetition: try to find an unused candidate from preferred list, rotating by post_id
    valid_preferred = [p for p in preferred if p not in blocked]
    if valid_preferred:
        chosen = valid_preferred[post_id % len(valid_preferred)]
        logger.info(f"Selected preferred hero variant '{chosen}' for topic '{topic}' (anti-repetition checked)")
        return chosen

    # 4. If all preferred were blocked, pick from ALL_HERO_VARIANTS not in blocked
    unused = [v for v in ALL_HERO_VARIANTS if v not in blocked]
    if unused:
        chosen = unused[post_id % len(unused)]
        logger.info(f"Selected fresh unused hero variant '{chosen}' for post #{post_id}")
        return chosen

    # 5. Emergency fallback: avoid immediate last post's hero and exclude_set
    last_used = recent_heroes[0] if recent_heroes else None
    emergency_blocked = set(filter(None, [last_used])).union(exclude_set)
    candidates = [v for v in ALL_HERO_VARIANTS if v not in emergency_blocked]
    if not candidates:
        candidates = [v for v in ALL_HERO_VARIANTS if v != last_used] or ALL_HERO_VARIANTS

    chosen = candidates[post_id % len(candidates)]
    logger.info(f"Rotated hero variant '{chosen}' for post #{post_id} (avoiding last: {last_used})")
    return chosen


class DailyPipeline:
    def __init__(self):
        self.research_agent = research_agent
        self.trend_agent = trend_agent
        self.strategy_agent = strategy_agent
        self.content_agent = content_agent
        self.design_agent = design_agent
        self.factcheck_agent = factcheck_agent
        self.qa_agent = qa_agent
        self.publishing_agent = publishing_agent

    async def run_daily_pipeline(
        self,
        user_id: int,
        custom_topic: Optional[str] = None,
        custom_pillar: Optional[str] = None,
        custom_audience: Optional[List[str]] = None,
        custom_notes: Optional[str] = None,
        custom_hook: Optional[str] = None,
        custom_tone: Optional[str] = None,
        custom_dm_keyword: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrates all 10 agents sequentially.
        Adheres strictly to the core principle:
        'DISCOVER something worth posting every day. Do NOT just generate something every day.'
        """
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True

        agent_run = AgentRun(
            user_id=user_id,
            run_type="daily_pipeline" if not custom_topic else "manual",
            status="running",
            started_at=datetime.utcnow(),
        )
        db.add(agent_run)
        db.commit()

        try:
            if custom_topic:
                # 1. CUSTOM TOPIC DIRECT FLOW: User explicitly requested this topic (via manual post or batch queue)
                update_pipeline_progress(1, "Topic Setup", f"Configuring strategic angle and hooks for custom topic: '{custom_topic}'...")
                agent_run.topics_researched = 1

                custom_candidate = {
                    "title": custom_topic,
                    "summary": custom_notes or f"Practical breakdown, key features, and high-utility workflows for {custom_topic}.",
                    "source_url": "https://promptpulse.ai",
                    "source_name": "PromptPulse Discovery",
                    "category": "workflow",
                    "content_pillar": custom_pillar or "AI Workflows & Automation",
                    "target_audience": custom_audience or ["creators", "founders", "AI power-users"],
                    "freshness": "BRAND_NEW",
                    "notes": custom_notes or "",
                    "hook": custom_hook or "",
                    "tone": custom_tone or "Practical Deep Dive",
                    "dm_keyword": custom_dm_keyword or "",
                    "composite_score": 9.0,
                    "scores": {
                        "freshness": 9.0,
                        "usefulness": 9.0,
                        "curiosity": 8.5,
                        "save_potential": 9.0,
                        "share_potential": 8.5,
                        "visual_potential": 8.5,
                        "audience_relevance": 9.0,
                    },
                }

                brand_pre = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
                opportunity = await self.strategy_agent.select_opportunity(
                    [custom_candidate],
                    [],
                    content_strategy=brand_pre.content_strategy if brand_pre else None
                )
                if not opportunity:
                    # Direct structured fallback for custom topic
                    opportunity = {
                        "topic": custom_topic,
                        "why_today": f"Latest breakthrough and essential workflows for {custom_topic}.",
                        "freshness": "BRAND_NEW",
                        "selected_angle": custom_tone or f"How to master {custom_topic} in simple steps",
                        "hook": custom_hook or f"Stop doing this manually. {custom_topic} changes everything.",
                        "target_audience": custom_audience or ["creators", "founders", "AI power-users"],
                        "content_pillar": custom_pillar or "AI Workflows & Automation",
                        "notes": custom_notes or "",
                        "tone": custom_tone or "Practical Deep Dive",
                        "dm_keyword": custom_dm_keyword or "",
                        "sources": ["https://promptpulse.ai"],
                        "composite_score": 9.0,
                        "scores": custom_candidate["scores"],
                    }
                else:
                    if custom_pillar:
                        opportunity["content_pillar"] = custom_pillar
                    if custom_audience:
                        opportunity["target_audience"] = custom_audience
                    if custom_notes:
                        opportunity["notes"] = custom_notes
                    if custom_hook:
                        opportunity["hook"] = custom_hook
                    if custom_tone:
                        opportunity["tone"] = custom_tone
                    if custom_dm_keyword:
                        opportunity["dm_keyword"] = custom_dm_keyword
            else:
                # 1. RESEARCH
                update_pipeline_progress(1, "Research", "Scanning verified web sources for breaking AI developments...")
                raw_topics = await self.research_agent.research()
                agent_run.topics_researched = len(raw_topics)
                db.commit()

                # 2. SCORE & FILTER
                update_pipeline_progress(2, "Trend Evaluation", f"Scoring {len(raw_topics)} candidate topics across 7 viability criteria...")
                scored_candidates = await self.trend_agent.score_topics(raw_topics)
                valid_candidates = [t for t in scored_candidates if t.get("composite_score", 0) >= 6.0]

                # 3. SELECT OPPORTUNITY & ANTI-REPETITION
                update_pipeline_progress(3, "Strategy & Selection", "Executing anti-repetition audit against previous 30 posts...")
                previous_posts = (
                    db.query(Post)
                    .filter(Post.user_id == user_id)
                    .order_by(Post.created_at.desc())
                    .limit(30)
                    .all()
                )
                prev_post_dicts = [
                    {
                        "topic": p.topic,
                        "created_at": p.created_at,
                        "content_pillar": p.content_pillar,
                    }
                    for p in previous_posts
                ]

                brand_pre = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
                opportunity = await self.strategy_agent.select_opportunity(
                    valid_candidates,
                    prev_post_dicts,
                    content_strategy=brand_pre.content_strategy if brand_pre else None
                )

                # 4. IF NO STRONG OPPORTUNITY FOUND TODAY
                if not opportunity:
                    update_pipeline_progress(3, "Strategy & Selection", "No breaking candidate passed threshold. Checking high-utility evergreen...")
                    opportunity = await self.strategy_agent.find_evergreen_with_fresh_angle(user_id)

                if not opportunity:
                    msg = "DISCOVERY PRINCIPLE TRIGGERED: Nothing strong enough to post today. Continuing research."
                    update_pipeline_progress(3, "Strategy & Selection", msg, status="no_opportunity")
                    agent_run.status = "no_opportunity"
                    agent_run.completed_at = datetime.utcnow()
                    agent_run.rejection_reasons = ["All candidates scored below 6.0 or failed anti-repetition checks."]
                    db.commit()
                    return {"status": "no_opportunity", "message": msg}

            agent_run.topic_selected = opportunity.get("topic")
            agent_run.rejection_reasons = opportunity.get("rejection_log", [])
            db.commit()

            # Fetch user brand settings
            brand = db.query(BrandSetting).filter(BrandSetting.user_id == user_id).first()
            brand_dict = {
                "primary_color": brand.primary_color if brand else "#2563EB",
                "background_color": brand.background_color if brand else "#F8FAFC",
                "text_color": brand.text_color if brand else "#0F172A",
                "secondary_color": brand.secondary_color if brand else "#64748B",
                "brand_name": brand.brand_name if brand else "PromptPulse",
            }

            # 5. WRITE CAROUSEL CONTENT
            update_pipeline_progress(4, "Content Creation", f"Writing 6-slide story narrative for '{opportunity.get('topic')}'...")
            slides_content = await self.content_agent.write_carousel(opportunity)

            # 6. GENERATE METADATA (Caption, Hashtags, Alt text)
            update_pipeline_progress(5, "Copywriting", "Generating high-converting caption, hashtags, and accessibility alt text...")
            caption = await self.content_agent.generate_caption(opportunity, slides_content)
            hashtags = await self.content_agent.generate_hashtags(opportunity)
            alt_text = await self.content_agent.generate_alt_text(slides_content)

            # 7. FACT CHECK
            update_pipeline_progress(6, "Fact Checking", "Verifying all claims, metrics, and dates against sources...")
            fact_result = await self.factcheck_agent.fact_check(slides_content, opportunity.get("sources", []))
            if not fact_result.get("passed"):
                slides_content = fact_result.get("updated_slides", slides_content)

            # 8. CREATE POST RECORD IN DB
            slide_6 = slides_content[5] if len(slides_content) >= 6 else {}
            extracted_keyword = slide_6.get("dm_keyword") or "GUIDE"
            extracted_dm_message = slide_6.get("dm_message") or f"Hey! Here is your free {opportunity.get('topic')} resource pack: https://promptpulse.ai/toolkit - enjoy!"
            import secrets
            generated_share_token = secrets.token_urlsafe(16)

            post = Post(
                user_id=user_id,
                topic=opportunity.get("topic", "AI Discovery"),
                hook=opportunity.get("hook", ""),
                angle=opportunity.get("selected_angle", ""),
                freshness_category=opportunity.get("freshness", "BRAND_NEW"),
                content_pillar=opportunity.get("content_pillar", "AI Tools & Productivity"),
                why_today_reason=opportunity.get("why_today", ""),
                target_audience=opportunity.get("target_audience", []),
                caption=caption,
                hashtags=hashtags,
                alt_text=alt_text,
                dm_keyword=extracted_keyword,
                dm_message=extracted_dm_message,
                share_token=generated_share_token,
                status="generating",
                sources=opportunity.get("sources", []),
                scores=opportunity.get("scores", {}),
                created_at=datetime.utcnow(),
            )
            db.add(post)
            db.flush()

            # Trigger everyday incremental learning
            try:
                from backend.agents.learning_agent import learning_agent
                await learning_agent.learn_from_post_event(user_id, post.id, "created", None, db)
            except Exception as _learn_err:
                logger.warning(f"Could not update learning agent: {_learn_err}")

            # Assign distinct hero variant for Slide 1 (use hero_editorial for custom topics)
            if custom_topic:
                chosen_hero = "hero_editorial"
            else:
                chosen_hero = select_hero_variant_for_post(
                    db=db,
                    user_id=user_id,
                    post_id=post.id,
                    topic=post.topic,
                    content_pillar=post.content_pillar,
                )
            if slides_content and len(slides_content) > 0:
                slides_content[0]["layout_type"] = chosen_hero
                slides_content[0]["html_template"] = f"{chosen_hero}.html"

            # 9. DESIGN & RENDER SLIDES (1080x1350 PNG)
            update_pipeline_progress(7, "Design Rendering", f"Rendering 6 branded slides with distinct hero '{chosen_hero}'...")
            slide_images = await self.design_agent.generate_slides(
                slides_content,
                post_id=post.id,
                brand_settings=brand_dict,
            )

            # Save PostSlide records
            for idx, s in enumerate(slides_content):
                local_img_path = slide_images[idx] if idx < len(slide_images) else ""
                slide_layout = s.get("layout_type", "hero")
                public_url = image_generator.get_public_url(post_id=post.id, slide_number=idx + 1) or local_img_path
                slide_rec = PostSlide(
                    post_id=post.id,
                    slide_number=idx + 1,
                    headline=s.get("headline", ""),
                    body_text=s.get("body_text", ""),
                    layout_type=slide_layout,
                    html_template=f"{slide_layout}.html",
                    image_path=public_url,
                )
                db.add(slide_rec)

            db.commit()

            # 10. QA CHECKS
            update_pipeline_progress(8, "Quality Control", "Validating slide dimensions, duplication, hooks, and CTAs...")
            qa_result = await self.qa_agent.quality_check(
                {"caption": caption, "hashtags": hashtags, "alt_text": alt_text},
                slide_images,
                slides_content,
            )

            if not qa_result.get("passed"):
                # Targeted regeneration of failed slides (Max 1 auto-attempt)
                failed_indices = qa_result.get("failed_slide_indices", [])
                update_pipeline_progress(8, "Quality Control", f"Auto-fixing {len(failed_indices)} failed slide(s)...")
                for s_num in failed_indices:
                    if 1 <= s_num <= len(slides_content):
                        new_img = await self.design_agent.regenerate_single_slide(
                            slides_content[s_num - 1],
                            post_id=post.id,
                            slide_number=s_num,
                            brand_settings=brand_dict,
                        )
                        slide_images[s_num - 1] = new_img
                        public_url = image_generator.get_public_url(post_id=post.id, slide_number=s_num) or new_img
                        db_slide = db.query(PostSlide).filter(
                            PostSlide.post_id == post.id,
                            PostSlide.slide_number == s_num,
                        ).first()
                        if db_slide:
                            db_slide.image_path = public_url
                            db_slide.regenerated_count += 1
                db.commit()

            # Only remove local temporary files if they were successfully uploaded to remote storage (e.g. Supabase)
            for idx, image_path in enumerate(slide_images):
                pub_url = image_generator.get_public_url(post_id=post.id, slide_number=idx + 1)
                if pub_url and pub_url.startswith(("http://", "https://")) and "localhost" not in pub_url and "127.0.0.1" not in pub_url:
                    Path(image_path).unlink(missing_ok=True)

            # 11. APPROVAL OR AUTO PUBLISH
            auto_mode = brand.auto_mode_enabled if brand else False
            if auto_mode:
                update_pipeline_progress(9, "Publishing", "Auto-mode enabled: Publishing directly to Meta Graph API...")
                pub_result = await self.publishing_agent.publish_to_instagram(post.id, db)
                update_pipeline_progress(10, "Complete", "Carousel published successfully to Instagram!", status="completed")
            else:
                post.status = "pending_approval"
                db.commit()
                update_pipeline_progress(10, "Awaiting Approval", "Carousel ready for user review in Dashboard.", status="pending_approval")

            agent_run.status = "completed"
            agent_run.completed_at = datetime.utcnow()
            db.commit()

            return {
                "status": "success",
                "post_id": post.id,
                "topic": post.topic,
                "hook": post.hook,
                "status_code": post.status,
                "slides_count": len(slide_images),
                "fact_check": fact_result,
                "qa_result": qa_result,
            }

        except Exception as e:
            logger.exception(f"Pipeline failure: {e}")
            try:
                db.rollback()
            except Exception:
                pass
            try:
                agent_run.status = "failed"
                agent_run.error_message = str(e)
                agent_run.completed_at = datetime.utcnow()
                db.commit()
            except Exception:
                pass
            update_pipeline_progress(0, "Error", f"Pipeline encountered error: {str(e)}", status="failed")
            return {"status": "error", "error": str(e)}

        finally:
            if should_close_db:
                db.close()

    async def regenerate_single_slide_in_post(
        self,
        post_id: int,
        slide_number: int,
        db: Session,
    ) -> Dict[str, Any]:
        """Regenerates only one slide for a given post."""
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return {"error": "Post not found."}

        slide = db.query(PostSlide).filter(
            PostSlide.post_id == post_id,
            PostSlide.slide_number == slide_number,
        ).first()
        if not slide:
            return {"error": f"Slide {slide_number} not found."}

        brand = db.query(BrandSetting).filter(BrandSetting.user_id == post.user_id).first()
        brand_dict = {
            "primary_color": brand.primary_color if brand else "#2563EB",
            "background_color": brand.background_color if brand else "#F8FAFC",
            "text_color": brand.text_color if brand else "#0F172A",
            "secondary_color": brand.secondary_color if brand else "#64748B",
            "brand_name": brand.brand_name if brand else "PromptPulse",
        }

        # If Slide 1 (hero) is being regenerated, rotate to a fresh hero variant to give a new look
        if slide_number == 1:
            current_hero = slide.layout_type
            available = [v for v in ALL_HERO_VARIANTS if v != current_hero]
            next_hero = available[(slide.regenerated_count) % len(available)]
            slide.layout_type = next_hero
            slide.html_template = f"{next_hero}.html"

        # Request new variation from AI Content Agent
        prompt = f"Provide a fresh variation for slide {slide_number} ({slide.layout_type}) for topic '{post.topic}'."
        fresh_content = await self.content_agent.ai.complete_json(
            "Return JSON with: headline (max 8 words), body_text (max 40 words)",
            prompt,
            model_tier="strong",
        )

        if isinstance(fresh_content, dict) and "headline" in fresh_content:
            slide.headline = fresh_content.get("headline", slide.headline)
            slide.body_text = fresh_content.get("body_text", slide.body_text)

        new_img = await self.design_agent.regenerate_single_slide(
            {
                "headline": slide.headline,
                "body_text": slide.body_text,
                "layout_type": slide.layout_type,
            },
            post_id=post.id,
            slide_number=slide_number,
            brand_settings=brand_dict,
        )

        slide.image_path = image_generator.get_public_url(
            post_id=post.id,
            slide_number=slide_number,
        ) or new_img
        slide.regenerated_count += 1
        db.commit()
        if slide.image_path.startswith(("http://", "https://")) and "localhost" not in slide.image_path and "127.0.0.1" not in slide.image_path:
            Path(new_img).unlink(missing_ok=True)

        return {
            "success": True,
            "post_id": post.id,
            "slide_number": slide.slide_number,
            "headline": slide.headline,
            "body_text": slide.body_text,
            "layout_type": slide.layout_type,
            "image_path": slide.image_path,
            "regenerated_count": slide.regenerated_count,
        }


daily_pipeline = DailyPipeline()
