"""
Configuration settings for OpenVoice API
"""

import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - Use string field to avoid JSON parsing issues
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001,http://localhost:8000,http://127.0.0.1:8000"
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,yourdomain.com"
    
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
    
    # S3 Storage (for Supabase Storage)
    S3_ACCESS_KEY: str = "625729a08b95bf1b7ff351a663f3a23c"
    S3_SECRET_KEY: str = "850181e4652dd023b7a98c58ae0d2d34bd487ee0cc3254aed6eda37307425907"
    S3_BUCKET_NAME: str = "audio-files"
    
    # Properties to convert comma-separated strings to lists
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into a list"""
        if not self.ALLOWED_ORIGINS or not self.ALLOWED_ORIGINS.strip():
            return [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Parse ALLOWED_HOSTS string into a list"""
        if not self.ALLOWED_HOSTS or not self.ALLOWED_HOSTS.strip():
            return ["localhost", "127.0.0.1"]
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
