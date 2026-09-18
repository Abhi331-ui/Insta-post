from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.post import Post, ScheduledPost
from backend.api.auth import get_current_user

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("")
def get_calendar(
    month: int = None,
    year: int = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns calendar events for content planning:
    - Topic summary
    - Content pillar color tag
    - Status badge (draft / pending_approval / scheduled / published / failed)
    - Publication or scheduled time
    """
    now = datetime.utcnow()
    # Default to 30 days window centered around now
    start_date = now - timedelta(days=15)
    end_date = now + timedelta(days=15)

    posts = (
        db.query(Post)
        .filter(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .limit(60)
        .all()
    )

    pillar_colors = {
        "AI Workflows & Automation": "#2563EB",
        "New Model & Tool Launches": "#8B5CF6",
        "Developer & Engineering Tools": "#10B981",
        "Productivity Experiments": "#F59E0B",
    }

    events = []
    for p in posts:
        event_time = p.scheduled_at or p.published_at or p.created_at
        pillar = p.content_pillar or "AI Workflows & Automation"
        events.append({
            "id": p.id,
            "topic": p.topic,
            "hook": p.hook,
            "content_pillar": pillar,
            "pillar_color": pillar_colors.get(pillar, "#2563EB"),
            "status": p.status,
            "date": event_time.strftime("%Y-%m-%d") if event_time else now.strftime("%Y-%m-%d"),
            "time": event_time.strftime("%H:%M") if event_time else "09:00",
            "slides_count": len(p.slides),
        })

    return events
