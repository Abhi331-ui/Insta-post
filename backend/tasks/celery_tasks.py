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
    },
)


@celery_app.task(name="backend.tasks.celery_tasks.run_scheduled_daily_pipeline")
def run_scheduled_daily_pipeline():
    """Runs daily autonomous discovery pipeline for all active users."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        for u in users:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                loop.run_until_complete(daily_pipeline.run_daily_pipeline(user_id=u.id, db=db))
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
