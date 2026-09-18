import pytest
from fastapi.testclient import TestClient

from backend.database import init_db, SessionLocal
from backend.main import app
from backend.models.user import User, BrandSetting
from backend.models.post import Post
from backend.models.notification import Notification
from backend.services.notification import notification_service


def test_post_publish_notification():
    """Verify that publishing triggers notification reminding user of next 10 ideas."""
    init_db()
    client = TestClient(app)
    db = SessionLocal()

    try:
        user = db.query(User).first()
        assert user is not None

        post = db.query(Post).filter(Post.user_id == user.id).first()
        if not post:
            post = Post(user_id=user.id, topic="Test Carousel", hook="Test hook", status="published")
            db.add(post)
            db.commit()

        # Trigger reminder
        notif = notification_service.send_post_publish_reminder(
            post_id=post.id,
            user_id=user.id,
            db=db,
            simulated=True,
        )

        assert notif is not None
        assert "Carousel Published" in notif.title
        assert "next 10 trending ideas" in notif.message
        assert notif.link == "/queue"
        assert notif.is_read is False

        # Verify API endpoint
        res = client.get("/api/notifications")
        assert res.status_code == 200
        data = res.json()
        assert data["unread_count"] >= 1
        assert len(data["notifications"]) >= 1

        # Mark as read
        notif_id = data["notifications"][0]["id"]
        read_res = client.post(f"/api/notifications/{notif_id}/read")
        assert read_res.status_code == 200

        # Mark all read
        read_all_res = client.post("/api/notifications/read-all")
        assert read_all_res.status_code == 200

        res_after = client.get("/api/notifications")
        assert res_after.json()["unread_count"] == 0
        print("[OK] All notification tests passed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    test_post_publish_notification()

