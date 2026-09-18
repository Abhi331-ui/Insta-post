from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class TopicQueueItem(Base):
    __tablename__ = "topic_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    batch_id = Column(String(50), nullable=False, index=True)
    topic = Column(String(255), nullable=False)

    scheduled_date = Column(DateTime, nullable=False, index=True)
    day_index = Column(Integer, nullable=False)  # 1 to 10

    # Status: pending, generating, ready, published, cancelled
    status = Column(String(50), default="pending", index=True)

    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    post = relationship("Post")
