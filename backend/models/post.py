from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Content Strategy & Metadata
    topic = Column(String(255), nullable=False)
    hook = Column(Text, nullable=False)
    angle = Column(Text, nullable=True)
    freshness_category = Column(String(50), default="BRAND_NEW")  # BRAND_NEW/DEVELOPING/RECENT/EVERGREEN
    content_pillar = Column(String(100), nullable=True)
    why_today_reason = Column(Text, nullable=True)
    target_audience = Column(JSON, default=list)

    # Post Copy
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)
    alt_text = Column(Text, nullable=True)

    # Status: draft/researching/generating/qa/pending_approval/scheduled/published/failed
    status = Column(String(50), default="draft", index=True)
    instagram_post_id = Column(String(100), nullable=True, index=True)

    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)

    sources = Column(JSON, default=list)  # list of URLs and source details
    scores = Column(JSON, default=dict)   # composite and sub-scores
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="posts")
    slides = relationship("PostSlide", back_populates="post", cascade="all, delete-orphan", order_by="PostSlide.slide_number")
    scheduled_record = relationship("ScheduledPost", back_populates="post", uselist=False, cascade="all, delete-orphan")
    publishing_logs = relationship("PublishingLog", back_populates="post", cascade="all, delete-orphan")
    analytics_records = relationship("Analytics", back_populates="post", cascade="all, delete-orphan")
    ai_generations = relationship("AIGeneration", back_populates="post", cascade="all, delete-orphan")


class PostSlide(Base):
    __tablename__ = "post_slides"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    slide_number = Column(Integer, nullable=False)  # 1 to 6

    headline = Column(String(255), nullable=False)
    body_text = Column(Text, nullable=True)
    layout_type = Column(String(50), default="hero")  # hero/tool_card/steps/comparison/workflow/cta
    html_template = Column(String(100), default="hero.html")
    image_path = Column(String(500), nullable=True)
    regenerated_count = Column(Integer, default=0)

    post = relationship("Post", back_populates="slides")


class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, unique=True)
    scheduled_time = Column(DateTime, nullable=False)
    timezone = Column(String(50), default="UTC")
    celery_task_id = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")  # pending/published/failed/cancelled
    is_published = Column(Boolean, default=False, nullable=False)  # Idempotency lock
    published_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    post = relationship("Post", back_populates="scheduled_record")


class PublishingLog(Base):
    __tablename__ = "publishing_logs"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    attempt_number = Column(Integer, default=1)
    status = Column(String(50), nullable=False)  # success/failed/retrying
    error_message = Column(Text, nullable=True)
    instagram_response = Column(JSON, default=dict)
    attempted_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="publishing_logs")
