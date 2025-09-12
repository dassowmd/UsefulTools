"""FastAPI main application."""

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routers import auth, rules, processing, analysis
from .dependencies import get_current_user, get_gmail_client, get_rules_engine
from .models import UserResponse
from ..core.client import GmailClient
from ..rules.engine import RulesEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Gmail Cleanup API")
    yield
    logger.info("Shutting down Gmail Cleanup API")


# Create FastAPI app
app = FastAPI(
    title="Gmail Cleanup API",
    description="Modern Gmail cleanup and email management API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(rules.router, prefix="/api/rules", tags=["rules"])
app.include_router(processing.router, prefix="/api/processing", tags=["processing"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

# Templates for web interface
templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs."""
    return RedirectResponse(url="/api/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "gmail-cleanup-api",
        "version": "0.1.0"
    }


@app.get("/api/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """Get current user profile information."""
    try:
        gmail_client: GmailClient = get_gmail_client()
        user_info = gmail_client.get_user_info() if gmail_client else {}
        
        return UserResponse(
            email=user_info.get('email', 'Unknown'),
            is_authenticated=True,
            messages_total=user_info.get('messagesTotal', 0),
            threads_total=user_info.get('threadsTotal', 0)
        )
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


# Mount static files (for serving frontend)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    # Static directory doesn't exist - this is fine for API-only deployment
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "gmail_cleanup.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )