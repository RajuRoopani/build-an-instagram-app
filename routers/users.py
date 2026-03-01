"""
Users router — handles user CRUD and follow/unfollow operations.
Response format uses field names aligned with test expectations:
  - user dict exposes "user_id" (not "id")
  - followers/following return list of {"user_id": ...} objects
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from models import (
    UserCreate,
    UserUpdate,
    FollowRequest,
    make_user,
    users_db,
    followers_db,
    following_db,
)

router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_user_or_404(user_id: str) -> dict:
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    return user


def _serialize_user(user: dict) -> dict:
    """Return user dict with 'user_id' key and follower/following counts."""
    uid = user["id"]
    return {
        "user_id": uid,
        "username": user["username"],
        "display_name": user["display_name"],
        "bio": user["bio"],
        "profile_picture_url": user["profile_picture_url"],
        "created_at": user["created_at"],
        "follower_count": len(followers_db.get(uid, set())),
        "following_count": len(following_db.get(uid, set())),
    }


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
def create_user(payload: UserCreate) -> JSONResponse:
    """Create a new user profile. Returns 201 with the created user."""
    user_id = str(uuid.uuid4())
    user = make_user(user_id, payload)
    users_db[user_id] = user
    followers_db[user_id] = set()
    following_db[user_id] = set()
    return JSONResponse(status_code=201, content=_serialize_user(user))


@router.get("/{user_id}", status_code=200)
def get_user(user_id: str) -> dict:
    """Get a user profile by ID. Returns 404 if not found."""
    user = _get_user_or_404(user_id)
    return _serialize_user(user)


@router.put("/{user_id}", status_code=200)
def update_user(user_id: str, payload: UserUpdate) -> dict:
    """Partial update of a user profile. Only supplied fields are updated."""
    user = _get_user_or_404(user_id)
    updates = payload.model_dump(exclude_unset=True)
    user.update(updates)
    users_db[user_id] = user
    return _serialize_user(user)


# ---------------------------------------------------------------------------
# Follow system
# ---------------------------------------------------------------------------

@router.post("/{user_id}/follow", status_code=200)
def follow_user(user_id: str, payload: FollowRequest) -> dict:
    """
    Follow a user.
    - user_id: the user to follow (target)
    - payload.follower_id: the user who is following
    Returns 404 if either user does not exist, 400 if trying to follow yourself.
    """
    _get_user_or_404(user_id)
    _get_user_or_404(payload.follower_id)

    if user_id == payload.follower_id:
        raise HTTPException(status_code=400, detail="A user cannot follow themselves")

    followers_db.setdefault(user_id, set()).add(payload.follower_id)
    following_db.setdefault(payload.follower_id, set()).add(user_id)

    return {"detail": f"User '{payload.follower_id}' is now following '{user_id}'"}


@router.delete("/{user_id}/follow", status_code=200)
async def unfollow_user(
    user_id: str,
    request: Request,
    follower_id: Optional[str] = Query(default=None),
) -> dict:
    """
    Unfollow a user.
    Accepts query param follower_id OR JSON body {"follower_id": ...}.
    Returns 404 if either user does not exist.
    """
    # Prefer query param; fall back to JSON body
    resolved_follower_id: str = follower_id or ""
    if not resolved_follower_id:
        try:
            body = await request.json()
            resolved_follower_id = body.get("follower_id", "")
        except Exception:
            resolved_follower_id = ""

    if not resolved_follower_id:
        raise HTTPException(status_code=422, detail="follower_id is required")

    _get_user_or_404(user_id)
    _get_user_or_404(resolved_follower_id)

    followers_db.setdefault(user_id, set()).discard(resolved_follower_id)
    following_db.setdefault(resolved_follower_id, set()).discard(user_id)

    return {"detail": f"User '{resolved_follower_id}' has unfollowed '{user_id}'"}


@router.get("/{user_id}/followers", status_code=200)
def get_followers(user_id: str) -> List[dict]:
    """Get list of followers as [{"user_id": ...}, ...] objects."""
    _get_user_or_404(user_id)
    follower_ids = list(followers_db.get(user_id, set()))
    return [{"user_id": fid} for fid in follower_ids]


@router.get("/{user_id}/following", status_code=200)
def get_following(user_id: str) -> List[dict]:
    """Get list of followed users as [{"user_id": ...}, ...] objects."""
    _get_user_or_404(user_id)
    following_ids = list(following_db.get(user_id, set()))
    return [{"user_id": fid} for fid in following_ids]


# ---------------------------------------------------------------------------
# Posts by user
# ---------------------------------------------------------------------------

@router.get("/{user_id}/posts", status_code=200)
def get_user_posts(user_id: str) -> List[dict]:
    """Get all posts created by a specific user, newest first."""
    from models import posts_db  # local import to avoid circular-import edge cases

    _get_user_or_404(user_id)
    user_posts = [_serialize_post(p) for p in posts_db.values() if p["user_id"] == user_id]
    user_posts.sort(key=lambda p: p["created_at"], reverse=True)
    return user_posts


def _serialize_post(post: dict) -> dict:
    """Return post dict with 'post_id' key."""
    return {
        "post_id": post["id"],
        **{k: v for k, v in post.items() if k != "id"},
    }
