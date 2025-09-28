"""
OpenVoice API - Basic FastAPI Backend (without OpenVoice CLI)
This version works without OpenVoice CLI for initial testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

# Basic imports without OpenVoice dependencies
from app.core.config_simple import settings
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers

# Import only basic API modules
from app.api import health

# Create a simplified app without OpenVoice dependencies
app = FastAPI(
    title="OpenVoice API (Basic)",
    description="Basic API for testing without OpenVoice CLI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include only health router
app.include_router(health.router, prefix="/api/v1", tags=["health"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OpenVoice API (Basic Version)",
        "version": "1.0.0",
        "status": "running",
        "note": "This is a basic version without OpenVoice CLI. Install OpenVoice CLI for full functionality.",
        "docs": "/docs"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "API is working!",
        "status": "success",
        "timestamp": "2024-01-01T00:00:00Z"
    }

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    print("🚀 Starting OpenVoice API (Basic Version)")
    print("=" * 50)
    print("This version works without OpenVoice CLI")
    print("Install OpenVoice CLI for full voice conversion features")
    print("=" * 50)
    
    uvicorn.run(
        "main-basic:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
