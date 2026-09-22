import asyncio
import logging
from celery import Celery
from celery.schedules import crontab

from backend.config import settings
from backend.database import SessionLocal
from backend.models.user import User, BrandSetting
from backend.models.post import Post, ScheduledPost
from backend.pipeline.daily_pipeline import daily_pipeline
from backend.agents.publishing_agent import publishing_agent
from backend.agents.analytics_agent import analytics_agent
from backend.agents.learning_agent import learning_agent

logger = logging.getLogger("PromptPulse.CeleryTasks")

from backend.services.scheduler import scheduler_service

celery_app = Celery(
    "promptpulse",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "publish-due-scheduled-posts": {
            "task": "backend.tasks.celery_tasks.publish_due_scheduled_posts",
            "schedule": crontab(minute="*"),  # Every minute
        },
        "daily-research-pipeline": {
            "task": "backend.tasks.celery_tasks.run_scheduled_daily_pipeline",
            "schedule": crontab(hour=6, minute=0),  # 6:00 AM daily
        },
        "collect-analytics-hourly": {
            "task": "backend.tasks.celery_tasks.collect_analytics_for_due_posts",
            "schedule": crontab(minute=0, hour="*"),  # Every hour
        },
        "weekly-learning-synthesis": {
            "task": "backend.tasks.celery_tasks.run_weekly_learning_agent",
            "schedule": crontab(day_of_week=1, hour=7, minute=0),  # Every Monday at 7:00 AM
        },
        "check-queue-refill-reminders": {
            "task": "backend.tasks.celery_tasks.check_queue_refill_reminders",
            "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
        },
        "check-comments-and-dms": {
            "task": "backend.tasks.celery_tasks.check_comments_and_dms_task",
            "schedule": crontab(minute="*/5"),  # Every 5 minutes
        },
    },
)


@celery_app.task(name="backend.tasks.celery_tasks.publish_due_scheduled_posts")
def publish_due_scheduled_posts():
    """Checks for due scheduled posts and publishes them."""
    db = SessionLocal()
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        results = loop.run_until_complete(scheduler_service.publish_due_posts(db))
        return results
    finally:
        db.close()


@celery_app.task(name="backend.tasks.celery_tasks.run_scheduled_daily_pipeline")
def run_scheduled_daily_pipeline():
    """
    Runs daily autonomous discovery pipeline for all active users.
    For users with multiple posts_per_day, runs the pipeline once per slot
    and schedules each generated post at the corresponding posting time.
    """
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for u in users:
            try:
                brand = db.query(BrandSetting).filter(BrandSetting.user_id == u.id).first()
                posts_per_day = brand.posts_per_day if brand else 1
                posting_times = brand.posting_times if brand and brand.posting_times else [brand.posting_time or "09:00"] if brand else ["09:00"]
                if isinstance(posting_times, str):
                    try:
                        import json
                        posting_times = json.loads(posting_times)
                    except Exception:
                        posting_times = [brand.posting_time or "09:00"] if brand else ["09:00"]
                if not isinstance(posting_times, list) or len(posting_times) == 0:
                    posting_times = ["09:00"]

                # Determine how many pipelines to run for this user today
                num_runs = posts_per_day if (brand and brand.auto_mode_enabled) else 1

                for slot_idx in range(num_runs):
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_closed():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                        result = loop.run_until_complete(
                            daily_pipeline.run_daily_pipeline(user_id=u.id, db=db)
                        )

                        # If pipeline produced a post, schedule it at the correct slot time
                        if result.get("status") == "success" and "post_id" in result:
                            post_id = result["post_id"]
                            slot_time_str = posting_times[slot_idx] if slot_idx < len(posting_times) else posting_times[0]
                            try:
                                slot_h, slot_m = map(int, slot_time_str.split(":"))
                            except Exception:
                                slot_h, slot_m = 9, 0

                            from datetime import datetime
                            now = datetime.utcnow()
                            target_time = now.replace(hour=slot_h, minute=slot_m, second=0, microsecond=0)
                            if target_time <= now:
                                target_time = target_time  # Already past — publish immediately via scheduler

                            post = db.query(Post).filter(Post.id == post_id).first()
                            if post and post.status not in ("published",):
                                post.scheduled_at = target_time
                                if post.status == "pending_approval":
                                    pass  # Don't override approval-pending status
                                else:
                                    post.status = "scheduled"

                                sched = db.query(ScheduledPost).filter(ScheduledPost.post_id == post_id).first()
                                if not sched:
                                    sched = ScheduledPost(
                                        post_id=post_id,
                                        scheduled_time=target_time,
                                        status="pending",
                                        is_published=False,
                                    )
                                    db.add(sched)
                                else:
                                    sched.scheduled_time = target_time
                                    sched.status = "pending"
                                    sched.is_published = False
                                db.commit()

                    except Exception as e:
                        logger.error(f"Error running pipeline slot {slot_idx+1} for user {u.id}: {e}")

            except Exception as e:
                logger.error(f"Error running scheduled pipeline for user {u.id}: {e}")
    finally:
        db.close()


