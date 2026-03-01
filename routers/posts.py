"""
Posts router — handles post CRUD, feed, likes and comments.
Response format uses field names aligned with test expectations:
  - post dict exposes "post_id" (not "id")
  - comment dict exposes "comment_id" (not "id")
  - feed and user-posts return lists directly
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from models import (
    PostCreate,
    CommentCreate,
    make_post,
    make_comment,
    users_db,
    posts_db,
    likes_db,
    comments_db,
    following_db,
)

router = APIRouter(tags=["posts"])

VALID_CONTENT_TYPES = {"photo", "status", "video"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_post_or_404(post_id: str) -> dict:
    post = posts_db.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post '{post_id}' not found")
    return post


def _get_user_or_404(user_id: str) -> dict:
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    return user


def _serialize_post(post: dict) -> dict:
    """Return post dict with 'post_id' key instead of 'id'."""
    return {
        "post_id": post["id"],
        **{k: v for k, v in post.items() if k != "id"},
    }


def _serialize_comment(comment: dict) -> dict:
    """Return comment dict with 'comment_id' key instead of 'id'."""
    return {
        "comment_id": comment["id"],
        **{k: v for k, v in comment.items() if k != "id"},
    }


# ---------------------------------------------------------------------------
# Post CRUD
# ---------------------------------------------------------------------------

@router.post("/posts", status_code=201)
def create_post(payload: PostCreate) -> JSONResponse:
    """
    Create a new post.
    Validates that the author user exists and content_type is valid.
    Returns 201 with the created post.
    """
    _get_user_or_404(payload.user_id)

    if payload.content_type not in VALID_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"content_type must be one of {sorted(VALID_CONTENT_TYPES)}",
        )

    post_id = str(uuid.uuid4())
    post = make_post(post_id, payload)
    posts_db[post_id] = post
    likes_db[post_id] = set()
    comments_db[post_id] = []

    return JSONResponse(status_code=201, content=_serialize_post(post))


@router.get("/posts/{post_id}", status_code=200)
def get_post(post_id: str) -> dict:
    """Get a single post by ID including like_count and repost_count."""
    return _serialize_post(_get_post_or_404(post_id))


@router.get("/feed", status_code=200)
def get_feed(user_id: Optional[str] = Query(default=None)) -> List[dict]:
    """
    Get the post feed as a list (not wrapped in a dict).
    - If user_id is provided, return only posts from users that user follows
      plus the user's own posts.
    - Otherwise return all posts, newest first.
    """
    if user_id is not None:
        _get_user_or_404(user_id)
        # Include posts by the user themselves AND by users they follow
        followed = following_db.get(user_id, set()) | {user_id}
        feed_posts = [_serialize_post(p) for p in posts_db.values() if p["user_id"] in followed]
    else:
        feed_posts = [_serialize_post(p) for p in posts_db.values()]

    feed_posts.sort(key=lambda p: p["created_at"], reverse=True)
    return feed_posts


# ---------------------------------------------------------------------------
# Likes
# ---------------------------------------------------------------------------

@router.post("/posts/{post_id}/likes", status_code=200)
def like_post(post_id: str, payload: dict) -> dict:
    """
    Like a post.
    Body: {"user_id": "<user_id>"}
    Idempotent — liking the same post twice has no additional effect.
    Increments like_count on the post.
    """
    user_id: str = payload.get("user_id", "")
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id is required")

    _get_user_or_404(user_id)
    post = _get_post_or_404(post_id)

    post_likes: set = likes_db.setdefault(post_id, set())
    if user_id not in post_likes:
        post_likes.add(user_id)
        post["like_count"] = len(post_likes)

    return {"post_id": post_id, "like_count": post["like_count"]}


@router.delete("/posts/{post_id}/likes", status_code=200)
async def unlike_post(
    post_id: str,
    request: Request,
    user_id: Optional[str] = Query(default=None),
) -> dict:
    """
    Unlike a post.
    Accepts query param user_id OR JSON body {"user_id": ...}.
    Idempotent — unliking a post you haven't liked is a no-op.
    Decrements like_count on the post.
    """
    # Prefer query param; fall back to JSON body
    resolved_user_id: str = user_id or ""
    if not resolved_user_id:
        try:
            body = await request.json()
            resolved_user_id = body.get("user_id", "")
        except Exception:
            resolved_user_id = ""

    if not resolved_user_id:
        raise HTTPException(status_code=422, detail="user_id is required")

    # Check post first so a nonexistent post always returns 404 (not user 404)
    post = _get_post_or_404(post_id)
    _get_user_or_404(resolved_user_id)

    post_likes: set = likes_db.setdefault(post_id, set())
    if resolved_user_id in post_likes:
        post_likes.discard(resolved_user_id)
        post["like_count"] = len(post_likes)

    return {"post_id": post_id, "like_count": post["like_count"]}


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

@router.post("/posts/{post_id}/comments", status_code=201)
def add_comment(post_id: str, payload: CommentCreate) -> JSONResponse:
    """
    Add a comment to a post.
    Returns 201 with the created comment (uses 'comment_id' field).
    """
    _get_user_or_404(payload.user_id)
    _get_post_or_404(post_id)

    comment_id = str(uuid.uuid4())
    comment = make_comment(comment_id, post_id, payload)
    comments_db.setdefault(post_id, []).append(comment)

    return JSONResponse(status_code=201, content=_serialize_comment(comment))


@router.get("/posts/{post_id}/comments", status_code=200)
def get_comments(post_id: str) -> List[dict]:
    """Get all comments on a post as a list (oldest first)."""
    _get_post_or_404(post_id)
    return [_serialize_comment(c) for c in comments_db.get(post_id, [])]
