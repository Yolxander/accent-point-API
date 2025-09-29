"""
Voice-to-Voice Transformation API endpoints
Comprehensive voice transformation using OpenVoice AI
"""

import os
import tempfile
import uuid
import base64
import time
from typing import Optional, Dict, Any
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ValidationError
import asyncio

from app.core.config import settings
from app.core.exceptions import AudioProcessingError, FileValidationError, ConversionError
from app.services.audio_processor import AudioProcessor
from app.services.voice_converter import VoiceConverter
from app.models.conversion import (
    VoiceToVoiceRequest, 
    VoiceToVoiceResponse, 
    ConversionStatus,
    AudioTransformationOptions
)

router = APIRouter()

# Initialize services
audio_processor = AudioProcessor()
voice_converter = VoiceConverter()


class VoiceToVoiceFormRequest(BaseModel):
    """Form-based request model for voice-to-voice transformation"""
    transformation_type: str = "voice_conversion"
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None
    output_format: str = "wav"
    quality: str = "high"
    pitch_shift: Optional[float] = None
    speed_change: Optional[float] = None
    volume_adjustment: Optional[float] = None
    noise_reduction: bool = False
    echo_removal: bool = False
    voice_enhancement: bool = False


@router.post("/transform-voice", 
             response_model=VoiceToVoiceResponse,
             summary="Transform Voice (Form Data)",
             description="Transform voice using uploaded audio files with comprehensive processing options")
