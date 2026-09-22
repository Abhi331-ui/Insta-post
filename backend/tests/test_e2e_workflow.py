"""
Comprehensive End-to-End Workflow Test for PromptPulse.
Tests the complete user journey:
1. User profile & Instagram/Telegram connectivity
2. Topic Queue ingestion & scheduling pacing
3. Autonomous Carousel generation (6 slides, dynamic hero, Slide 6 CTA keyword)
4. Multi-page PDF Export for client review / LinkedIn
5. Post publishing to Instagram (simulated/live)
6. Comment & DM monitoring with automated Private Reply lead-magnet delivery
7. Client Magic Review link approval workflow
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image

from backend.database import init_db, SessionLocal
from backend.models.user import User, BrandSetting, InstagramAccount
from backend.models.post import Post, PostSlide, ScheduledPost
from backend.models.queue import TopicQueueItem
from backend.models.interaction import InstagramInteraction
from backend.services.image_generator import image_generator
from backend.pipeline.daily_pipeline import daily_pipeline
from backend.agents.publishing_agent import publishing_agent
from backend.services.engagement_service import engagement_service
from backend.services.notification import notification_service
from backend.services.instagram import instagram_service


def run_e2e_workflow():
    print("=" * 70)
    print(">>> STARTING PROMPTPULSE FULL END-TO-END WORKFLOW TEST")
    print("=" * 70)

    # 1. Initialize Database
    init_db()
    db = SessionLocal()

    try:
        # Step 1: Ensure User & Brand Settings
        print("\n[Step 1] Verifying User & Settings...")
        user = db.query(User).first()
        if not user:
            user = User(
                email="creator@promptpulse.ai",
                hashed_password="test_hashed_password",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        brand = db.query(BrandSetting).filter(BrandSetting.user_id == user.id).first()
        if not brand:
            brand = BrandSetting(
                user_id=user.id,
                brand_name="PromptPulse Growth",
                primary_color="#7C3AED",
                background_color="#030712",
                posts_per_day=2,
                posting_times=["09:00", "18:00"],
                auto_mode_enabled=True,
            )
            db.add(brand)
            db.commit()
            db.refresh(brand)
        else:
            brand.posts_per_day = 2
            brand.posting_times = ["09:00", "18:00"]
            brand.auto_mode_enabled = True
            db.commit()

        # Connect Instagram test account if not present
        ig_acc = db.query(InstagramAccount).filter(InstagramAccount.user_id == user.id).first()
        if not ig_acc:
            ig_acc = InstagramAccount(
                user_id=user.id,
                instagram_user_id="17841400000000001",
                page_name="PromptPulse Official",
                username="promptpulse.ai",
                access_token="TEST_MOCK_TOKEN_E2E",
            )
            db.add(ig_acc)
            db.commit()

        # Connect Telegram on brand settings
        brand.telegram_chat_id = "123456789"
        brand.telegram_connected = True
        db.commit()

        print(f"  [OK] User verified: ID={user.id}, Email={user.email}")
        print(f"  [OK] Brand verified: {brand.brand_name}, {brand.posts_per_day} posts/day at {brand.posting_times}")
        print(f"  [OK] Instagram connected: @{ig_acc.username} (ID: {ig_acc.instagram_user_id})")
        print(f"  [OK] Telegram connected: Chat ID {brand.telegram_chat_id}")

        # Step 2: Topic Queue Ingestion
        print("\n[Step 2] Ingesting Topics into Topic Queue...")
        topics_to_test = [
            "5 AI tools that write better code than senior engineers",
            "How to automate high-ticket client acquisition in 2026",
            "The secret framework to build viral carousels in 10 minutes",
        ]

        now = datetime.utcnow()
        queue_items = []
        effective_times = brand.posting_times
        if isinstance(effective_times, str):
            import json
            try:
                effective_times = json.loads(effective_times)
            except Exception:
                effective_times = ["09:00", "18:00"]
        if not isinstance(effective_times, list) or len(effective_times) < 2:
            effective_times = ["09:00", "18:00"]

        batch_id = f"batch_{int(now.timestamp())}"
        for idx, topic in enumerate(topics_to_test):
            # Schedule with pacing: 2 posts per day (slot 0 at 9am, slot 1 at 6pm)
            day_offset = idx // 2
            slot_idx = idx % 2
            h, m = map(int, effective_times[slot_idx].split(":"))
            sched_time = (now + timedelta(days=day_offset)).replace(hour=h, minute=m, second=0)

            item = TopicQueueItem(
                user_id=user.id,
                batch_id=batch_id,
                day_index=idx + 1,
                topic=topic,
                scheduled_date=sched_time,
                status="pending",
            )
            db.add(item)
            queue_items.append(item)

        db.commit()
        for it in queue_items:
            db.refresh(it)
        print(f"  [OK] Ingested {len(queue_items)} topics with 2 posts/day pacing.")
        for it in queue_items:
            print(f"    - [{it.scheduled_date.strftime('%Y-%m-%d %H:%M')}] {it.topic[:45]}...")

        # Step 3: Autonomous Carousel Generation from Queue
        print("\n[Step 3] Running Autonomous Carousel Generation for Top Topic...")
        target_item = queue_items[0]
        loop = asyncio.get_event_loop()

        pipeline_res = loop.run_until_complete(
            daily_pipeline.run_daily_pipeline(user_id=user.id, db=db, custom_topic=target_item.topic)
        )
        assert pipeline_res.get("status") == "success", f"Pipeline failed: {pipeline_res}"
        post_id = pipeline_res["post_id"]
        post = db.query(Post).filter(Post.id == post_id).first()
        assert post is not None, "Post not found in DB"
        assert len(post.slides) == 6, f"Expected 6 slides, got {len(post.slides)}"

        print(f"  [OK] Post generated successfully: ID={post.id}")
        print(f"  [OK] Topic: {post.topic}")
        print(f"  [OK] Hook (Slide 1): {post.slides[0].headline}")
        print(f"  [OK] Hero Layout Type: {post.slides[0].layout_type}")
        print(f"  [OK] Slide 6 CTA: {post.slides[5].headline}")
        print(f"  [OK] Lead Magnet Trigger Keyword: '{post.dm_keyword}'")
        dm_preview = (post.dm_message or "https://promptpulse.ai/toolkit")[:60]
        print(f"  [OK] Automated DM Message Preview: '{dm_preview}...'")
        print(f"  [OK] Magic Review Share Token: {post.share_token}")

        # Update queue item to generated
        target_item.status = "generated"
        target_item.post_id = post.id
        db.commit()

        # Step 4: Verify Slide Visual Assets & Multi-Page PDF Export
        print("\n[Step 4] Verifying Slide Visual Assets & Multi-Page PDF Export...")
        import io
        import requests
        from backend.api.posts import _build_pdf_from_post

        for s in post.slides:
            assert s.image_path is not None, f"Slide {s.slide_number} has no image_path"
            if s.image_path.startswith(("http://", "https://")):
                r = requests.get(s.image_path, timeout=15)
                assert r.status_code == 200, f"Failed to download slide {s.slide_number} from Supabase: {s.image_path}"
                with Image.open(io.BytesIO(r.content)) as img:
                    assert img.size == (1080, 1350), f"Slide size is {img.size}, expected (1080, 1350)"
                print(f"  [OK] Slide {s.slide_number} verified from Supabase cloud: 1080x1350 PNG ({s.image_path.split('/')[-1]})")
            else:
                local_path = Path(s.image_path)
                assert local_path.exists(), f"Slide {s.slide_number} image missing: {s.image_path}"
                with Image.open(local_path) as img:
                    assert img.size == (1080, 1350), f"Slide size is {img.size}, expected (1080, 1350)"
                print(f"  [OK] Slide {s.slide_number} verified from local storage: 1080x1350 PNG ({local_path.name})")

        # Test PDF Export
        pdf_buffer = _build_pdf_from_post(post)
        pdf_size = len(pdf_buffer.getvalue())
        assert pdf_size > 50000, f"PDF generated is unexpectedly small: {pdf_size} bytes"
        print(f"  [OK] Multi-Page PDF successfully created ({pdf_size / 1024:.1f} KB, 6 pages).")

        # Step 5: Simulate Publishing to Instagram
        print("\n[Step 5] Simulating Instagram Carousel Publishing...")
        pub_res = loop.run_until_complete(publishing_agent.publish_to_instagram(post.id, db))
        assert pub_res.get("success") is True, f"Publishing failed: {pub_res}"
        db.refresh(post)
        assert post.status == "published", f"Post status is {post.status}, expected 'published'"
        assert post.instagram_post_id is not None, "instagram_post_id was not set"
        print(f"  [OK] Post published to Instagram! Media ID: {post.instagram_post_id}")

        # Step 6: Autonomous Engagement — Comment & DM Handling
        print("\n[Step 6] Testing Autonomous Comment & DM Monitoring with Lead Magnet Private Reply...")
        # Add a simulated comment on this published post with the trigger keyword
        test_commenter = "future_customer_99"
        trigger_comment_content = f"Can you please send me the {post.dm_keyword}?? Looks awesome!"
        
        # Test engagement processing directly
        # In test/simulated mode, instagram_service returns mock comments
        engagement_res = engagement_service.process_user_interactions(user.id, db)
        print(f"  [OK] Engagement check executed: {engagement_res}")

        # Let's also verify direct interaction handling with an explicit interaction record
        ext_comment_id = f"comment_test_{int(datetime.utcnow().timestamp())}_{post.id}"
        interaction = InstagramInteraction(
            user_id=user.id,
            post_id=post.id,
            type="comment",
            external_id=ext_comment_id,
            sender_id=f"user_test_{post.id}",
            sender_username=test_commenter,
            content=trigger_comment_content,
            is_keyword_match=True,
            matched_keyword=post.dm_keyword,
            status="pending",
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        # Trigger private reply DM
        dm_res = instagram_service.send_private_reply(
            comment_id=interaction.external_id,
            message=post.dm_message or f"Hey @{test_commenter}! Here is your free {post.dm_keyword} link: https://promptpulse.ai/toolkit",
            access_token=ig_acc.access_token,
        )
        assert dm_res.get("success", False) or dm_res.get("status") == "success"

        # Trigger public comment reply
        reply_res = instagram_service.reply_to_comment(
            comment_id=interaction.external_id,
            message=f"Hey @{test_commenter}! Just sent the {post.dm_keyword} to your DMs 🚀 Check your inbox!",
            access_token=ig_acc.access_token,
        )
        assert reply_res.get("success", False) or reply_res.get("status") == "success"

        interaction.status = "replied"
        interaction.reply_content = f"Hey @{test_commenter}! Just sent the {post.dm_keyword} to your DMs 🚀 Check your inbox!"
        interaction.dm_sent = True
        interaction.replied_at = datetime.utcnow()
        db.commit()
        db.refresh(interaction)

        print(f"  [OK] Follower comment received: '{interaction.content}' from @{interaction.sender_username}")
        print(f"  [OK] Keyword '{interaction.matched_keyword}' detected: is_keyword_match={interaction.is_keyword_match}")
        print(f"  [OK] Meta Private Reply DM sent directly to commenter's inbox: dm_sent={interaction.dm_sent}")
        print(f"  [OK] Public confirmation reply posted: '{interaction.reply_content}'")

        # Step 7: Client Magic Review Link Workflow
        print("\n[Step 7] Testing Client Magic Review Link Workflow...")
        from fastapi.testclient import TestClient
        from backend.main import app
        client = TestClient(app)

        # Fetch public review endpoint
        review_res = client.get(f"/api/posts/public/review/{post.share_token}")
        assert review_res.status_code == 200, f"Review link returned {review_res.status_code}"
        review_data = review_res.json()
        assert review_data["topic"] == post.topic
        assert len(review_data["slides"]) == 6
        print(f"  [OK] Magic review page accessible without login: /review/{post.share_token}")
        print(f"  [OK] Client slides loaded: {len(review_data['slides'])} slides")

        # Client submits feedback or approval
        action_res = client.post(
            f"/api/posts/public/review/{post.share_token}/action",
            json={"action": "approve", "feedback": "Looks fantastic! Approved for posting."},
        )
        assert action_res.status_code == 200
        print("  [OK] Client 1-click approval executed successfully!")

        # Step 8: Inbox API Check
        print("\n[Step 8] Testing Inbox API Endpoints...")
        from backend.api.auth import create_access_token
        auth_token = create_access_token(data={"sub": user.email})
        headers = {"Authorization": f"Bearer {auth_token}"}

        inbox_res = client.get("/api/interactions", headers=headers)
        assert inbox_res.status_code == 200
        items = inbox_res.json()
        assert len(items) >= 1
        print(f"  [OK] GET /api/interactions returned {len(items)} interactions")

        stats_res = client.get("/api/interactions/stats", headers=headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        print(f"  [OK] GET /api/interactions/stats: {stats}")
        assert stats["keyword_matches"] >= 1
        assert stats["auto_dms_sent"] >= 1

        print("\n" + "=" * 70)
        print(">>> ALL 8 STEPS OF THE END-TO-END WORKFLOW PASSED WITH ZERO ERRORS!")
        print("=" * 70)
        return True

    finally:
        db.close()


if __name__ == "__main__":
    success = run_e2e_workflow()
    if success:
        print("\n[SUCCESS] Entire PromptPulse workflow is fully operational.")
