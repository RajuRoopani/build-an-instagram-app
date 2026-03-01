"""
Test suite for Repost and Messaging features.

Tests cover:
- Creating reposts and verifying repost_count increments
- Sending direct messages and retrieving conversations
- Creating group chats and sending/retrieving group messages
"""

import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_storage():
    """Clear all in-memory storage before each test."""
    from models import (
        users_db,
        posts_db,
        followers_db,
        following_db,
        likes_db,
        comments_db,
        messages_db,
        group_chats_db,
    )

    users_db.clear()
    posts_db.clear()
    followers_db.clear()
    following_db.clear()
    likes_db.clear()
    comments_db.clear()
    messages_db.clear()
    group_chats_db.clear()


# ---------------------------------------------------------------------------
# Helper functions to create test data
# ---------------------------------------------------------------------------

def create_test_user(username: str = "testuser", display_name: str = "Test User"):
    """Create a user and return the response."""
    return client.post(
        "/users",
        json={
            "username": username,
            "display_name": display_name,
            "bio": "Test bio",
            "profile_picture_url": "http://pic.jpg",
        },
    )


def create_test_post(user_id: str, caption: str = "test post"):
    """Create a post and return the response."""
    return client.post(
        "/posts",
        json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://img.jpg",
            "caption": caption,
        },
    )


# ---------------------------------------------------------------------------
# Repost Tests
# ---------------------------------------------------------------------------

def test_repost_create_success():
    """Test creating a repost successfully."""
    # Create a user and a post
    user_resp = create_test_user(username="user1")
    assert user_resp.status_code == 201
    user_id = user_resp.json()["user_id"]

    post_resp = create_test_post(user_id, "Original post")
    assert post_resp.status_code == 201
    post_id = post_resp.json()["post_id"]

    # Create another user to repost
    user2_resp = create_test_user(username="user2")
    assert user2_resp.status_code == 201
    user2_id = user2_resp.json()["user_id"]

    # Repost the post
    repost_resp = client.post(
        f"/posts/{post_id}/repost",
        json={"user_id": user2_id, "caption": "Reposting this!"},
    )

    assert repost_resp.status_code == 201
    repost_data = repost_resp.json()
    assert repost_data["user_id"] == user2_id
    assert repost_data["original_post_id"] == post_id
    assert repost_data["caption"] == "Reposting this!"
    assert repost_data["content_type"] == "photo"
    assert repost_data["content_url"] == "http://img.jpg"


def test_repost_increments_count():
    """Test that reposting increments the original post's repost_count."""
    # Create a user and a post
    user_resp = create_test_user(username="user1")
    user_id = user_resp.json()["user_id"]

    post_resp = create_test_post(user_id, "Original post")
    post_id = post_resp.json()["post_id"]

    # Verify initial repost_count is 0
    get_post_resp = client.get(f"/posts/{post_id}")
    assert get_post_resp.json()["repost_count"] == 0

    # Create another user and repost
    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    repost_resp = client.post(
        f"/posts/{post_id}/repost",
        json={"user_id": user2_id},
    )
    assert repost_resp.status_code == 201

    # Verify repost_count incremented
    get_post_resp = client.get(f"/posts/{post_id}")
    assert get_post_resp.json()["repost_count"] == 1

    # Repost again with a third user
    user3_resp = create_test_user(username="user3")
    user3_id = user3_resp.json()["user_id"]

    repost_resp2 = client.post(
        f"/posts/{post_id}/repost",
        json={"user_id": user3_id},
    )
    assert repost_resp2.status_code == 201

    # Verify repost_count is now 2
    get_post_resp = client.get(f"/posts/{post_id}")
    assert get_post_resp.json()["repost_count"] == 2


def test_repost_nonexistent_post():
    """Test reposting a nonexistent post returns 404."""
    # Create a user
    user_resp = create_test_user(username="user1")
    user_id = user_resp.json()["user_id"]

    # Try to repost a nonexistent post
    repost_resp = client.post(
        "/posts/nonexistent/repost",
        json={"user_id": user_id},
    )

    assert repost_resp.status_code == 404