async def transform_voice(
    input_audio: UploadFile = File(..., description="Input audio file to transform (WAV, MP3, FLAC, M4A, OGG)"),
    reference_audio: UploadFile = File(..., description="Reference audio file for voice characteristics (WAV, MP3, FLAC, M4A, OGG)"),
    transformation_type: str = Form("voice_conversion", description="Type of transformation: voice_conversion, accent_change, gender_swap, age_change, emotion_change"),
    device: str = Form("cpu", description="Processing device: 'cpu' or 'cuda'"),
    normalize: bool = Form(True, description="Normalize audio before processing"),
    target_sample_rate: Optional[int] = Form(None, description="Target sample rate (default: 22050)"),
    output_format: str = Form("wav", description="Output audio format: 'wav', 'mp3', 'flac'"),
    quality: str = Form("high", description="Output quality: 'low', 'medium', 'high'"),
    pitch_shift: Optional[float] = Form(None, description="Pitch shift in semitones (-12 to 12)"),
    speed_change: Optional[float] = Form(None, description="Speed change multiplier (0.5 to 2.0)"),
    volume_adjustment: Optional[float] = Form(None, description="Volume adjustment multiplier (0.1 to 3.0)"),
    noise_reduction: bool = Form(False, description="Apply noise reduction"),
    echo_removal: bool = Form(False, description="Remove echo"),
    voice_enhancement: bool = Form(False, description="Enhance voice quality")
):
    """
    Transform voice using OpenVoice AI with comprehensive options
    
    - **input_audio**: Audio file containing the voice to transform
    - **reference_audio**: Audio file containing the target voice characteristics
    - **transformation_type**: Type of transformation (voice_conversion, accent_change, gender_swap)
    - **device**: Processing device ('cpu' or 'cuda')
    - **normalize**: Whether to normalize audio before processing
    - **target_sample_rate**: Target sample rate for processing
    - **output_format**: Output audio format (wav, mp3, flac)
    - **quality**: Output quality (low, medium, high)
    - **pitch_shift**: Pitch shift in semitones (-12 to 12)
    - **speed_change**: Speed change multiplier (0.5 to 2.0)
    - **volume_adjustment**: Volume adjustment multiplier (0.1 to 3.0)
    - **noise_reduction**: Apply noise reduction
    - **echo_removal**: Remove echo
    - **voice_enhancement**: Enhance voice quality
    """
    
    start_time = time.time()
    conversion_id = str(uuid.uuid4())
    
    try:
        # Validate file types
        if not input_audio.content_type.startswith('audio/'):
            raise FileValidationError("Input file must be an audio file")
        
        if not reference_audio.content_type.startswith('audio/'):
            raise FileValidationError("Reference file must be an audio file")
        
        # Validate file sizes
        if input_audio.size > settings.MAX_FILE_SIZE:
            raise FileValidationError(f"Input file too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")
        
        if reference_audio.size > settings.MAX_FILE_SIZE:
            raise FileValidationError(f"Reference file too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")
        
        # Validate transformation parameters
        if pitch_shift is not None and not (-12.0 <= pitch_shift <= 12.0):
            raise FileValidationError("Pitch shift must be between -12.0 and 12.0 semitones")
        
        if speed_change is not None and not (0.5 <= speed_change <= 2.0):
            raise FileValidationError("Speed change must be between 0.5 and 2.0")
        
        if volume_adjustment is not None and not (0.1 <= volume_adjustment <= 3.0):
            raise FileValidationError("Volume adjustment must be between 0.1 and 3.0")
        
        # Read uploaded files
        input_content = await input_audio.read()
        reference_content = await reference_audio.read()
        
        # Process input audio
        input_data, input_sr = await audio_processor.load_audio_from_bytes(input_content)
        input_duration = len(input_data) / input_sr if input_sr > 0 else 0
        
        # Process reference audio
        reference_data, reference_sr = await audio_processor.load_audio_from_bytes(reference_content)
        
        # Normalize and resample if requested
        if normalize:
            input_data = audio_processor.normalize_audio(input_data)
            reference_data = audio_processor.normalize_audio(reference_data)
        
        target_sr = target_sample_rate or settings.TARGET_SAMPLE_RATE
        
        if input_sr != target_sr:
            input_data = audio_processor.resample_audio(input_data, input_sr, target_sr)
        if reference_sr != target_sr:
            reference_data = audio_processor.resample_audio(reference_data, reference_sr, target_sr)
        
        # Apply audio transformations
        if pitch_shift is not None:
            input_data = await audio_processor.pitch_shift(input_data, target_sr, pitch_shift)
        
        if speed_change is not None:
            input_data = await audio_processor.speed_change(input_data, target_sr, speed_change)
        
        if volume_adjustment is not None:
            input_data = await audio_processor.volume_adjust(input_data, volume_adjustment)
        
        if noise_reduction:
            input_data = await audio_processor.noise_reduction(input_data, target_sr)
        
        if echo_removal:
            input_data = await audio_processor.echo_removal(input_data, target_sr)
        
        if voice_enhancement:
            input_data = await audio_processor.voice_enhancement(input_data, target_sr)
        
        # Create temporary files for OpenVoice processing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_input:
            audio_processor.save_audio(temp_input.name, input_data, target_sr)
            temp_input_path = temp_input.name
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_ref:
            audio_processor.save_audio(temp_ref.name, reference_data, target_sr)
            temp_ref_path = temp_ref.name
        
        # Create output file path
        output_filename = f"transformed_{conversion_id}.{output_format}"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        # Perform voice transformation
        await voice_converter.convert_voice(
            input_file=temp_input_path,
            reference_file=temp_ref_path,
            output_file=output_path,
            device=device
        )
        
        # Clean up temporary files
        os.unlink(temp_input_path)
        os.unlink(temp_ref_path)
        
        # Verify output file exists
        if not os.path.exists(output_path):
            raise ConversionError("Voice transformation failed - no output file generated")
        
        # Get output file info
        file_size = os.path.getsize(output_path)
        output_duration = len(input_data) / target_sr  # Approximate duration
        
        processing_time = time.time() - start_time
        
        return VoiceToVoiceResponse(
            conversion_id=conversion_id,
            status=ConversionStatus.COMPLETED,
            message="Voice transformation completed successfully",
            transformation_type=transformation_type,
            input_duration=input_duration,
            output_duration=output_duration,
            output_file=output_filename,
            file_size=file_size,
            download_url=f"/api/v1/download/{output_filename}",
            processing_time=processing_time,
            completed_at=time.time()
        )
        
    except Exception as e:
        # Clean up any temporary files
        try:
            if 'temp_input_path' in locals():
                os.unlink(temp_input_path)
            if 'temp_ref_path' in locals():
                os.unlink(temp_ref_path)
        except:
            pass
        
        processing_time = time.time() - start_time
        
        return VoiceToVoiceResponse(
            conversion_id=conversion_id,
            status=ConversionStatus.FAILED,
            message="Voice transformation failed",
            transformation_type=transformation_type,
            error_message=str(e),
            processing_time=processing_time
        )


@router.post("/transform-voice-json", 
             response_model=VoiceToVoiceResponse,
             summary="Transform Voice (JSON)",
             description="Transform voice using JSON request body with base64 encoded audio data")
