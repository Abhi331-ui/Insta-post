from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.models.notification import Notification
from backend.api.auth import get_current_user
from backend.services.notification import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def get_notifications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns list of notifications and unread count."""
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(30)
        .all()
    )

    unread_count = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.is_read == False)
        .count()
    )

    return {
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
                "time_display": n.created_at.strftime("%b %d, %I:%M %p"),
            }
            for n in notifs
        ],
    }


@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks a single notification as read."""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")

    notif.is_read = True
    db.commit()
    return {"success": True}


@router.post("/read-all")
def mark_all_as_read(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks all notifications as read for current user."""
    db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"success": True}


@router.post("/test-reminder")
def trigger_test_reminder(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Triggers an instant post-publish reminder notification for verification."""
    from backend.models.post import Post
    latest_post = db.query(Post).filter(Post.user_id == user.id).first()
    post_id = latest_post.id if latest_post else 1

    notif = notification_service.send_post_publish_reminder(
        post_id=post_id,
        user_id=user.id,
        db=db,
        simulated=True,
    )
    return {
        "success": True,
        "notification_id": notif.id,
        "title": notif.title,
        "message": notif.message,
    }
