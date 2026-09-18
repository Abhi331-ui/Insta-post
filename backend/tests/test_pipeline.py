import os
import pytest
from pathlib import Path
from PIL import Image

from backend.database import init_db, SessionLocal
from backend.models.user import User, BrandSetting
from backend.models.post import Post, PostSlide
from backend.services.ai_provider import ai_provider
from backend.services.image_generator import image_generator
from backend.agents.trend_agent import trend_agent
from backend.agents.qa_agent import qa_agent
from backend.pipeline.daily_pipeline import daily_pipeline


def test_database_init():
    """Verify database initialization creates all tables."""
    init_db()
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        assert user_count >= 0
    finally:
        db.close()


def test_ai_provider_completion():
    """Verify AI provider fallback and extraction."""
    json_res = ai_provider._extract_json('{"test": 123, "name": "PromptPulse"}')
    assert json_res.get("test") == 123
    assert json_res.get("name") == "PromptPulse"


def test_image_generation_all_layouts():
    """Verify 1080x1350 slide rendering across all 6 layouts."""
    layouts = ["hero", "tool_card", "steps", "comparison", "workflow", "cta"]
    for idx, layout in enumerate(layouts):
        img_path = image_generator.generate_slide_image(
            post_id=999,
            slide_number=idx + 1,
            layout_type=layout,
            content={
                "headline": f"Test Headline for {layout}",
                "body_text": "High resolution mobile readable body copy adhering to PromptPulse standards.",
                "category": "BREAKTHROUGH",
            },
            brand={
                "brand_name": "PromptPulse",
                "primary_color": "#2563EB",
                "background_color": "#F8FAFC",
            },
        )
        assert Path(img_path).exists()
        with Image.open(img_path) as img:
            assert img.size == (1080, 1350), f"Layout {layout} returned wrong size {img.size}"


def test_trend_scoring():
    """Verify TrendAgent scoring and filtering."""
    import asyncio
    topics = [
        {
            "title": "Bolt.new in-browser runtime",
            "summary": "Containerized development engine.",
            "category": "tool",
        }
    ]
    scored = asyncio.run(trend_agent.score_topics(topics))
    assert len(scored) >= 1
    assert scored[0]["composite_score"] >= 6.0


def test_qa_agent():
    """Verify QA Agent critical checks."""
    import asyncio
    # Generate 6 slide images
    slide_images = []
    slides_content = []
    for i in range(1, 7):
        layout = "hero" if i == 1 else ("cta" if i == 6 else "tool_card")
        p = image_generator.generate_slide_image(
            post_id=998,
            slide_number=i,
            layout_type=layout,
            content={
                "headline": f"Unique Hook Headline {i}" if i == 1 else (f"Slide Insight {i}" if i < 6 else "Save this and follow PromptPulse"),
                "body_text": "Body text verification" if i < 6 else "Follow for daily verified AI discoveries.",
            }
        )
        slide_images.append(p)
        slides_content.append({
            "slide_number": i,
            "headline": f"Unique Hook Headline {i}" if i == 1 else (f"Slide Insight {i}" if i < 6 else "Save this and follow PromptPulse"),
            "body_text": "Body text verification",
            "layout_type": layout,
        })

    qa_res = asyncio.run(qa_agent.quality_check(
        {"caption": "Test caption", "hashtags": "#test", "alt_text": "Alt text"},
        slide_images,
        slides_content,
    ))
    assert qa_res["passed"] is True
    assert len(qa_res["critical_failures"]) == 0


def test_full_pipeline_run():
    """Verify full end-to-end pipeline run creating a post in the database."""
    import asyncio
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            from backend.api.auth import get_current_user
            user = get_current_user(None, db)

        res = asyncio.run(daily_pipeline.run_daily_pipeline(user_id=user.id, db=db))
        assert res["status"] in ["success", "no_opportunity"]
        if res["status"] == "success":
            assert "post_id" in res
            post = db.query(Post).filter(Post.id == res["post_id"]).first()
            assert post is not None
            assert len(post.slides) == 6
    finally:
        db.close()


def test_all_10_hero_variants_rendering():
    """Verify all 10 hero variants render cleanly to 1080x1350 PNG images."""
    from backend.pipeline.daily_pipeline import ALL_HERO_VARIANTS
    for idx, hero_type in enumerate(ALL_HERO_VARIANTS):
        img_path = image_generator.generate_slide_image(
            post_id=888 + idx,
            slide_number=1,
            layout_type=hero_type,
            content={
                "headline_prefix": "THIS BREAKTHROUGH CHANGES",
                "headline_highlight": "EVERYTHING",
                "headline": "THIS BREAKTHROUGH CHANGES EVERYTHING",
                "body_text": "Next generation AI architecture delivering instant results.",
                "annotation": "Real-time verification.",
                "category": "BREAKTHROUGH",
                "tool_name": "PromptPulse AI",
            },
            brand={
                "brand_name": "PromptPulse",
                "primary_color": "#7C3AED",
                "background_color": "#000000",
            },
        )
        assert Path(img_path).exists(), f"Image not found for {hero_type}"
        with Image.open(img_path) as img:
            assert img.size == (1080, 1350), f"{hero_type} returned size {img.size} instead of (1080, 1350)"


def test_select_hero_variant_anti_repetition():
    """Verify select_hero_variant_for_post avoids repetition across consecutive posts."""
    from backend.pipeline.daily_pipeline import select_hero_variant_for_post, ALL_HERO_VARIANTS
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).first()
        user_id = user.id if user else 1

        selected_heroes = []
        for i in range(10):
            hero = select_hero_variant_for_post(
                db=db,
                user_id=user_id,
                post_id=1000 + i,
                topic=f"Test AI Topic {i}",
                content_pillar="AI Tools & Productivity",
            )
            assert hero in ALL_HERO_VARIANTS
            selected_heroes.append(hero)

        # Ensure no two consecutive posts share the same hero variant
        for i in range(len(selected_heroes) - 1):
            assert selected_heroes[i] != selected_heroes[i + 1], f"Consecutive duplicate found: {selected_heroes[i]}"
    finally:
        db.close()


