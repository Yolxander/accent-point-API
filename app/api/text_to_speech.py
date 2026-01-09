"""
Text-to-speech endpoints with voice conversion
"""

import os
import tempfile
import uuid
import time
from typing import Optional, Dict, Tuple
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import AudioProcessingError, FileValidationError, ConversionError
from app.services.audio_processor import AudioProcessor
from app.services.tts_service import TTSService
from app.models.conversion import ConversionResponse

router = APIRouter()

# Initialize services
audio_processor = AudioProcessor()
tts_service = TTSService()

# In-memory cache for TTS audio data (conversion_id -> (audio_data, timestamp))
# This allows the /play-tts endpoint to retrieve audio after generation
_tts_audio_cache: Dict[str, Tuple[bytes, float]] = {}
CACHE_EXPIRY_SECONDS = 3600  # 1 hour


class TTSRequestModel(BaseModel):
    """Request model for text-to-speech conversion"""
    text: str
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None
    voice_speed: float = 1.0
    voice_pitch: float = 1.0


@router.post("/convert-text-to-speech", response_model=ConversionResponse)
async def convert_text_to_speech(
    text: str = Form(..., description="Text to convert to speech"),
    normalize: bool = Form(True),
    target_sample_rate: Optional[int] = Form(None),
    voice_speed: float = Form(1.0),
    voice_pitch: float = Form(1.0)
):
    """
    Convert text to speech using high-quality TTS (Piper)
    
    - **text**: Text to convert to speech
    - **normalize**: Whether to normalize audio before processing
    - **target_sample_rate**: Target sample rate for processing (default: 22050)
    - **voice_speed**: Speed multiplier for generated speech (0.5-2.0)
    - **voice_pitch**: Pitch multiplier for generated speech (0.5-2.0)
    """
    
    # Validate inputs
    if not text.strip():
        raise FileValidationError("Text cannot be empty")
    
    if len(text) > 5000:  # Reasonable limit for TTS
        raise FileValidationError("Text too long. Maximum 5000 characters")
    
    # Validate voice parameters
    if not 0.5 <= voice_speed <= 2.0:
        raise FileValidationError("Voice speed must be between 0.5 and 2.0")
    
    if not 0.5 <= voice_pitch <= 2.0:
        raise FileValidationError("Voice pitch must be between 0.5 and 2.0")
    
    # Generate unique conversion ID
    conversion_id = str(uuid.uuid4())
    
    try:
        # Step 1: Generate TTS audio from text (high-quality native TTS)
        tts_audio_data, tts_sample_rate = await tts_service.generate_speech(
            text=text,
            speed=voice_speed,
            pitch=voice_pitch
        )
        
        # Step 2: Normalize and resample
        target_sr = target_sample_rate or settings.TARGET_SAMPLE_RATE
        
        if tts_sample_rate != target_sr:
            tts_audio_data = audio_processor.resample_audio(tts_audio_data, tts_sample_rate, target_sr)
        
        # Step 3: Create temporary file for saving
        output_filename = f"tts_{conversion_id}.wav"
        temp_output_path = os.path.join(settings.TEMP_DIR, output_filename)
        
        # Step 4: Save audio (normalization will be applied in audio_processor if needed)
        audio_processor.save_audio(temp_output_path, tts_audio_data, target_sr)
        
        # Step 5: Read the generated audio file
        with open(temp_output_path, 'rb') as f:
            audio_data = f.read()
        
        # Get file size
        file_size = len(audio_data)
        output_duration = len(tts_audio_data) / target_sr
        
        # Store audio data in cache for /play-tts endpoint
        _tts_audio_cache[conversion_id] = (audio_data, time.time())
        
        # Clean up temporary output file
        os.unlink(temp_output_path)
        
        return ConversionResponse(
            conversion_id=conversion_id,
            status="completed",
            message="Text-to-speech conversion completed successfully",
            output_file=output_filename,
            file_size=file_size,
            download_url=f"/api/v1/play-tts/{conversion_id}"
        )
        
    except Exception as e:
        # Clean up any temporary files
        try:
            if 'temp_output_path' in locals() and os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
        except:
            pass
        
        raise ConversionError(f"Text-to-speech conversion failed: {str(e)}")


@router.post("/preview-tts")
async def preview_tts(
    text: str = Form(..., description="Text to preview"),
    voice_speed: float = Form(1.0),
    voice_pitch: float = Form(1.0)
):
    """
    Generate a preview of text-to-speech without voice conversion
    """
    
    if not text.strip():
        raise FileValidationError("Text cannot be empty")
    
    if len(text) > 1000:  # Shorter limit for preview
        raise FileValidationError("Text too long for preview. Maximum 1000 characters")
    
    try:
        # Generate TTS audio
        tts_audio_data, tts_sample_rate = await tts_service.generate_speech(
            text=text,
            speed=voice_speed,
            pitch=voice_pitch
        )
        
        # Create temporary file for preview
        conversion_id = str(uuid.uuid4())
        output_filename = f"tts_preview_{conversion_id}.wav"
        temp_output_path = os.path.join(settings.TEMP_DIR, output_filename)
        
        # Save preview audio
        audio_processor.save_audio(temp_output_path, tts_audio_data, tts_sample_rate)
        
        # Read the generated audio file
        with open(temp_output_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up temporary file
        os.unlink(temp_output_path)
        
        return {
            "conversion_id": conversion_id,
            "status": "completed",
            "message": "TTS preview generated successfully",
            "output_file": output_filename,
            "download_url": f"/api/v1/play-tts/{conversion_id}",
            "audio_data": audio_data  # Include audio data for immediate playback
        }
        
    except Exception as e:
        raise ConversionError(f"TTS preview generation failed: {str(e)}")


@router.get("/play-tts/{conversion_id}",
            summary="Play TTS Audio",
            description="Stream the text-to-speech audio file by conversion ID")
async def play_tts_audio(conversion_id: str):
    """Play text-to-speech audio file from cache"""
    
    try:
        # Clean up expired cache entries
        current_time = time.time()
        expired_ids = [
            cid for cid, (_, timestamp) in _tts_audio_cache.items()
            if current_time - timestamp > CACHE_EXPIRY_SECONDS
        ]
        for cid in expired_ids:
            del _tts_audio_cache[cid]
        
        # Get audio data from cache
        if conversion_id not in _tts_audio_cache:
            raise HTTPException(status_code=404, detail="TTS audio not found or expired")
        
        audio_data, _ = _tts_audio_cache[conversion_id]
        
        # Determine filename from conversion_id
        filename = f"tts_{conversion_id}.wav"
        
        # Return audio data as streaming response
        return Response(
            content=audio_data,
            media_type='audio/wav',
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Accept-Ranges": "bytes"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TTS audio: {str(e)}")
