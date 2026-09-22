import asyncio
from datetime import datetime, timedelta
from backend.database import init_db, SessionLocal
from backend.models.user import User
from backend.models.post import Post, PostSlide, ScheduledPost
from backend.agents.qa_agent import qa_agent
from backend.api.posts import serialize_post
from backend.pipeline.daily_pipeline import daily_pipeline
from backend.services.scheduler import scheduler_service


def test_qa_agent_cta_title_recognition():
    """Verify QA Agent accepts Slide 6 CTA when call-to-action is in cta_title."""
    slides_content = [
        {"slide_number": 1, "headline": "Top AI Breakthrough", "body_text": "Overview"},
        {"slide_number": 2, "headline": "Context", "body_text": "Details"},
        {"slide_number": 3, "headline": "Features", "body_text": "Details"},
        {"slide_number": 4, "headline": "Steps", "body_text": "Details"},
        {"slide_number": 5, "headline": "Examples", "body_text": "Details"},
        {
            "slide_number": 6,
            "headline": "A NEW ERA FOR CREATORS",
            "body_text": "Better tools. Bigger ideas.",
            "cta_title": "Save this post",
            "cta_subtitle": "And start exploring the future.",
        },
    ]

    # Create dummy slide images
    from PIL import Image
    import tempfile
    from pathlib import Path

    temp_images = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(1, 7):
            p = Path(tmpdir) / f"slide_{i}.png"
            img = Image.new("RGB", (1080, 1350), color=(0, 0, 0))
            img.save(p)
            temp_images.append(str(p))

        qa_res = asyncio.run(qa_agent.quality_check(
            {"caption": "Test caption", "hashtags": "#test", "alt_text": "Alt text"},
            temp_images,
            slides_content,
        ))

        assert qa_res["passed"] is True, f"QA checks failed: {qa_res['critical_failures']}"
        assert 6 not in qa_res["failed_slide_indices"]


def test_post_serialization_remote_url():
    """Verify serialize_post preserves remote Supabase URLs rather than rewriting them."""
    post = Post(
        id=555,
        user_id=1,
        topic="Supabase URL Test",
        hook="Testing Supabase URL retention",
        status="pending_approval",
    )
    remote_url = "https://uomtyqgrkhelnqvjmmox.supabase.co/storage/v1/object/public/slides/posts/555/slide_1.png"
    slide = PostSlide(
        id=1,
        post_id=555,
        slide_number=1,
        headline="Headline",
        body_text="Body",
        layout_type="hero",
        image_path=remote_url,
    )
    post.slides = [slide]

    serialized = serialize_post(post)
    assert len(serialized["slides"]) == 1
    assert serialized["slides"][0]["image_url"] == remote_url


def test_custom_topic_pipeline_flow():
    """Verify that a custom topic from the queue or manual post directly creates a post."""
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            from backend.api.auth import get_current_user
            user = get_current_user(None, db)

        topic = "Bolt.new WebContainers Full-Stack Engine"
        res = asyncio.run(daily_pipeline.run_daily_pipeline(user_id=user.id, custom_topic=topic, db=db))
        assert res["status"] == "success"
        assert res["topic"] == topic
        assert "post_id" in res

        post = db.query(Post).filter(Post.id == res["post_id"]).first()
        assert post is not None
        assert len(post.slides) == 6
    finally:
        db.close()


def test_scheduler_publish_due_posts():
    """Verify scheduler_service.publish_due_posts finds due posts and processes them."""
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).first()
        user_id = user.id if user else 1

        # Create a test post due in the past
        post = Post(
            user_id=user_id,
            topic="Scheduled Post Test",
            hook="Testing auto publishing",
            status="scheduled",
            scheduled_at=datetime.utcnow() - timedelta(minutes=10),
        )
        db.add(post)
        db.flush()

        # Add 6 slides
        for i in range(1, 7):
            db.add(PostSlide(
                post_id=post.id,
                slide_number=i,
                headline=f"Headline {i}",
                body_text="Body",
                layout_type="hero",
                image_path=f"http://localhost:8000/media/slides/test_{i}.png",
            ))

        sched = ScheduledPost(
            post_id=post.id,
            scheduled_time=datetime.utcnow() - timedelta(minutes=10),
            status="pending",
            is_published=False,
        )
        db.add(sched)
        db.commit()

        results = asyncio.run(scheduler_service.publish_due_posts(db))
        assert any(r["post_id"] == post.id for r in results)

        db.refresh(sched)
        db.refresh(post)
        assert sched.status == "published"
        assert post.status == "published"
    finally:
        db.close()


def test_instagram_connection_options():
    """Verify test-connect, manual-connect, and disconnect endpoints work cleanly."""
    from backend.api.settings import (
        connect_instagram_test,
        connect_instagram_manual,
        disconnect_instagram,
        ManualInstagramConnectRequest,
    )
    from backend.models.user import InstagramAccount

    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            from backend.api.auth import get_current_user
            user = get_current_user(None, db)

        # 1. Test 1-click test connect
        res1 = connect_instagram_test(user=user, db=db)
        assert res1["success"] is True
        ig = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
        assert ig is not None
        assert ig.instagram_user_id == "test_instagram_business_id"

        # 2. Test manual connect
        req = ManualInstagramConnectRequest(
            instagram_user_id="17841400000000001",
            access_token="EAAXtesttoken123",
            page_name="My Production Page",
        )
        res2 = connect_instagram_manual(req=req, user=user, db=db)
        assert res2["success"] is True
        db.refresh(ig)
        assert ig.instagram_user_id == "17841400000000001"
        assert ig.page_name == "My Production Page"

        # 3. Test disconnect
        res3 = disconnect_instagram(user=user, db=db)
        assert res3["success"] is True
        ig_after = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
        assert ig_after is None
    finally:
        db.close()
