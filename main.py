"""
OpenVoice API - FastAPI Backend for Voice Conversion
Production-ready API for Next.js frontend integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

from app.api import voice_conversion, text_to_speech, batch_processing, health
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    setup_logging()
    yield
    # Shutdown
    pass


# Create FastAPI application
app = FastAPI(
    title="OpenVoice API",
    description="Production-ready API for voice conversion and text-to-speech using OpenVoice AI",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Setup exception handlers
setup_exception_handlers(app)

# Include API routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(voice_conversion.router, prefix="/api/v1", tags=["voice-conversion"])
app.include_router(text_to_speech.router, prefix="/api/v1", tags=["text-to-speech"])
app.include_router(batch_processing.router, prefix="/api/v1", tags=["batch-processing"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OpenVoice API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
