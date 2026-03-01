"""
Repost / Viral Sharing router.

Handles reposting existing posts and tracking viral spread via repost_count.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from models import posts_db, users_db

router = APIRouter(tags=["repost"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class RepostRequest(BaseModel):
    user_id: str
    caption: Optional[str] = None


class RepostResponse(BaseModel):
    id: str
    user_id: str
    original_post_id: str
    content_type: str
    content_url: str
    caption: Optional[str]
    repost_count: int
    like_count: int
    created_at: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/posts/{post_id}/repost",
    response_model=RepostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Repost an existing post",
)
def repost_post(post_id: str, body: RepostRequest) -> RepostResponse:
    """
    Create a new post entry that is a repost of *post_id*.

    - Copies ``content_type`` and ``content_url`` from the original.
    - Sets ``original_post_id`` to the original post's ID.
    - Increments ``repost_count`` on the original post.
    - Returns the newly created repost as a 201.
    """
    # Validate original post exists
    original = posts_db.get(post_id)
    if original is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post '{post_id}' not found.",
        )

    # Validate user exists
    if body.user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{body.user_id}' not found.",
        )

    # Build the new repost entry
    new_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc).isoformat()

    repost: dict = {
        "id": new_id,
        "user_id": body.user_id,
        "content_type": original["content_type"],
        "content_url": original["content_url"],
        "caption": body.caption,
        "created_at": now,
        "original_post_id": post_id,
        "repost_count": 0,
        "like_count": 0,
    }

    # Persist the new post
    posts_db[new_id] = repost

    # Increment repost_count on the original
    original["repost_count"] = original.get("repost_count", 0) + 1

    return RepostResponse(**repost)