@celery_app.task(name="backend.tasks.celery_tasks.publish_post_task")
def publish_post_task(post_id: int):
    """Celery task to publish a scheduled post to Instagram."""
    db = SessionLocal()
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        result = loop.run_until_complete(publishing_agent.publish_to_instagram(post_id, db))
        return result
    finally:
        db.close()


@celery_app.task(name="backend.tasks.celery_tasks.collect_analytics_for_due_posts")
def collect_analytics_for_due_posts():
    """Hourly collection of post metrics via Meta Graph API."""
    db = SessionLocal()
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        results = loop.run_until_complete(analytics_agent.collect_due_posts(db))
        return results
    finally:
        db.close()


@celery_app.task(name="backend.tasks.celery_tasks.run_weekly_learning_agent")
def run_weekly_learning_agent():
    """Weekly optimization loop that updates brand settings and biases future strategy."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for u in users:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(learning_agent.update_strategy(user_id=u.id, db=db))
    finally:
        db.close()


@celery_app.task(name="backend.tasks.celery_tasks.check_queue_refill_reminders")
def check_queue_refill_reminders():
    """
    Checks topic queue coverage for all users every 6 hours.
    If coverage drops to:
    - 5 days or fewer (e.g. 5 topics for 1 post/day, 10 topics for 2 posts/day): sends reminder
    - 2 days or fewer: sends urgent reminder
    - 0 days: sends critical queue empty alert
    Ensures notifications are not spammed by checking last sent reminder in the past 12 hours.
    """
    from datetime import datetime, timedelta
    from backend.models.queue import TopicQueueItem
    from backend.models.notification import Notification
    from backend.services.notification import notification_service

    db = SessionLocal()
    try:
        users = db.query(User).all()
        now = datetime.utcnow()
        for u in users:
            try:
                brand = db.query(BrandSetting).filter(BrandSetting.user_id == u.id).first()
                posts_per_day = brand.posts_per_day if brand else 1
                if posts_per_day < 1:
                    posts_per_day = 1

                # Count remaining active topics in queue
                remaining_items = (
                    db.query(TopicQueueItem)
                    .filter(
                        TopicQueueItem.user_id == u.id,
                        TopicQueueItem.scheduled_date > now,
                        TopicQueueItem.status != "published",
                    )
                    .count()
                )

                days_left = remaining_items / posts_per_day

                # Check if we should alert
                if days_left <= 5.0:
                    # Check if a refill reminder was already sent in the last 12 hours to avoid spamming
                    recent_notif = (
                        db.query(Notification)
                        .filter(
                            Notification.user_id == u.id,
                            Notification.type == "queue_refill_reminder",
                            Notification.created_at >= now - timedelta(hours=12),
                        )
                        .first()
                    )
                    if not recent_notif:
                        notification_service.send_refill_reminder(
                            user_id=u.id,
                            remaining_items=remaining_items,
                            posts_per_day=posts_per_day,
                            days_left=days_left,
                            db=db,
                        )
                        logger.info(f"Sent queue refill reminder for user {u.id}: {remaining_items} topics, {days_left:.1f} days left")
            except Exception as e:
                logger.error(f"Error checking queue refill reminder for user {u.id}: {e}")
    finally:
        db.close()


@celery_app.task(name="backend.tasks.celery_tasks.check_comments_and_dms_task")
def check_comments_and_dms_task():
    """
    Autonomous background task: checks comments on published posts and recent DMs,
    detects keyword triggers, automatically sends Private Reply DMs with lead-magnets,
    and notifies the user on Telegram.
    """
    from backend.services.engagement_service import engagement_service
    db = SessionLocal()
    try:
        results = engagement_service.process_all_users(db)
        return results
    except Exception as e:
        logger.error(f"Error in check_comments_and_dms_task: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

