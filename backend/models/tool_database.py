from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from backend.database import Base


class ToolDatabase(Base):
    __tablename__ = "tool_database"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    website = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)  # productivity, dev, design, video, writing, audio, automation
    description = Column(Text, nullable=True)
    features = Column(JSON, default=list)
    is_free = Column(Boolean, default=True)
    pricing_details = Column(String(255), nullable=True)
    use_cases = Column(JSON, default=list)
    target_audience = Column(JSON, default=list)
    verified_sources = Column(JSON, default=list)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