async def transform_voice_json(request: VoiceToVoiceRequest):
    """
    Transform voice using JSON request body (supports base64 encoded audio)
    
    This endpoint accepts base64 encoded audio data in the request body,
    making it suitable for frontend applications that prefer JSON over form data.
    """
    
    start_time = time.time()
    conversion_id = str(uuid.uuid4())
    
    try:
        # Decode base64 audio data
        try:
            input_audio_data = base64.b64decode(request.input_audio)
            reference_audio_data = base64.b64decode(request.reference_audio)
        except Exception as e:
            raise FileValidationError(f"Invalid base64 audio data: {str(e)}")
        
        # Validate file sizes
        if len(input_audio_data) > settings.MAX_FILE_SIZE:
            raise FileValidationError(f"Input audio too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")
        
        if len(reference_audio_data) > settings.MAX_FILE_SIZE:
            raise FileValidationError(f"Reference audio too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")
        
        # Process input audio
        input_data, input_sr = await audio_processor.load_audio_from_bytes(input_audio_data)
        input_duration = len(input_data) / input_sr if input_sr > 0 else 0
        
        # Process reference audio
        reference_data, reference_sr = await audio_processor.load_audio_from_bytes(reference_audio_data)
        
        # Normalize and resample if requested
        if request.normalize:
            input_data = audio_processor.normalize_audio(input_data)
            reference_data = audio_processor.normalize_audio(reference_data)
        
        target_sr = request.target_sample_rate or settings.TARGET_SAMPLE_RATE
        
        if input_sr != target_sr:
            input_data = audio_processor.resample_audio(input_data, input_sr, target_sr)
        if reference_sr != target_sr:
            reference_data = audio_processor.resample_audio(reference_data, reference_sr, target_sr)
        
        # Apply voice characteristics if provided
        if request.voice_characteristics:
            characteristics = request.voice_characteristics
            
            if 'pitch_shift' in characteristics:
                input_data = await audio_processor.pitch_shift(
                    input_data, target_sr, characteristics['pitch_shift']
                )
            
            if 'speed_change' in characteristics:
                input_data = await audio_processor.speed_change(
                    input_data, target_sr, characteristics['speed_change']
                )
            
            if 'volume_adjustment' in characteristics:
                input_data = await audio_processor.volume_adjust(
                    input_data, characteristics['volume_adjustment']
                )
        
        # Create temporary files for OpenVoice processing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_input:
            audio_processor.save_audio(temp_input.name, input_data, target_sr)
            temp_input_path = temp_input.name
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_ref:
            audio_processor.save_audio(temp_ref.name, reference_data, target_sr)
            temp_ref_path = temp_ref.name
        
        # Create output file path
        output_filename = f"transformed_{conversion_id}.{request.output_format}"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        # Perform voice transformation
        await voice_converter.convert_voice(
            input_file=temp_input_path,
            reference_file=temp_ref_path,
            output_file=output_path,
            device=request.device
        )
        
        # Clean up temporary files
        os.unlink(temp_input_path)
        os.unlink(temp_ref_path)
        
        # Verify output file exists
        if not os.path.exists(output_path):
            raise ConversionError("Voice transformation failed - no output file generated")
        
        # Get output file info
        file_size = os.path.getsize(output_path)
        output_duration = len(input_data) / target_sr
        
        processing_time = time.time() - start_time
        
        return VoiceToVoiceResponse(
            conversion_id=conversion_id,
            status=ConversionStatus.COMPLETED,
            message="Voice transformation completed successfully",
            transformation_type=request.transformation_type,
            input_duration=input_duration,
            output_duration=output_duration,
            output_file=output_filename,
            file_size=file_size,
            download_url=f"/api/v1/download/{output_filename}",
            processing_time=processing_time,
            completed_at=time.time()
        )
        
    except Exception as e:
        # Clean up any temporary files
        try:
            if 'temp_input_path' in locals():
                os.unlink(temp_input_path)
            if 'temp_ref_path' in locals():
                os.unlink(temp_ref_path)
        except:
            pass
        
        processing_time = time.time() - start_time
        
        return VoiceToVoiceResponse(
            conversion_id=conversion_id,
            status=ConversionStatus.FAILED,
            message="Voice transformation failed",
            transformation_type=request.transformation_type,
            error_message=str(e),
            processing_time=processing_time
        )


@router.get("/transformation-types",
            summary="Get Transformation Types",
            description="Get available voice transformation types and supported audio formats")
async def get_transformation_types():
    """Get available voice transformation types"""
    return {
        "transformation_types": [
            {
                "id": "voice_conversion",
                "name": "Voice Conversion",
                "description": "Convert voice characteristics using reference audio"
            },
            {
                "id": "accent_change",
                "name": "Accent Change",
                "description": "Change accent while preserving voice characteristics"
            },
            {
                "id": "gender_swap",
                "name": "Gender Swap",
                "description": "Change gender characteristics of the voice"
            },
            {
                "id": "age_change",
                "name": "Age Change",
                "description": "Modify voice to sound older or younger"
            },
            {
                "id": "emotion_change",
                "name": "Emotion Change",
                "description": "Modify emotional tone of the voice"
            }
        ],
        "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg"],
        "quality_levels": ["low", "medium", "high"]
    }


@router.get("/transformation-status/{conversion_id}",
            summary="Get Transformation Status",
            description="Get the status of a voice transformation using conversion ID")
async def get_transformation_status(conversion_id: str):
    """Get status of a voice transformation"""
    
    # This would typically check a database or cache
    # For now, we'll return a simple status
    return {
        "conversion_id": conversion_id,
        "status": "completed",
        "message": "Transformation completed"
    }


@router.get("/download/{filename}",
            summary="Download Transformed Audio",
            description="Download the transformed audio file by filename")
async def download_transformed_audio(filename: str):
    """Download transformed audio file"""
    
    # Validate filename
    allowed_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    media_type_map = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.m4a': 'audio/mp4',
        '.ogg': 'audio/ogg'
    }
    
    media_type = media_type_map.get(os.path.splitext(filename)[1].lower(), 'audio/wav')
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )
