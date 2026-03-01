# Simple Instagram-Like API

A minimalist Instagram-like social media REST API built with FastAPI, featuring user profiles, posts, social interactions, reposting, and messaging.

## Description

This project provides a complete REST API for a simple Instagram-like social network. Users can create profiles, post photos/videos/status updates, follow other users, like and comment on posts, repost content, send direct messages, and participate in group chats. All data is stored in-memory for simplicity.

## Tech Stack

- **Backend Framework**: Python 3.11+ with FastAPI
- **Testing**: pytest with FastAPI TestClient
- **Storage**: In-memory dictionaries (no database)
- **API Server**: Uvicorn

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RajuRoopani/build-a-simple-instagram-app.git
cd instagram_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Start the API server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

## Running Tests

```bash
pytest tests/ -v
```

Run tests for a specific feature:
```bash
pytest tests/test_users_posts.py -v        # Core features (Users, Posts, Follow, Likes, Comments)
pytest tests/test_repost_messages.py -v    # Repost and Messaging features
```

## API Endpoints Reference

### User Profile Management

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/users` | Create a new user profile | 201 Created |
| GET | `/users/{user_id}` | Retrieve user profile by ID | 200 OK, 404 Not Found |
| PUT | `/users/{user_id}` | Update user profile | 200 OK, 404 Not Found |
| GET | `/users/{user_id}/posts` | Get all posts by a user | 200 OK, 404 Not Found |

### Follow System

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/users/{user_id}/follow` | Follow a user | 200 OK, 404 Not Found |
| DELETE | `/users/{user_id}/follow` | Unfollow a user | 200 OK, 404 Not Found |
| GET | `/users/{user_id}/followers` | Get list of followers | 200 OK, 404 Not Found |
| GET | `/users/{user_id}/following` | Get list of users being followed | 200 OK, 404 Not Found |

### Posts

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/posts` | Create a new post (photo, video, status) | 201 Created, 404 Not Found |
| GET | `/posts/{post_id}` | Retrieve post by ID | 200 OK, 404 Not Found |

### Feed

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| GET | `/feed` | Get feed (optional query param `user_id`) | 200 OK |

### Likes

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/posts/{post_id}/likes` | Like a post | 200 OK, 404 Not Found |
| DELETE | `/posts/{post_id}/likes` | Unlike a post | 200 OK, 404 Not Found |

### Comments

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/posts/{post_id}/comments` | Add a comment to a post | 201 Created, 404 Not Found |
| GET | `/posts/{post_id}/comments` | Get all comments on a post | 200 OK, 404 Not Found |

### Reposting

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/posts/{post_id}/repost` | Create a repost of an existing post | 201 Created, 404 Not Found |

### Direct Messages

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/messages` | Send a direct message | 201 Created |
| GET | `/messages` | Get conversation (query params: `user1`, `user2`) | 200 OK |

### Group Chats

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | `/group-chats` | Create a new group chat | 201 Created |
| POST | `/group-chats/{chat_id}/messages` | Send a message to a group chat | 201 Created, 404 Not Found |
| GET | `/group-chats/{chat_id}/messages` | Get all messages in a group chat | 200 OK, 404 Not Found |

## Example Requests

### Create a User
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "display_name": "John Doe",
    "bio": "Photography enthusiast",
    "profile_picture_url": "https://example.com/pic.jpg"
  }'
```

### Create a Post
```bash
curl -X POST http://localhost:8000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid-here",
    "content_type": "photo",
    "content_url": "https://example.com/photo.jpg",
    "caption": "My amazing photo!"
  }'
```

### Follow a User
```bash
curl -X POST http://localhost:8000/users/{target_user_id}/follow \
  -H "Content-Type: application/json" \
  -d '{
    "follower_id": "your-user-uuid"
  }'
```

### Like a Post
```bash
curl -X POST http://localhost:8000/posts/{post_id}/likes \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid-here"
  }'
```

### Send a Direct Message
```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "user-uuid-1",
    "recipient_id": "user-uuid-2",
    "text": "Hey! How are you?"
  }'
```

### Create a Group Chat
```bash
curl -X POST http://localhost:8000/group-chats \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Team Lunch Plans",
    "member_ids": ["user-uuid-1", "user-uuid-2", "user-uuid-3"]
  }'
```

### Send a Group Message
```bash
curl -X POST http://localhost:8000/group-chats/{chat_id}/messages \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "user-uuid-here",
    "text": "Let'\''s meet at noon!"
  }'
```

## Project Structure

```
instagram_app/
├── main.py                 # FastAPI app initialization and router integration
├── models.py               # Pydantic models and in-memory storage
├── requirements.txt        # Python dependencies
├── routers/
│   ├── __init__.py
│   ├── users.py            # User CRUD and follow system
│   ├── posts.py            # Post CRUD, likes, comments, feed
│   ├── repost.py           # Reposting endpoints
│   └── messages.py         # DM and group chat endpoints
└── tests/
    ├── __init__.py
    ├── test_users_posts.py        # Tests for core features
    └── test_repost_messages.py    # Tests for repost and messaging
```

## Features

### User Profiles
- Create and manage user profiles
- Display user information (username, display name, bio, profile picture)
- Track follower/following counts

### Posts
- Support multiple content types (photo, video, status)
- Add captions to posts
- Track post metadata (creation time, like count, repost count)

### Social Interactions
- **Follow System**: Users can follow/unfollow other users
- **Likes**: Like and unlike posts with like count tracking
- **Comments**: Add and view comments on posts
- **Feed**: View posts from followed users

### Reposting
- Repost existing posts to share with your followers
- Viral tracking through repost_count increments
- Reposts inherit content from original posts

### Messaging
- **Direct Messages**: Send private messages between users
- **Group Chats**: Create and manage group conversations
- **Conversation History**: Retrieve message history between users

## Data Model

All data is stored in simple in-memory dictionaries:

- **users_db**: Maps user IDs to user objects
- **posts_db**: Maps post IDs to post objects
- **followers_db**: Maps user IDs to sets of follower IDs
- **following_db**: Maps user IDs to sets of followed user IDs
- **likes_db**: Maps post IDs to sets of user IDs who liked them
- **comments_db**: Maps post IDs to lists of comment objects
- **messages_db**: List of direct message objects
- **group_chats_db**: Maps group chat IDs to group chat objects

## Notes

- This is a demonstration API with in-memory storage. Data is lost when the server restarts.
- For production use, integrate with a real database (PostgreSQL, MongoDB, etc.)
- Consider adding authentication, authorization, and rate limiting for a production API
- Implement proper input validation and error handling

## License

MIT License
