"""
Voice conversion endpoints for audio-to-audio conversion
"""

import os
import tempfile
import uuid
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import AudioProcessingError, FileValidationError, ConversionError
from app.services.audio_processor import AudioProcessor
from app.services.voice_converter import VoiceConverter
from app.models.conversion import ConversionRequest, ConversionResponse, ConversionStatus

router = APIRouter()

# Initialize services
audio_processor = AudioProcessor()
voice_converter = VoiceConverter()


class ConversionRequestModel(BaseModel):
    """Request model for voice conversion"""
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None


@router.post("/convert-voice", response_model=ConversionResponse)
async def convert_voice(
    input_audio: UploadFile = File(..., description="Input audio file to convert"),
    reference_audio: UploadFile = File(..., description="Reference audio file for voice characteristics"),
    device: str = "cpu",
    normalize: bool = True,
    target_sample_rate: Optional[int] = None
):
    """
    Convert voice from input audio using reference audio characteristics
    
    - **input_audio**: Audio file containing the voice to convert
    - **reference_audio**: Audio file containing the target voice characteristics
    - **device**: Processing device ('cpu' or 'cuda')
    - **normalize**: Whether to normalize audio before processing
    - **target_sample_rate**: Target sample rate for processing (default: 22050)
    """
    
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
    
    # Generate unique conversion ID
    conversion_id = str(uuid.uuid4())
    
    try:
        # Read uploaded files
        input_content = await input_audio.read()
        reference_content = await reference_audio.read()
        
        # Process audio files
        input_data, input_sr = await audio_processor.load_audio_from_bytes(input_content)
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
        
        # Create temporary files for OpenVoice processing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_input:
            audio_processor.save_audio(temp_input.name, input_data, target_sr)
            temp_input_path = temp_input.name
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_ref:
            audio_processor.save_audio(temp_ref.name, reference_data, target_sr)
            temp_ref_path = temp_ref.name
        
        # Create output file path
        output_filename = f"converted_{conversion_id}.wav"
        output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
        
        # Perform voice conversion
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
            raise ConversionError("Voice conversion failed - no output file generated")
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        return ConversionResponse(
            conversion_id=conversion_id,
            status="completed",
            message="Voice conversion completed successfully",
            output_file=output_filename,
            file_size=file_size,
            download_url=f"/api/v1/download/{output_filename}"
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
        
        raise ConversionError(f"Voice conversion failed: {str(e)}")


@router.get("/download/{filename}")
async def download_converted_audio(filename: str):
    """Download converted audio file"""
    
    # Validate filename
    if not filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/wav"
    )


@router.get("/conversion-status/{conversion_id}")
async def get_conversion_status(conversion_id: str):
    """Get status of a voice conversion"""
    
    # This would typically check a database or cache
    # For now, we'll return a simple status
    return {
        "conversion_id": conversion_id,
        "status": "completed",
        "message": "Conversion completed"
    }