def test_repost_nonexistent_user():
    """Test reposting with a nonexistent user returns 404."""
    # Create a user and a post
    user_resp = create_test_user(username="user1")
    user_id = user_resp.json()["user_id"]

    post_resp = create_test_post(user_id, "Original post")
    post_id = post_resp.json()["post_id"]

    # Try to repost with a nonexistent user
    repost_resp = client.post(
        f"/posts/{post_id}/repost",
        json={"user_id": "nonexistent_user"},
    )

    assert repost_resp.status_code == 404


def test_repost_copies_content():
    """Test that a repost copies content_type and content_url from original."""
    # Create user and post with specific content
    user_resp = create_test_user(username="user1")
    user_id = user_resp.json()["user_id"]

    post_resp = client.post(
        "/posts",
        json={
            "user_id": user_id,
            "content_type": "video",
            "content_url": "http://video.mp4",
            "caption": "My video",
        },
    )
    post_id = post_resp.json()["post_id"]

    # Create another user and repost
    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    repost_resp = client.post(
        f"/posts/{post_id}/repost",
        json={"user_id": user2_id},
    )

    repost_data = repost_resp.json()
    assert repost_data["content_type"] == "video"
    assert repost_data["content_url"] == "http://video.mp4"


# ---------------------------------------------------------------------------
# Direct Message Tests
# ---------------------------------------------------------------------------

def test_send_dm_success():
    """Test sending a direct message successfully."""
    # Create two users
    user1_resp = create_test_user(username="user1")
    user1_id = user1_resp.json()["user_id"]

    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    # Send DM
    dm_resp = client.post(
        "/messages",
        json={
            "sender_id": user1_id,
            "recipient_id": user2_id,
            "text": "Hello user2!",
        },
    )

    assert dm_resp.status_code == 201
    dm_data = dm_resp.json()
    assert dm_data["sender_id"] == user1_id
    assert dm_data["recipient_id"] == user2_id
    assert dm_data["text"] == "Hello user2!"


def test_get_conversation():
    """Test retrieving a conversation between two users."""
    # Create two users
    user1_resp = create_test_user(username="user1")
    user1_id = user1_resp.json()["user_id"]

    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    # Send messages in both directions
    msg1 = client.post(
        "/messages",
        json={
            "sender_id": user1_id,
            "recipient_id": user2_id,
            "text": "Hello from user1",
        },
    )
    assert msg1.status_code == 201

    msg2 = client.post(
        "/messages",
        json={
            "sender_id": user2_id,
            "recipient_id": user1_id,
            "text": "Hello from user2",
        },
    )
    assert msg2.status_code == 201

    # Retrieve conversation
    conv_resp = client.get(
        "/messages",
        params={"user1": user1_id, "user2": user2_id},
    )

    assert conv_resp.status_code == 200
    messages = conv_resp.json()
    assert len(messages) == 2

    # Messages should be ordered chronologically
    assert messages[0]["sender_id"] == user1_id
    assert messages[1]["sender_id"] == user2_id


def test_get_conversation_one_direction():
    """Test that conversation query works regardless of user order."""
    # Create two users
    user1_resp = create_test_user(username="user1")
    user1_id = user1_resp.json()["user_id"]

    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    # Send messages
    client.post(
        "/messages",
        json={
            "sender_id": user1_id,
            "recipient_id": user2_id,
            "text": "Message 1",
        },
    )

    # Get conversation with reversed user order
    conv_resp = client.get(
        "/messages",
        params={"user1": user2_id, "user2": user1_id},
    )

    assert conv_resp.status_code == 200
    messages = conv_resp.json()
    assert len(messages) == 1
    assert messages[0]["text"] == "Message 1"


# ---------------------------------------------------------------------------
# Group Chat Tests
# ---------------------------------------------------------------------------

def test_create_group_chat_success():
    """Test creating a group chat successfully."""
    # Create users
    user1_resp = create_test_user(username="user1")
    user1_id = user1_resp.json()["user_id"]

    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    user3_resp = create_test_user(username="user3")
    user3_id = user3_resp.json()["user_id"]

    # Create group chat
    group_resp = client.post(
        "/group-chats",
        json={
            "name": "Friends Group",
            "member_ids": [user1_id, user2_id, user3_id],
        },
    )

    assert group_resp.status_code == 201
    group_data = group_resp.json()
    assert group_data["name"] == "Friends Group"
    assert set(group_data["member_ids"]) == {user1_id, user2_id, user3_id}
    assert group_data["messages"] == []


