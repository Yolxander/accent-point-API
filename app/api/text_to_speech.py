"""
Text-to-speech endpoints with voice conversion
"""

import os
import tempfile
import uuid
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import AudioProcessingError, FileValidationError, ConversionError
from app.services.audio_processor import AudioProcessor
from app.services.voice_converter import VoiceConverter
from app.services.tts_service import TTSService
from app.models.conversion import ConversionResponse

router = APIRouter()

# Initialize services
audio_processor = AudioProcessor()
voice_converter = VoiceConverter()
tts_service = TTSService()


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
    reference_audio: UploadFile = File(..., description="Reference audio file for voice characteristics"),
    device: str = Form("cpu"),
    normalize: bool = Form(True),
    target_sample_rate: Optional[int] = Form(None),
    voice_speed: float = Form(1.0),
    voice_pitch: float = Form(1.0)
):
    """
    Convert text to speech using reference audio voice characteristics
    
    - **text**: Text to convert to speech
    - **reference_audio**: Audio file containing the target voice characteristics
    - **device**: Processing device ('cpu' or 'cuda')
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
    
    if not reference_audio.content_type.startswith('audio/'):
        raise FileValidationError("Reference file must be an audio file")
    
    if reference_audio.size > settings.MAX_FILE_SIZE:
        raise FileValidationError(f"Reference file too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")
    
    # Validate voice parameters
    if not 0.5 <= voice_speed <= 2.0:
        raise FileValidationError("Voice speed must be between 0.5 and 2.0")
    
    if not 0.5 <= voice_pitch <= 2.0:
        raise FileValidationError("Voice pitch must be between 0.5 and 2.0")
    
    # Generate unique conversion ID
    conversion_id = str(uuid.uuid4())
    
    try:
        # Step 1: Generate TTS audio from text
        tts_audio_data, tts_sample_rate = await tts_service.generate_speech(
            text=text,
            speed=voice_speed,
            pitch=voice_pitch
        )
        
        # Step 2: Load reference audio
        reference_content = await reference_audio.read()
        reference_data, reference_sr = await audio_processor.load_audio_from_bytes(reference_content)
        
        # Step 3: Normalize and resample both audios
        if normalize:
            tts_audio_data = audio_processor.normalize_audio(tts_audio_data)
            reference_data = audio_processor.normalize_audio(reference_data)
        
        target_sr = target_sample_rate or settings.TARGET_SAMPLE_RATE
        
        if tts_sample_rate != target_sr:
            tts_audio_data = audio_processor.resample_audio(tts_audio_data, tts_sample_rate, target_sr)
        
        if reference_sr != target_sr:
            reference_data = audio_processor.resample_audio(reference_data, reference_sr, target_sr)
        
        # Step 4: Create temporary files for OpenVoice processing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_tts:
            audio_processor.save_audio(temp_tts.name, tts_audio_data, target_sr)
            temp_tts_path = temp_tts.name
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_ref:
            audio_processor.save_audio(temp_ref.name, reference_data, target_sr)
            temp_ref_path = temp_ref.name
        
        # Step 5: Create temporary output file path
        output_filename = f"tts_converted_{conversion_id}.wav"
        temp_output_path = os.path.join(settings.TEMP_DIR, output_filename)
        
        # Step 6: Apply voice characteristics using OpenVoice
        await voice_converter.convert_voice(
            input_file=temp_tts_path,
            reference_file=temp_ref_path,
            output_file=temp_output_path,
            device=device
        )
        
        # Clean up temporary input files
        os.unlink(temp_tts_path)
        os.unlink(temp_ref_path)
        
        # Verify output file exists
        if not os.path.exists(temp_output_path):
            raise ConversionError("Text-to-speech conversion failed - no output file generated")
        
        # Read the generated audio file
        with open(temp_output_path, 'rb') as f:
            audio_data = f.read()
        
        # Get file size
        file_size = len(audio_data)
        output_duration = len(tts_audio_data) / target_sr
        
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
            if 'temp_tts_path' in locals():
                os.unlink(temp_tts_path)
            if 'temp_ref_path' in locals():
                os.unlink(temp_ref_path)
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
            description="Stream the text-to-speech audio file from database by conversion ID")
async def play_tts_audio(conversion_id: str):
    """Play text-to-speech audio file from database"""
    
    try:
        # Get audio data from database
        audio_data = await db_service.get_audio_from_tts_conversion(conversion_id)
        
        if not audio_data:
            raise HTTPException(status_code=404, detail="TTS audio not found")
        
        # Get conversion record for metadata
        conversion = await db_service.get_text_to_speech_conversion(conversion_id)
        if not conversion:
            raise HTTPException(status_code=404, detail="TTS conversion not found")
        
        filename = conversion.get("output_filename", f"tts_{conversion_id}.wav")
        output_format = conversion.get("output_format", "wav")
        
        # Determine media type based on output format
        media_type_map = {
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'flac': 'audio/flac',
            'm4a': 'audio/mp4',
            'ogg': 'audio/ogg'
        }
        
        media_type = media_type_map.get(output_format.lower(), 'audio/wav')
        
        # Return audio data as streaming response
        from fastapi.responses import Response
        return Response(
            content=audio_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Accept-Ranges": "bytes"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving TTS audio: {str(e)}")
