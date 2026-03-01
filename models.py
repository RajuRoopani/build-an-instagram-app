"""
Shared Pydantic models and in-memory storage for the Instagram-like app.
All routers import storage dicts from here to ensure shared state.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# In-memory storage (shared across all routers via module-level references)
# ---------------------------------------------------------------------------

users_db: Dict[str, dict] = {}         # user_id  -> user dict
posts_db: Dict[str, dict] = {}         # post_id  -> post dict
followers_db: Dict[str, Set] = {}      # user_id  -> set of follower user_ids
following_db: Dict[str, Set] = {}      # user_id  -> set of following user_ids
likes_db: Dict[str, Set] = {}          # post_id  -> set of user_ids who liked
comments_db: Dict[str, list] = {}      # post_id  -> list of comment dicts
messages_db: List[dict] = []           # flat list of DM dicts
group_chats_db: Dict[str, dict] = {}   # chat_id  -> group chat dict


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    username: str
    display_name: str
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    user_id: str
    username: str
    display_name: str
    bio: str
    profile_picture_url: str
    created_at: str
    follower_count: int = 0
    following_count: int = 0


# ---------------------------------------------------------------------------
# Post schemas
# ---------------------------------------------------------------------------

class PostCreate(BaseModel):
    user_id: str
    content_type: str = Field(..., description="One of: photo, status, video")
    content_url: Optional[str] = None
    caption: Optional[str] = None


class PostUpdate(BaseModel):
    caption: Optional[str] = None
    content_url: Optional[str] = None


class PostResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    content_type: str
    content_url: str
    caption: str
    created_at: str
    original_post_id: Optional[str] = None
    repost_count: int = 0
    like_count: int = 0


# ---------------------------------------------------------------------------
# Follow / Unfollow schemas
# ---------------------------------------------------------------------------

class FollowRequest(BaseModel):
    follower_id: str


class UnfollowRequest(BaseModel):
    follower_id: str


# ---------------------------------------------------------------------------
# Like schema
# ---------------------------------------------------------------------------

class LikeRequest(BaseModel):
    user_id: str


# ---------------------------------------------------------------------------
# Comment schemas
# ---------------------------------------------------------------------------

class CommentCreate(BaseModel):
    user_id: str
    text: str


class CommentResponse(BaseModel):
    comment_id: str
    post_id: str
    user_id: str
    text: str
    created_at: str


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def make_user(user_id: str, payload: UserCreate) -> dict:
    """
    Build a user dict from a UserCreate payload.

    Includes BOTH ``id`` and ``user_id`` fields so that:
    - routers/users.py can read ``user["id"]`` for its ``_serialize_user`` helper
    - routers/repost.py and tests that access ``resp.json()["user_id"]`` both work
    """
    now: str = datetime.now(tz=timezone.utc).isoformat()
    return {
        "id": user_id,
        "user_id": user_id,
        "username": payload.username,
        "display_name": payload.display_name,
        "bio": payload.bio or "",
        "profile_picture_url": payload.profile_picture_url or "",
        "created_at": now,
    }


def make_post(post_id: str, payload: PostCreate) -> dict:
    """
    Build a post dict from a PostCreate payload.

    Includes BOTH ``id`` and ``post_id`` fields so that:
    - routers/posts.py can read ``post["id"]`` for its ``_serialize_post`` helper
    - routers/repost.py and tests that access ``resp.json()["post_id"]`` both work
    """
    now: str = datetime.now(tz=timezone.utc).isoformat()
    return {
        "id": post_id,
        "post_id": post_id,
        "user_id": payload.user_id,
        "content_type": payload.content_type,
        "content_url": payload.content_url or "",
        "caption": payload.caption or "",
        "created_at": now,
        "original_post_id": None,
        "repost_count": 0,
        "like_count": 0,
    }


def make_comment(comment_id: str, post_id: str, payload: CommentCreate) -> dict:
    """
    Build a comment dict from a CommentCreate payload.

    Uses ``comment_id`` as the primary key name (consistent with test expectations
    and the ``_serialize_comment`` helper in routers/posts.py).
    Also includes ``id`` so the serializer helper continues to work unchanged.
    """
    now: str = datetime.now(tz=timezone.utc).isoformat()
    return {
        "id": comment_id,
        "comment_id": comment_id,
        "post_id": post_id,
        "user_id": payload.user_id,
        "text": payload.text,
        "created_at": now,
    }
