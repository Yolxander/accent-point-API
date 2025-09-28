"""
Simple configuration settings for OpenVoice API
"""

import os
from typing import List, Optional


class Settings:
    """Simple application settings without Pydantic"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:3001",
        "https://yourdomain.com"  # Production domain
    ]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "yourdomain.com"]
    
    # OpenVoice
    OPENVOICE_DEVICE: str = "cpu"  # cpu or cuda
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_AUDIO_TYPES: List[str] = [
        "audio/wav",
        "audio/mp3", 
        "audio/flac",
        "audio/m4a",
        "audio/ogg"
    ]
    
    # Audio Processing
    TARGET_SAMPLE_RATE: int = 22050
    NORMALIZE_AUDIO: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Storage
    TEMP_DIR: str = "/tmp/openvoice_api"
    UPLOAD_DIR: str = "/tmp/openvoice_uploads"
    OUTPUT_DIR: str = "/tmp/openvoice_outputs"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
