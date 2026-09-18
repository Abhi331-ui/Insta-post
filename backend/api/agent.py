import asyncio
import json
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.pipeline.daily_pipeline import daily_pipeline, current_pipeline_state

router = APIRouter(prefix="/api", tags=["agent"])


@router.get("/agent-status")
async def get_agent_status_sse():
    """
    Server-Sent Events (SSE) stream broadcasting live agent pipeline progress:
    Research -> Score -> Select -> Write -> Design -> Fact Check -> QA -> Publish
    """
    async def event_generator():
        last_state = ""
        while True:
            current_json = json.dumps(current_pipeline_state)
            if current_json != last_state:
                yield f"data: {current_json}\n\n"
                last_state = current_json
            await asyncio.sleep(0.8)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/agent/status-json")
def get_agent_status_json():
    """Direct JSON snapshot of current agent pipeline state."""
    return current_pipeline_state


@router.post("/agent/run-now")
async def run_agent_now(
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """Triggers autonomous discovery pipeline immediately."""
    background_tasks.add_task(daily_pipeline.run_daily_pipeline, user_id=user.id)
    return {
        "success": True,
        "message": "Autonomous content pipeline triggered. Follow live progress on the dashboard status bar.",
    }
