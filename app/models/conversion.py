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


class VoiceToVoiceRequest(BaseModel):
    """Request model for voice-to-voice transformation"""
    input_audio: str  # Base64 encoded audio or file path
    reference_audio: str  # Base64 encoded audio or file path
    transformation_type: str = "voice_conversion"  # voice_conversion, accent_change, gender_swap, etc.
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None
    voice_characteristics: Optional[Dict[str, Any]] = None  # Additional voice parameters
    output_format: str = "wav"  # wav, mp3, flac
    quality: str = "high"  # low, medium, high


class VoiceToVoiceResponse(BaseModel):
    """Response model for voice-to-voice transformation"""
    conversion_id: str
    status: ConversionStatus
    message: str
    transformation_type: str
    input_duration: Optional[float] = None
    output_duration: Optional[float] = None
    output_file: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AudioTransformationOptions(BaseModel):
    """Audio transformation options"""
    pitch_shift: Optional[float] = Field(None, ge=-12.0, le=12.0)  # Semitones
    speed_change: Optional[float] = Field(None, ge=0.5, le=2.0)  # Speed multiplier
    volume_adjustment: Optional[float] = Field(None, ge=0.1, le=3.0)  # Volume multiplier
    noise_reduction: bool = False
    echo_removal: bool = False
    voice_enhancement: bool = False
