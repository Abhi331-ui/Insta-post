from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    run_type = Column(String(50), default="daily_pipeline")  # daily_pipeline, manual, research_only, learning
    status = Column(String(50), default="running")  # running, completed, failed, no_opportunity
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    topics_researched = Column(Integer, default=0)
    topic_selected = Column(String(255), nullable=True)
    rejection_reasons = Column(JSON, default=list)
    error_message = Column(Text, nullable=True)

    user = relationship("User", back_populates="agent_runs")


class AIGeneration(Base):
    __tablename__ = "ai_generations"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    agent_name = Column(String(50), nullable=False)
    model_used = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    generated_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="ai_generations")
