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

from app.api import voice_conversion, text_to_speech, batch_processing, health, voice_to_voice
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
    description="""
    ## 🎤 OpenVoice AI - Comprehensive Voice Transformation API
    
    A production-ready API for advanced voice conversion, text-to-speech, and voice-to-voice transformation using OpenVoice AI technology.
    
    ### 🚀 Key Features
    
    - **Voice-to-Voice Transformation**: Convert voice characteristics using reference audio
    - **Text-to-Speech**: Generate speech from text with custom voice characteristics
    - **Batch Processing**: Process multiple audio files simultaneously
    - **Advanced Audio Processing**: Pitch shifting, speed change, volume adjustment, noise reduction
    - **Multiple Audio Formats**: Support for WAV, MP3, FLAC, M4A, OGG
    - **Real-time Processing**: Fast and efficient voice transformation
    - **RESTful API**: Easy integration with frontend applications
    
    ### 📋 Available Endpoints
    
    #### Health & Status
    - `GET /api/v1/health` - Check API health and OpenVoice availability
    
    #### Voice-to-Voice Transformation
    - `POST /api/v1/transform-voice` - Transform voice using form data (file uploads)
    - `POST /api/v1/transform-voice-json` - Transform voice using JSON (base64 audio)
    - `GET /api/v1/transformation-types` - Get available transformation types
    - `GET /api/v1/transformation-status/{id}` - Get transformation status
    - `GET /api/v1/download/{filename}` - Download transformed audio
    
    #### Voice Conversion (Legacy)
    - `POST /api/v1/convert-voice` - Basic voice conversion
    - `GET /api/v1/conversion-status/{id}` - Get conversion status
    
    #### Text-to-Speech
    - `POST /api/v1/convert-text-to-speech` - Convert text to speech with voice characteristics
    
    #### Batch Processing
    - `POST /api/v1/batch-convert-voices` - Process multiple audio files
    
    ### 🎯 Transformation Types
    
    - **voice_conversion**: Convert voice characteristics using reference audio
    - **accent_change**: Change accent while preserving voice characteristics
    - **gender_swap**: Change gender characteristics of the voice
    - **age_change**: Modify voice to sound older or younger
    - **emotion_change**: Modify emotional tone of the voice
    
    ### 🔧 Audio Processing Options
    
    - **Pitch Shift**: -12 to +12 semitones
    - **Speed Change**: 0.5x to 2.0x multiplier
    - **Volume Adjustment**: 0.1x to 3.0x multiplier
    - **Noise Reduction**: Remove background noise
    - **Echo Removal**: Remove echo effects
    - **Voice Enhancement**: Improve voice quality
    
    ### 📊 Supported Formats
    
    - **Input**: WAV, MP3, FLAC, M4A, OGG
    - **Output**: WAV, MP3, FLAC
    - **Quality**: Low, Medium, High
    
    ### 🔒 Rate Limits
    
    - **Requests**: 100 per hour per IP
    - **File Size**: 50MB maximum per file
    - **Processing**: Asynchronous for large files
    
    ### 🌐 CORS Support
    
    Configured for Next.js frontend integration with support for:
    - `http://localhost:3000` (development)
    - `http://localhost:3001` (alternative dev port)
    - Custom production domains
    
    ### 📚 Documentation
    
    - **Interactive Docs**: Available at `/docs` (development mode)
    - **ReDoc**: Available at `/redoc` (development mode)
    - **OpenAPI Schema**: Available at `/openapi.json`
    
    ### 🧪 Testing
    
    Use the provided Postman collection or test with the included HTML demo.
    """,
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
    contact={
        "name": "OpenVoice API Support",
        "url": "https://github.com/your-repo/openvoice-api",
        "email": "support@openvoice-api.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.openvoice.com",
            "description": "Production server"
        }
    ]
)

# Add CORS middleware for Next.js frontend
# For development, allow all origins with localhost/127.0.0.1/0.0.0.0
if settings.ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=False,  # Must be False when allow_origins=["*"]
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
            "Cache-Control",
            "Pragma"
        ],
        expose_headers=[
            "Content-Disposition",
            "Content-Type",
            "Content-Length",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Credentials"
        ],
        max_age=3600
    )
else:
    # Production CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
            "Cache-Control",
            "Pragma"
        ],
        expose_headers=[
            "Content-Disposition",
            "Content-Type",
            "Content-Length",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Credentials"
        ],
        max_age=3600
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
app.include_router(voice_to_voice.router, prefix="/api/v1", tags=["voice-to-voice"])


@app.get("/", 
         summary="API Root",
         description="Get basic API information and available endpoints",
         tags=["root"])
async def root():
    """
    ## 🎤 OpenVoice API Root
    
    Welcome to the OpenVoice AI API! This endpoint provides basic information about the API and available endpoints.
    
    ### Quick Start
    1. Check API health: `GET /api/v1/health`
    2. Get transformation types: `GET /api/v1/transformation-types`
    3. Transform voice: `POST /api/v1/transform-voice`
    
    ### Documentation
    - Interactive docs: `/docs` (development mode)
    - ReDoc: `/redoc` (development mode)
    - OpenAPI schema: `/openapi.json`
    """
    return {
        "message": "🎤 OpenVoice AI API",
        "version": "1.0.0",
        "status": "running",
        "description": "Comprehensive voice transformation API using OpenVoice AI",
        "features": [
            "Voice-to-Voice Transformation",
            "Text-to-Speech with Voice Characteristics", 
            "Batch Processing",
            "Advanced Audio Processing",
            "Multiple Audio Format Support"
        ],
        "endpoints": {
            "health": "/api/v1/health",
            "voice_to_voice": {
                "transform_form": "/api/v1/transform-voice",
                "transform_json": "/api/v1/transform-voice-json",
                "transformation_types": "/api/v1/transformation-types",
                "status": "/api/v1/transformation-status/{id}",
                "download": "/api/v1/download/{filename}"
            },
            "voice_conversion": {
                "convert": "/api/v1/convert-voice",
                "status": "/api/v1/conversion-status/{id}"
            },
            "text_to_speech": "/api/v1/convert-text-to-speech",
            "batch_processing": "/api/v1/batch-convert-voices"
        },
        "supported_formats": {
            "input": ["wav", "mp3", "flac", "m4a", "ogg"],
            "output": ["wav", "mp3", "flac"]
        },
        "transformation_types": [
            "voice_conversion",
            "accent_change", 
            "gender_swap",
            "age_change",
            "emotion_change"
        ],
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled",
        "redoc": "/redoc" if settings.ENVIRONMENT == "development" else "disabled",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
