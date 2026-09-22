import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models.user import User, InstagramAccount
from backend.models.interaction import InstagramInteraction
from backend.api.auth import get_current_user
from backend.services.instagram import instagram_service
from backend.services.engagement_service import engagement_service

logger = logging.getLogger("PromptPulse.InteractionsAPI")

router = APIRouter(prefix="/api/interactions", tags=["interactions"])


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    post_id: Optional[int] = None
    type: str
    external_id: Optional[str] = None
    sender_id: Optional[str] = None
    sender_username: Optional[str] = None
    content: str
    is_keyword_match: bool
    matched_keyword: Optional[str] = None
    status: str
    reply_content: Optional[str] = None
    dm_sent: bool
    created_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ManualReplyRequest(BaseModel):
    reply_message: str
    send_dm: bool = False


class InteractionStatsResponse(BaseModel):
    total_interactions: int
    total_comments: int
    total_dms: int
    keyword_matches: int
    auto_dms_sent: int
    pending_count: int


@router.get("", response_model=List[InteractionResponse])
def get_interactions(
    type: Optional[str] = Query(None, description="Filter by type: 'comment' or 'dm'"),
    status: Optional[str] = Query(None, description="Filter by status: 'pending', 'replied', or 'ignored'"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List Instagram interactions (comments & DMs) for the current user."""
    query = db.query(InstagramInteraction).filter(InstagramInteraction.user_id == current_user.id)
    if type:
        query = query.filter(InstagramInteraction.type == type)
    if status:
        query = query.filter(InstagramInteraction.status == status)

    interactions = query.order_by(desc(InstagramInteraction.created_at)).offset(offset).limit(limit).all()
    return interactions


@router.get("/stats", response_model=InteractionStatsResponse)
def get_interaction_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get interaction counters and automation metrics for current user."""
    base_query = db.query(InstagramInteraction).filter(InstagramInteraction.user_id == current_user.id)
    total = base_query.count()
    comments = base_query.filter(InstagramInteraction.type == "comment").count()
    dms = base_query.filter(InstagramInteraction.type == "dm").count()
    keyword_matches = base_query.filter(InstagramInteraction.is_keyword_match == True).count()
    auto_dms_sent = base_query.filter(InstagramInteraction.dm_sent == True).count()
    pending = base_query.filter(InstagramInteraction.status == "pending").count()

    return InteractionStatsResponse(
        total_interactions=total,
        total_comments=comments,
        total_dms=dms,
        keyword_matches=keyword_matches,
        auto_dms_sent=auto_dms_sent,
        pending_count=pending,
    )


@router.post("/check-now")
def trigger_manual_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger an immediate check of comments and DMs on the user's Instagram account."""
    try:
        results = engagement_service.process_user_interactions(current_user.id, db)
        return {
            "status": "success",
            "message": "Engagement check completed successfully.",
            "data": results,
        }
    except Exception as e:
        logger.error(f"Error checking interactions for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{interaction_id}/reply")
def reply_to_interaction(
    interaction_id: int,
    req: ManualReplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a manual reply (comment reply or direct message) to an interaction."""
    interaction = (
        db.query(InstagramInteraction)
        .filter(InstagramInteraction.id == interaction_id, InstagramInteraction.user_id == current_user.id)
        .first()
    )
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found.")

    account = (
        db.query(InstagramAccount)
        .filter(InstagramAccount.user_id == current_user.id)
        .first()
    )
    access_token = account.access_token if account else None

    # Perform reply via Instagram service
    try:
        if interaction.type == "comment":
            if req.send_dm:
                # Private reply DM to commenter
                dm_res = instagram_service.send_private_reply(
                    comment_id=interaction.external_id or "",
                    message=req.reply_message,
                    access_token=access_token,
                )
                interaction.dm_sent = dm_res.get("success", False) or dm_res.get("status") == "success"
            else:
                # Public comment reply
                instagram_service.reply_to_comment(
                    comment_id=interaction.external_id or "",
                    message=req.reply_message,
                    access_token=access_token,
                )
        elif interaction.type == "dm":
            dm_res = instagram_service.send_direct_message(
                recipient_id=interaction.sender_id or "",
                message=req.reply_message,
                access_token=access_token,
            )
            interaction.dm_sent = dm_res.get("success", False) or dm_res.get("status") == "success"

        interaction.status = "replied"
        interaction.reply_content = req.reply_message
        interaction.replied_at = datetime.utcnow()
        db.commit()
        db.refresh(interaction)

        return {
            "status": "success",
            "message": "Reply sent successfully.",
            "interaction": InteractionResponse.from_orm(interaction),
        }
    except Exception as e:
        logger.error(f"Failed to send reply to interaction {interaction_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {str(e)}")


@router.post("/{interaction_id}/ignore")
def ignore_interaction(
    interaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an interaction as ignored."""
    interaction = (
        db.query(InstagramInteraction)
        .filter(InstagramInteraction.id == interaction_id, InstagramInteraction.user_id == current_user.id)
        .first()
    )
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found.")

    interaction.status = "ignored"
    db.commit()
    return {"status": "success", "message": "Interaction ignored."}
