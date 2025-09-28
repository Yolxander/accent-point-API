"""
Data models for voice conversion
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ConversionStatus(str, Enum):
    """Conversion status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConversionRequest(BaseModel):
    """Request model for voice conversion"""
    input_file: str
    reference_file: str
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None


class ConversionResponse(BaseModel):
    """Response model for voice conversion"""
    conversion_id: str
    status: ConversionStatus
    message: str
    output_file: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class BatchConversionRequest(BaseModel):
    """Request model for batch conversion"""
    input_files: List[str]
    reference_file: str
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None
    max_concurrent: int = 3


class BatchConversionResponse(BaseModel):
    """Response model for batch conversion"""
    batch_id: str
    status: ConversionStatus
    message: str
    total_files: int
    processed_files: int
    failed_files: int
    results: List[Dict[str, Any]]
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class TTSRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str = Field(..., min_length=1, max_length=5000)
    reference_file: str
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None
    voice_speed: float = Field(1.0, ge=0.5, le=2.0)
    voice_pitch: float = Field(1.0, ge=0.5, le=2.0)


class TTSResponse(BaseModel):
    """Response model for text-to-speech"""
    conversion_id: str
    status: ConversionStatus
    message: str
    output_file: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AudioFileInfo(BaseModel):
    """Audio file information model"""
    filename: str
    content_type: str
    size: int
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_depth: Optional[int] = None


class ConversionProgress(BaseModel):
    """Conversion progress model"""
    conversion_id: str
    status: ConversionStatus
    progress_percentage: float = Field(0.0, ge=0.0, le=100.0)
    current_step: str
    total_steps: int
    current_step_number: int
    estimated_time_remaining: Optional[int] = None  # seconds
    message: str
