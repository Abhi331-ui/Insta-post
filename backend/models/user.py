from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    brand_settings = relationship("BrandSetting", back_populates="user", uselist=False)
    content_pillars = relationship("ContentPillar", back_populates="user")
    instagram_account = relationship("InstagramAccount", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="user")
    agent_runs = relationship("AgentRun", back_populates="user")


class InstagramAccount(Base):
    __tablename__ = "instagram_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    instagram_user_id = Column(String(100), nullable=True)
    access_token = Column(String(500), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    page_name = Column(String(255), nullable=True)
    connected_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="instagram_account")


class BrandSetting(Base):
    __tablename__ = "brand_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Palette (Updated Dark/Cinematic Design System)
    primary_color = Column(String(30), default="#7C3AED")
    background_color = Column(String(30), default="#000000")
    text_color = Column(String(30), default="#FFFFFF")
    secondary_color = Column(String(30), default="#D1D5DB")

    # Brand Details
    brand_name = Column(String(100), default="PromptPulse")
    tagline = Column(String(255), default="Discover AI Worth Using")
    niche = Column(String(100), default="AI Tools & Productivity")

    # Schedule & Automation
    posting_time = Column(String(10), default="09:00")  # HH:MM format
    timezone = Column(String(50), default="UTC")
    active_days = Column(JSON, default=lambda: ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"])
    posts_per_day = Column(Integer, default=1)
    ai_provider = Column(String(20), default="gemini")
    auto_mode_enabled = Column(Boolean, default=False)
    webhook_url = Column(String(500), nullable=True)  # Discord, Slack, or Telegram webhook for daily reminders

    # Learned strategy recommendations from Learning Agent
    content_strategy = Column(JSON, default=dict)

    user = relationship("User", back_populates="brand_settings")


class ContentPillar(Base):
    __tablename__ = "content_pillars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    percentage = Column(Integer, default=25)
    description = Column(String(500), nullable=True)

    user = relationship("User", back_populates="content_pillars")
