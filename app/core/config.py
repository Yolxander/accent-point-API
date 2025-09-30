"""
Configuration settings for OpenVoice API
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
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
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:3001",
        "http://localhost:8000",  # API server itself
        "http://127.0.0.1:8000",
        "http://0.0.0.0:8000",    # API server with 0.0.0.0 binding
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
    
    # Supabase
    SUPABASE_URL: str = "http://127.0.0.1:54321"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
    SUPABASE_SERVICE_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
