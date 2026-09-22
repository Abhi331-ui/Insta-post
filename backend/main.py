import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.api.auth import router as auth_router
from backend.api.posts import router as posts_router
from backend.api.calendar import router as calendar_router
from backend.api.analytics import router as analytics_router
from backend.api.settings import router as settings_router
from backend.api.agent import router as agent_router
from backend.api.queue import router as queue_router
from backend.api.notifications import router as notifications_router
from backend.api.interactions import router as interactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    # Ensure media directories exist
    settings.SLIDES_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="PromptPulse — Autonomous AI Instagram Content Agent",
    description="Autonomous engine discovering, writing, designing, and publishing 6-slide Instagram carousels daily.",
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    settings.FRONTEND_URL,
]
origins = [origin for origin in dict.fromkeys(origin for origin in origins if origin)]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for rendered slide images
media_dir = str(settings.MEDIA_DIR)
app.mount("/media", StaticFiles(directory=media_dir), name="media")

# Include API Routers
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(calendar_router)
app.include_router(analytics_router)
app.include_router(settings_router)
app.include_router(agent_router)
app.include_router(queue_router)
app.include_router(notifications_router)
app.include_router(interactions_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PromptPulse API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to PromptPulse Autonomous AI Instagram Content Agent API",
        "docs": "/docs",
        "health": "/health",
    }