def test_send_group_message_success():
    """Test sending a message to a group chat."""
    # Create users and group chat
    user1_resp = create_test_user(username="user1")
    user1_id = user1_resp.json()["user_id"]

    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    group_resp = client.post(
        "/group-chats",
        json={
            "name": "Test Group",
            "member_ids": [user1_id, user2_id],
        },
    )
    group_id = group_resp.json()["id"]

    # Send message to group
    msg_resp = client.post(
        f"/group-chats/{group_id}/messages",
        json={
            "sender_id": user1_id,
            "text": "Hello everyone!",
        },
    )

    assert msg_resp.status_code == 201
    msg_data = msg_resp.json()
    assert msg_data["sender_id"] == user1_id
    assert msg_data["text"] == "Hello everyone!"


def test_get_group_messages():
    """Test retrieving messages from a group chat."""
    # Create users and group chat
    user1_resp = create_test_user(username="user1")
    user1_id = user1_resp.json()["user_id"]

    user2_resp = create_test_user(username="user2")
    user2_id = user2_resp.json()["user_id"]

    group_resp = client.post(
        "/group-chats",
        json={
            "name": "Test Group",
            "member_ids": [user1_id, user2_id],
        },
    )
    group_id = group_resp.json()["id"]

    # Send multiple messages
    client.post(
        f"/group-chats/{group_id}/messages",
        json={"sender_id": user1_id, "text": "Message 1"},
    )
    client.post(
        f"/group-chats/{group_id}/messages",
        json={"sender_id": user2_id, "text": "Message 2"},
    )
    client.post(
        f"/group-chats/{group_id}/messages",
        json={"sender_id": user1_id, "text": "Message 3"},
    )

    # Retrieve messages
    msgs_resp = client.get(f"/group-chats/{group_id}/messages")

    assert msgs_resp.status_code == 200
    messages = msgs_resp.json()
    assert len(messages) == 3
    assert messages[0]["text"] == "Message 1"
    assert messages[1]["text"] == "Message 2"
    assert messages[2]["text"] == "Message 3"


def test_send_message_to_nonexistent_group():
    """Test sending a message to a nonexistent group returns 404."""
    # Create a user
    user_resp = create_test_user(username="user1")
    user_id = user_resp.json()["user_id"]

    # Try to send message to nonexistent group
    msg_resp = client.post(
        "/group-chats/nonexistent/messages",
        json={
            "sender_id": user_id,
            "text": "Hello",
        },
    )

    assert msg_resp.status_code == 404


def test_get_messages_from_nonexistent_group():
    """Test getting messages from a nonexistent group returns 404."""
    msgs_resp = client.get("/group-chats/nonexistent/messages")
    assert msgs_resp.status_code == 404


def test_group_chat_with_multiple_messages():
    """Test a group chat with multiple sequential messages."""
    # Create users
    user1_resp = create_test_user(username="alice")
    user1_id = user1_resp.json()["user_id"]

    user2_resp = create_test_user(username="bob")
    user2_id = user2_resp.json()["user_id"]

    user3_resp = create_test_user(username="charlie")
    user3_id = user3_resp.json()["user_id"]

    # Create group
    group_resp = client.post(
        "/group-chats",
        json={
            "name": "Team Chat",
            "member_ids": [user1_id, user2_id, user3_id],
        },
    )
    group_id = group_resp.json()["id"]

    # Send messages
    messages_to_send = [
        (user1_id, "Let's start"),
        (user2_id, "I agree"),
        (user3_id, "Let's go"),
        (user1_id, "Great!"),
    ]

    for sender_id, text in messages_to_send:
        resp = client.post(
            f"/group-chats/{group_id}/messages",
            json={"sender_id": sender_id, "text": text},
        )
        assert resp.status_code == 201

    # Retrieve and verify all messages
    msgs_resp = client.get(f"/group-chats/{group_id}/messages")
    messages = msgs_resp.json()

    assert len(messages) == 4
    for i, (sender_id, text) in enumerate(messages_to_send):
        assert messages[i]["sender_id"] == sender_id
        assert messages[i]["text"] == text
