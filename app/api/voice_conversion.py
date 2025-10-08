"""
Voice conversion endpoints for audio-to-audio conversion
"""

import os
import tempfile
import uuid
import time
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import AudioProcessingError, FileValidationError, ConversionError
from app.services.audio_processor import AudioProcessor
from app.services.voice_converter import VoiceConverter
from app.services.database_service import db_service
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
    start_time = time.time()
    
    # Create database record for tracking
    try:
        db_record = await db_service.create_voice_conversion(
            user_id=None,  # Will be set when user authentication is implemented
            session_id=conversion_id,
            transformation_type="voice_conversion",
            source_audio_filename=input_audio.filename,
            source_audio_size=input_audio.size,
            reference_audio_filename=reference_audio.filename,
            reference_audio_size=reference_audio.size
        )
    except Exception as e:
        print(f"Warning: Failed to create database record: {e}")
        db_record = None
    
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
        
        # Create temporary output file path
        output_filename = f"converted_{conversion_id}.wav"
        temp_output_path = os.path.join(settings.TEMP_DIR, output_filename)
        
        # Perform voice conversion
        await voice_converter.convert_voice(
            input_file=temp_input_path,
            reference_file=temp_ref_path,
            output_file=temp_output_path,
            device=device
        )
        
        # Clean up temporary input files
        os.unlink(temp_input_path)
        os.unlink(temp_ref_path)
        
        # Verify output file exists
        if not os.path.exists(temp_output_path):
            raise ConversionError("Voice conversion failed - no output file generated")
        
        # Read the generated audio file
        with open(temp_output_path, 'rb') as f:
            audio_data = f.read()
        
        # Get file size and duration
        file_size = len(audio_data)
        output_duration = len(input_data) / target_sr
        
        processing_time = time.time() - start_time
        
        # Save audio data to database
        if db_record:
            try:
                await db_service.save_audio_to_conversion(
                    conversion_id,
                    audio_data,
                    output_filename,
                    file_size,
                    output_duration
                )
            except Exception as e:
                print(f"Warning: Failed to save audio to database: {e}")
                # Fallback to file system storage
                output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                await db_service.update_voice_conversion(
                    conversion_id,
                    status="completed",
                    output_filename=output_filename,
                    output_file_size=file_size,
                    output_duration=output_duration,
                    processing_time_seconds=processing_time,
                    completed_at=datetime.now().isoformat()
                )
        
        # Clean up temporary output file
        os.unlink(temp_output_path)
        
        # Update API usage statistics
        try:
            await db_service.update_api_usage_stats(
                user_id=None,
                endpoint="convert_voice",
                processing_time=processing_time,
                file_size=file_size
            )
        except Exception as e:
            print(f"Warning: Failed to update usage stats: {e}")
        
        return ConversionResponse(
            conversion_id=conversion_id,
            status="completed",
            message="Voice conversion completed successfully",
            output_file=output_filename,
            file_size=file_size,
            download_url=f"/api/v1/play-voice/{conversion_id}",
            play_url=f"/api/v1/play-voice/{conversion_id}",
            output_duration=output_duration,
            processing_time=processing_time,
            completed_at=datetime.now()
        )
        
    except Exception as e:
        # Clean up any temporary files
        try:
            if 'temp_input_path' in locals():
                os.unlink(temp_input_path)
            if 'temp_ref_path' in locals():
                os.unlink(temp_ref_path)
            if 'temp_output_path' in locals():
                os.unlink(temp_output_path)
        except:
            pass
        
        processing_time = time.time() - start_time
        
        # Update database record with failure details
        if db_record:
            try:
                await db_service.update_voice_conversion(
                    conversion_id,
                    status="failed",
                    error_message=str(e),
                    processing_time_seconds=processing_time
                )
            except Exception as db_error:
                print(f"Warning: Failed to update database record: {db_error}")
        
        raise ConversionError(f"Voice conversion failed: {str(e)}")


@router.get("/play-voice/{conversion_id}",
            summary="Play Voice Conversion Audio",
            description="Stream the voice conversion audio file from database by conversion ID")
async def play_voice_conversion_audio(conversion_id: str):
    """Play voice conversion audio file from database"""
    
    try:
        # Get audio data from database
        audio_data = await db_service.get_audio_from_conversion(conversion_id)
        
        if not audio_data:
            raise HTTPException(status_code=404, detail="Audio not found")
        
        # Get conversion record for metadata
        conversion = await db_service.get_voice_conversion(conversion_id)
        if not conversion:
            raise HTTPException(status_code=404, detail="Conversion not found")
        
        filename = conversion.get("output_filename", f"voice_{conversion_id}.wav")
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
        raise HTTPException(status_code=500, detail=f"Error retrieving audio: {str(e)}")


@router.get("/download/{filename}",
            summary="Download Voice Conversion Audio (Legacy)",
            description="Download the voice conversion audio file by filename (legacy endpoint for file system storage)")
async def download_converted_audio(filename: str):
    """Download converted audio file from file system (legacy)"""
    
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


@router.get("/conversion-status/{conversion_id}",
            summary="Get Voice Conversion Status",
            description="Get the status of a voice conversion using conversion ID")
async def get_conversion_status(conversion_id: str):
    """Get status of a voice conversion"""
    
    try:
        # Get conversion record from database
        conversion = await db_service.get_voice_conversion(conversion_id)
        
        if not conversion:
            raise HTTPException(status_code=404, detail="Conversion not found")
        
        return {
            "conversion_id": conversion_id,
            "status": conversion.get("status", "unknown"),
            "transformation_type": conversion.get("transformation_type", "voice_conversion"),
            "created_at": conversion.get("created_at"),
            "updated_at": conversion.get("updated_at"),
            "completed_at": conversion.get("completed_at"),
            "processing_time_seconds": conversion.get("processing_time_seconds"),
            "output_filename": conversion.get("output_filename"),
            "output_file_size": conversion.get("output_file_size"),
            "output_duration": conversion.get("output_duration"),
            "error_message": conversion.get("error_message"),
            "play_url": f"/api/v1/play-voice/{conversion_id}",
            "message": f"Conversion {conversion.get('status', 'unknown')}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversion status: {str(e)}")
