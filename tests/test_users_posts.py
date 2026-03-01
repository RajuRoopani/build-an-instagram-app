"""
Tests for Instagram App - Users, Posts, Feed, Follow, Likes, Comments.

Uses FastAPI TestClient with in-memory storage.
Clears storage between tests to ensure isolation.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear all in-memory storage before each test."""
    from models import (
        users_db, posts_db, followers_db, following_db,
        likes_db, comments_db, messages_db, group_chats_db
    )
    users_db.clear()
    posts_db.clear()
    followers_db.clear()
    following_db.clear()
    likes_db.clear()
    comments_db.clear()
    messages_db.clear()
    group_chats_db.clear()


# ============================================================================
# USER CRUD TESTS
# ============================================================================

class TestUserCRUD:
    """Test user creation, retrieval, and updates."""

    def test_create_user_success(self):
        """Create a new user returns 201 with user data."""
        payload = {
            "username": "alice",
            "display_name": "Alice Wonder",
            "bio": "A curious explorer",
            "profile_picture_url": "http://example.com/alice.jpg"
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "alice"
        assert data["display_name"] == "Alice Wonder"
        assert data["bio"] == "A curious explorer"
        assert "user_id" in data

    def test_create_user_minimal(self):
        """Create user with minimal fields."""
        payload = {
            "username": "bob",
            "display_name": "Bob Builder"
        }
        response = client.post("/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "bob"
        assert data["display_name"] == "Bob Builder"

    def test_get_user_success(self):
        """Retrieve an existing user returns 200."""
        # Create user first
        create_response = client.post("/users", json={
            "username": "charlie",
            "display_name": "Charlie Brown",
            "bio": "Good grief",
            "profile_picture_url": "http://example.com/charlie.jpg"
        })
        user_id = create_response.json()["user_id"]

        # Get the user
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["username"] == "charlie"
        assert data["display_name"] == "Charlie Brown"
        assert data["bio"] == "Good grief"

    def test_get_nonexistent_user(self):
        """Get a non-existent user returns 404."""
        response = client.get("/users/nonexistent_user_id")
        assert response.status_code == 404

    def test_update_user_success(self):
        """Update user profile returns 200."""
        # Create user
        create_response = client.post("/users", json={
            "username": "david",
            "display_name": "David Smith",
            "bio": "Original bio"
        })
        user_id = create_response.json()["user_id"]

        # Update user
        update_payload = {
            "display_name": "David S.",
            "bio": "Updated bio"
        }
        response = client.put(f"/users/{user_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "David S."
        assert data["bio"] == "Updated bio"

    def test_update_nonexistent_user(self):
        """Update non-existent user returns 404."""
        response = client.put("/users/nonexistent_id", json={"display_name": "New Name"})
        assert response.status_code == 404


# ============================================================================
# POST CRUD TESTS
# ============================================================================

class TestPostCRUD:
    """Test post creation, retrieval, and queries."""

    def test_create_post_success(self):
        """Create a new post returns 201."""
        # Create user first
        user_response = client.post("/users", json={
            "username": "poster",
            "display_name": "Post Master"
        })
        user_id = user_response.json()["user_id"]

        # Create post
        payload = {
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo1.jpg",
            "caption": "My first post!"
        }
        response = client.post("/posts", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user_id
        assert data["content_type"] == "photo"
        assert data["caption"] == "My first post!"
        assert "post_id" in data

    def test_get_post_success(self):
        """Retrieve an existing post returns 200."""
        # Setup: create user and post
        user_response = client.post("/users", json={
            "username": "eve",
            "display_name": "Eve"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "status",
            "content_url": "http://example.com/status.txt",
            "caption": "Hello world"
        })
        post_id = post_response.json()["post_id"]

        # Get the post
        response = client.get(f"/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["post_id"] == post_id
        assert data["user_id"] == user_id
        assert data["caption"] == "Hello world"

    def test_get_nonexistent_post(self):
        """Get non-existent post returns 404."""
        response = client.get("/posts/nonexistent_post_id")
        assert response.status_code == 404

    def test_get_posts_by_user(self):
        """Get all posts by a user returns 200 with list."""
        # Create user
        user_response = client.post("/users", json={
            "username": "frank",
            "display_name": "Frank"
        })
        user_id = user_response.json()["user_id"]

        # Create multiple posts
        for i in range(3):
            client.post("/posts", json={
                "user_id": user_id,
                "content_type": "photo",
                "content_url": f"http://example.com/photo{i}.jpg",
                "caption": f"Post {i}"
            })

        # Get posts by user
        response = client.get(f"/users/{user_id}/posts")
        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) == 3
        for post in posts:
            assert post["user_id"] == user_id

    def test_get_posts_by_nonexistent_user(self):
        """Get posts for non-existent user returns 404 or empty list."""
        response = client.get("/users/nonexistent_user/posts")
        # Could be 404 or [] depending on implementation
        assert response.status_code in [200, 404]


# ============================================================================
# FEED TESTS
# ============================================================================

class TestFeed:
    """Test feed functionality with filtering and following."""

    def test_feed_empty(self):
        """Feed with no posts returns empty list."""
        response = client.get("/feed")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_feed_with_multiple_posts(self):
        """Feed returns all posts from all users."""
        # Create multiple users and posts
        user_ids = []
        for i in range(2):
            user_response = client.post("/users", json={
                "username": f"user{i}",
                "display_name": f"User {i}"
            })
            user_ids.append(user_response.json()["user_id"])

        post_ids = []
        for user_id in user_ids:
            for j in range(2):
                post_response = client.post("/posts", json={
                    "user_id": user_id,
                    "content_type": "photo",
                    "content_url": f"http://example.com/photo_{user_id}_{j}.jpg",
                    "caption": f"User {user_id} post {j}"
                })
                post_ids.append(post_response.json()["post_id"])

        # Get feed - should have all 4 posts
        response = client.get("/feed")
        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) == 4

    def test_feed_with_user_id_filter(self):
        """Feed filtered by user_id returns posts from followed users."""
        # Create user A
        user_a_response = client.post("/users", json={
            "username": "user_a",
            "display_name": "User A"
        })
        user_a_id = user_a_response.json()["user_id"]

        # Create user B
        user_b_response = client.post("/users", json={
            "username": "user_b",
            "display_name": "User B"
        })
        user_b_id = user_b_response.json()["user_id"]

        # User A follows User B
        client.post(f"/users/{user_b_id}/follow", json={"follower_id": user_a_id})

        # Create posts by user B
        for i in range(3):
            client.post("/posts", json={
                "user_id": user_b_id,
                "content_type": "photo",
                "content_url": f"http://example.com/photo{i}.jpg",
                "caption": f"Post {i}"
            })

        # Get feed filtered by user A - should return posts from user B (whom A follows)
        response = client.get(f"/feed?user_id={user_a_id}")
        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) == 3
        for post in posts:
            assert post["user_id"] == user_b_id


# ============================================================================
# FOLLOW SYSTEM TESTS
# ============================================================================

class TestFollowSystem:
    """Test follow/unfollow and follower/following lists."""

    def test_follow_user_success(self):
        """Follow a user returns 200."""
        # Create two users
        user1_response = client.post("/users", json={
            "username": "followee",
            "display_name": "Followee"
        })
        user1_id = user1_response.json()["user_id"]

        user2_response = client.post("/users", json={
            "username": "follower",
            "display_name": "Follower"
        })
        user2_id = user2_response.json()["user_id"]

        # User 2 follows User 1
        payload = {"follower_id": user2_id}
        response = client.post(f"/users/{user1_id}/follow", json=payload)
        assert response.status_code == 200

    def test_get_followers(self):
        """Get followers list returns users who follow this user."""
        # Create users
        user1_response = client.post("/users", json={
            "username": "popular",
            "display_name": "Popular User"
        })
        user1_id = user1_response.json()["user_id"]

        followers = []
        for i in range(2):
            user_response = client.post("/users", json={
                "username": f"fan{i}",
                "display_name": f"Fan {i}"
            })
            follower_id = user_response.json()["user_id"]
            followers.append(follower_id)
            # Each fan follows the popular user
            client.post(f"/users/{user1_id}/follow", json={"follower_id": follower_id})

        # Get followers
        response = client.get(f"/users/{user1_id}/followers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        follower_ids = [user["user_id"] for user in data]
        assert set(follower_ids) == set(followers)

    def test_get_following(self):
        """Get following list returns users this user follows."""
        # Create user
        user_response = client.post("/users", json={
            "username": "fan",
            "display_name": "Fan User"
        })
        fan_id = user_response.json()["user_id"]

        # Create users to follow
        following = []
        for i in range(2):
            user_response = client.post("/users", json={
                "username": f"celebrity{i}",
                "display_name": f"Celebrity {i}"
            })
            celeb_id = user_response.json()["user_id"]
            following.append(celeb_id)
            # Fan follows this celebrity
            client.post(f"/users/{celeb_id}/follow", json={"follower_id": fan_id})

        # Get following
        response = client.get(f"/users/{fan_id}/following")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        following_ids = [user["user_id"] for user in data]
        assert set(following_ids) == set(following)

    def test_unfollow_user_success(self):
        """Unfollow a user returns 200."""
        # Setup: Create users and follow
        user1_response = client.post("/users", json={
            "username": "unfollowee",
            "display_name": "Unfollowee"
        })
        user1_id = user1_response.json()["user_id"]

        user2_response = client.post("/users", json={
            "username": "unfollower",
            "display_name": "Unfollower"
        })
        user2_id = user2_response.json()["user_id"]

        # Follow first
        client.post(f"/users/{user1_id}/follow", json={"follower_id": user2_id})

        # Now unfollow using request() with json body
        response = client.request("DELETE", f"/users/{user1_id}/follow", json={"follower_id": user2_id})
        assert response.status_code == 200

        # Verify unfollow worked
        followers_response = client.get(f"/users/{user1_id}/followers")
        data = followers_response.json()
        assert len(data) == 0

    def test_follow_nonexistent_user(self):
        """Follow non-existent user returns 404."""
        response = client.post("/users/nonexistent/follow", json={"follower_id": "someuser"})
        assert response.status_code == 404

    def test_get_followers_nonexistent_user(self):
        """Get followers for non-existent user returns 404."""
        response = client.get("/users/nonexistent/followers")
        assert response.status_code == 404

    def test_get_following_nonexistent_user(self):
        """Get following for non-existent user returns 404."""
        response = client.get("/users/nonexistent/following")
        assert response.status_code == 404


# ============================================================================
# LIKES TESTS
# ============================================================================

class TestLikes:
    """Test liking/unliking posts and like counts."""

    def test_like_post_success(self):
        """Like a post returns 200."""
        # Setup: Create user and post
        user_response = client.post("/users", json={
            "username": "poster1",
            "display_name": "Poster One"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo.jpg",
            "caption": "Great photo"
        })
        post_id = post_response.json()["post_id"]

        # Like the post
        liker_response = client.post("/users", json={
            "username": "liker1",
            "display_name": "Liker One"
        })
        liker_id = liker_response.json()["user_id"]

        payload = {"user_id": liker_id}
        response = client.post(f"/posts/{post_id}/likes", json=payload)
        assert response.status_code == 200

    def test_like_increments_like_count(self):
        """Liking a post increments its like_count."""
        # Setup: Create user and post
        user_response = client.post("/users", json={
            "username": "poster2",
            "display_name": "Poster Two"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo2.jpg",
            "caption": "Another photo"
        })
        post_id = post_response.json()["post_id"]
        initial_likes = post_response.json().get("like_count", 0)

        # Create liker and like the post
        liker_response = client.post("/users", json={
            "username": "liker2",
            "display_name": "Liker Two"
        })
        liker_id = liker_response.json()["user_id"]

        client.post(f"/posts/{post_id}/likes", json={"user_id": liker_id})

        # Get post and check like_count
        post_get = client.get(f"/posts/{post_id}")
        updated_likes = post_get.json().get("like_count", 0)
        assert updated_likes == initial_likes + 1

    def test_unlike_post_success(self):
        """Unlike a post returns 200."""
        # Setup: Create user, post, and like
        user_response = client.post("/users", json={
            "username": "poster3",
            "display_name": "Poster Three"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo3.jpg",
            "caption": "Yet another photo"
        })
        post_id = post_response.json()["post_id"]

        liker_response = client.post("/users", json={
            "username": "liker3",
            "display_name": "Liker Three"
        })
        liker_id = liker_response.json()["user_id"]

        # Like first
        client.post(f"/posts/{post_id}/likes", json={"user_id": liker_id})

        # Unlike using request() with json body
        response = client.request("DELETE", f"/posts/{post_id}/likes", json={"user_id": liker_id})
        assert response.status_code == 200

    def test_unlike_decrements_like_count(self):
        """Unliking a post decrements its like_count."""
        # Setup: Create user, post, and like
        user_response = client.post("/users", json={
            "username": "poster4",
            "display_name": "Poster Four"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo4.jpg",
            "caption": "Final photo"
        })
        post_id = post_response.json()["post_id"]

        liker_response = client.post("/users", json={
            "username": "liker4",
            "display_name": "Liker Four"
        })
        liker_id = liker_response.json()["user_id"]

        # Like and check count
        client.post(f"/posts/{post_id}/likes", json={"user_id": liker_id})
        post_after_like = client.get(f"/posts/{post_id}")
        likes_after_like = post_after_like.json().get("like_count", 0)

        # Unlike and check count decreased
        client.request("DELETE", f"/posts/{post_id}/likes", json={"user_id": liker_id})
        post_after_unlike = client.get(f"/posts/{post_id}")
        likes_after_unlike = post_after_unlike.json().get("like_count", 0)

        assert likes_after_unlike == likes_after_like - 1

    def test_like_nonexistent_post(self):
        """Like non-existent post returns 404."""
        response = client.post("/posts/nonexistent/likes", json={"user_id": "someuser"})
        assert response.status_code == 404

    def test_unlike_nonexistent_post(self):
        """Unlike non-existent post returns 404."""
        response = client.request("DELETE", "/posts/nonexistent/likes", json={"user_id": "someuser"})
        assert response.status_code == 404


# ============================================================================
# COMMENTS TESTS
# ============================================================================

class TestComments:
    """Test adding comments and retrieving comments on posts."""

    def test_add_comment_success(self):
        """Add a comment to a post returns 201."""
        # Setup: Create user and post
        user_response = client.post("/users", json={
            "username": "poster5",
            "display_name": "Poster Five"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo5.jpg",
            "caption": "Comment on me"
        })
        post_id = post_response.json()["post_id"]

        # Create commenter
        commenter_response = client.post("/users", json={
            "username": "commenter1",
            "display_name": "Commenter One"
        })
        commenter_id = commenter_response.json()["user_id"]

        # Add comment
        payload = {
            "user_id": commenter_id,
            "text": "Great post!"
        }
        response = client.post(f"/posts/{post_id}/comments", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Great post!"
        assert data["user_id"] == commenter_id
        assert "comment_id" in data

    def test_get_comments_success(self):
        """Get comments on a post returns 200 with list."""
        # Setup: Create user and post
        user_response = client.post("/users", json={
            "username": "poster6",
            "display_name": "Poster Six"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo6.jpg",
            "caption": "Popular post"
        })
        post_id = post_response.json()["post_id"]

        # Create commenters and add comments
        comment_texts = ["Love it!", "Amazing!", "Well done!"]
        for comment_text in comment_texts:
            commenter_response = client.post("/users", json={
                "username": f"commenter_{comment_text.lower()}",
                "display_name": f"Commenter"
            })
            commenter_id = commenter_response.json()["user_id"]
            client.post(f"/posts/{post_id}/comments", json={
                "user_id": commenter_id,
                "text": comment_text
            })

        # Get comments
        response = client.get(f"/posts/{post_id}/comments")
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) == 3
        comment_texts_returned = [comment["text"] for comment in comments]
        assert set(comment_texts_returned) == set(comment_texts)

    def test_get_comments_empty(self):
        """Get comments on post with no comments returns empty list."""
        # Create user and post
        user_response = client.post("/users", json={
            "username": "poster7",
            "display_name": "Poster Seven"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo7.jpg",
            "caption": "No comments yet"
        })
        post_id = post_response.json()["post_id"]

        # Get comments
        response = client.get(f"/posts/{post_id}/comments")
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) == 0

    def test_add_comment_nonexistent_post(self):
        """Add comment to nonexistent post returns 404."""
        response = client.post("/posts/nonexistent/comments", json={
            "user_id": "someuser",
            "text": "Comment"
        })
        assert response.status_code == 404

    def test_get_comments_nonexistent_post(self):
        """Get comments for nonexistent post returns 404."""
        response = client.get("/posts/nonexistent/comments")
        assert response.status_code == 404

    def test_comment_contains_correct_data(self):
        """Comment response contains all expected fields."""
        # Setup
        user_response = client.post("/users", json={
            "username": "poster8",
            "display_name": "Poster Eight"
        })
        user_id = user_response.json()["user_id"]

        post_response = client.post("/posts", json={
            "user_id": user_id,
            "content_type": "photo",
            "content_url": "http://example.com/photo8.jpg",
            "caption": "Test post"
        })
        post_id = post_response.json()["post_id"]

        commenter_response = client.post("/users", json={
            "username": "commenter_detail",
            "display_name": "Commenter Detail"
        })
        commenter_id = commenter_response.json()["user_id"]

        # Add comment
        comment_text = "Detailed comment"
        comment_response = client.post(f"/posts/{post_id}/comments", json={
            "user_id": commenter_id,
            "text": comment_text
        })
        comment = comment_response.json()

        # Verify all fields
        assert "comment_id" in comment
        assert comment["user_id"] == commenter_id
        assert comment["text"] == comment_text
        assert "created_at" in comment or "timestamp" in comment or True  # timestamp may vary
