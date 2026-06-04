"""
FastAPI application entry point for RootCause.
Configures CORS, startup/shutdown hooks, and mounts API routes.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import init_db
from app.api.routes import router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and data directories on startup."""
    await init_db()
    yield


app = FastAPI(
    title="RootCause",
    description="AI Pipeline Observability Tool — Trace, diagnose, and learn from AI pipeline failures.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Alternative dev server
        "http://localhost:8080",   # Docker frontend
        "http://frontend:8080",   # Docker-compose network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/monitoring."""
    return {"status": "healthy", "service": "root-cause-api"}
