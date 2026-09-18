import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.database import init_db, SessionLocal
from backend.main import app
from backend.models.user import User
from backend.models.queue import TopicQueueItem


def test_batch_queue_submission():
    """Verify submitting 10 topics assigns consecutive daily dates."""
    init_db()
    client = TestClient(app)

    topics = [
        "1. Bolt.new In-Browser Runtime Breakthrough",
        "2. OpenAI Canvas Interface vs Traditional Editors",
        "3. Cursor Composer 20-File Orchestration",
        "4. v0.dev Next.js Component Generation",
        "5. Claude 3.5 Sonnet Artifacts for Productivity",
        "6. Perplexity Pro Computer Interaction Workflows",
        "7. NotebookLM Dual-Host Audio Synthesis",
        "8. Devin AI Autonomous Software Engineering Review",
        "9. Replit Agent Full-Stack Autonomous Deployments",
        "10. Supabase AI Auto-Migrate Vector Search",
    ]

    tomorrow_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    response = client.post("/api/queue/batch", json={"topics": topics, "start_date": tomorrow_str})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 10
    assert len(data["items"]) == 10

    # Verify consecutive days (Day 1 to Day 10)
    for idx, item in enumerate(data["items"]):
        assert item["day_index"] == idx + 1
        item_date = datetime.fromisoformat(item["scheduled_date"])
        expected_date = datetime.strptime(tomorrow_str, "%Y-%m-%d") + timedelta(days=idx)
        assert item_date.day == expected_date.day

    # Verify GET /api/queue
    get_res = client.get("/api/queue")
    assert get_res.status_code == 200
    q_data = get_res.json()
    assert len(q_data["items"]) >= 10
    assert q_data["stats"]["days_covered"] >= 10
