"""
Instagram-like REST API — entry point.
Run with: uvicorn main:app --reload
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import users, posts

app = FastAPI(
    title="Simple Instagram API",
    description="A simple Instagram-like REST API with users, posts, follow system, likes, comments, reposts and direct messages.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — permissive for demo; tighten in production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Core routers (always available)
# ---------------------------------------------------------------------------
app.include_router(users.router)
app.include_router(posts.router)

# Optional routers — gracefully skipped if files don't exist yet
try:
    from routers import repost, messages
    app.include_router(repost.router)
    app.include_router(messages.router)
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Static files — served from ./static at /static
# Only mount when the directory exists so tests/dev work without it.
# ---------------------------------------------------------------------------
STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["frontend"], include_in_schema=False)
def serve_index() -> FileResponse:
    """Serve the frontend SPA home page."""
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))
    # Graceful fallback when the UX engineer's files haven't landed yet
    from fastapi.responses import JSONResponse
    return JSONResponse(
        {"status": "ok", "service": "Instagram API", "note": "Frontend not yet deployed"},
        status_code=200,
    )


@app.get("/api/health", tags=["health"])
def health_check() -> dict:
    """Health-check endpoint — confirms the API is running."""
    return {"status": "ok", "service": "Instagram API"}
