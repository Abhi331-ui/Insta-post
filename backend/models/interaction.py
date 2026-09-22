from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class InstagramInteraction(Base):
    __tablename__ = "instagram_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)

    # Type: "comment" or "dm"
    type = Column(String(20), default="comment", index=True)
    sender_username = Column(String(100), nullable=False)
    sender_id = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)

    # Keyword match & automation
    is_keyword_match = Column(Boolean, default=False)
    matched_keyword = Column(String(50), nullable=True)

    # Status: "pending", "replied", "dm_sent", "ignored"
    status = Column(String(50), default="pending", index=True)
    reply_content = Column(Text, nullable=True)
    dm_sent = Column(Boolean, default=False)

    external_id = Column(String(100), nullable=True, unique=True, index=True)  # comment_id or message_id
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    post = relationship("Post")
