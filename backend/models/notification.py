from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    type = Column(String(50), default="post_published")  # post_published, refill_reminder, system
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255), default="/queue")
    is_read = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
