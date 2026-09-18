from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    profile_visits = Column(Integer, default=0)
    follows = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    collected_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="analytics_records")
