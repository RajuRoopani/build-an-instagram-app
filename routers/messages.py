"""
Messaging router — Personal DMs and Group Chats.

Provides endpoints for:
- Sending and retrieving direct messages between two users.
- Creating group chats and posting / retrieving messages within them.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from models import messages_db, group_chats_db

router = APIRouter(tags=["messages"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class SendDMRequest(BaseModel):
    sender_id: str
    recipient_id: str
    text: str


class DMResponse(BaseModel):
    id: str
    sender_id: str
    recipient_id: str
    text: str
    created_at: str


class CreateGroupChatRequest(BaseModel):
    name: str
    member_ids: List[str]


class GroupChatResponse(BaseModel):
    id: str
    name: str
    member_ids: List[str]
    messages: List[dict]


class GroupMessageRequest(BaseModel):
    sender_id: str
    text: str


class GroupMessageResponse(BaseModel):
    id: str
    sender_id: str
    text: str
    created_at: str


# ---------------------------------------------------------------------------
# Personal DM Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/messages",
    response_model=DMResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a direct message",
)
def send_dm(body: SendDMRequest) -> DMResponse:
    """
    Send a direct message from ``sender_id`` to ``recipient_id``.

    The message is stored in ``messages_db`` (a list).
    """
    now = datetime.now(tz=timezone.utc).isoformat()
    message: dict = {
        "id": str(uuid.uuid4()),
        "sender_id": body.sender_id,
        "recipient_id": body.recipient_id,
        "text": body.text,
        "created_at": now,
    }
    messages_db.append(message)
    return DMResponse(**message)


@router.get(
    "/messages",
    response_model=List[DMResponse],
    status_code=status.HTTP_200_OK,
    summary="Get conversation between two users",
)
def get_conversation(
    user1: str = Query(..., description="First user ID"),
    user2: str = Query(..., description="Second user ID"),
) -> List[DMResponse]:
    """
    Retrieve all direct messages exchanged between ``user1`` and ``user2``
    in either direction, ordered by creation time (ascending).
    """
    conversation = [
        msg
        for msg in messages_db
        if (msg["sender_id"] == user1 and msg["recipient_id"] == user2)
        or (msg["sender_id"] == user2 and msg["recipient_id"] == user1)
    ]
    # Sort chronologically
    conversation.sort(key=lambda m: m["created_at"])
    return [DMResponse(**m) for m in conversation]


# ---------------------------------------------------------------------------
# Group Chat Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/group-chats",
    response_model=GroupChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a group chat",
)
def create_group_chat(body: CreateGroupChatRequest) -> GroupChatResponse:
    """
    Create a new group chat with the given ``name`` and initial ``member_ids``.
    Stored in ``group_chats_db`` keyed by chat ID.
    """
    chat_id = str(uuid.uuid4())
    chat: dict = {
        "id": chat_id,
        "name": body.name,
        "member_ids": list(body.member_ids),
        "messages": [],
    }
    group_chats_db[chat_id] = chat
    return GroupChatResponse(**chat)


@router.post(
    "/group-chats/{chat_id}/messages",
    response_model=GroupMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message to a group chat",
)
def send_group_message(chat_id: str, body: GroupMessageRequest) -> GroupMessageResponse:
    """
    Append a message to the group chat identified by ``chat_id``.
    Returns 404 if the chat does not exist.
    """
    chat = group_chats_db.get(chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group chat '{chat_id}' not found.",
        )

    now = datetime.now(tz=timezone.utc).isoformat()
    message: dict = {
        "id": str(uuid.uuid4()),
        "sender_id": body.sender_id,
        "text": body.text,
        "created_at": now,
    }
    chat["messages"].append(message)
    return GroupMessageResponse(**message)


@router.get(
    "/group-chats/{chat_id}/messages",
    response_model=List[GroupMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all messages in a group chat",
)
def get_group_messages(chat_id: str) -> List[GroupMessageResponse]:
    """
    Retrieve all messages in the group chat identified by ``chat_id``.
    Returns 404 if the chat does not exist.
    """
    chat = group_chats_db.get(chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group chat '{chat_id}' not found.",
        )
    return [GroupMessageResponse(**m) for m in chat["messages"]]
