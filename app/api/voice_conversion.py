"""
Voice conversion endpoints for audio-to-audio conversion
"""

import os
import tempfile
import uuid
import time
import glob
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
    
    # Create database record for tracking (optional)
    db_record = None
    if db_service.is_available():
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
            # Use the actual database record ID for updates
            if db_record:
                conversion_id = db_record["id"]
        except Exception as e:
            print(f"Warning: Failed to create database record: {e}")
            db_record = None
    else:
        print("Database not available - continuing without database tracking")
    
    try:
        # Read uploaded files
        input_content = await input_audio.read()
        reference_content = await reference_audio.read()
        
        # Process audio files
        input_data, input_sr = await audio_processor.load_audio_from_bytes(input_content)
        reference_data, reference_sr = await audio_processor.load_audio_from_bytes(reference_content)
        
        # Normalize and resample if requested
        target_sr = target_sample_rate or settings.TARGET_SAMPLE_RATE
        
        # Resample first, then normalize (loudness normalization needs correct sample rate)
        if input_sr != target_sr:
            input_data = audio_processor.resample_audio(input_data, input_sr, target_sr)
        if reference_sr != target_sr:
            reference_data = audio_processor.resample_audio(reference_data, reference_sr, target_sr)
        
        # Apply loudness normalization instead of peak normalization
        if normalize:
            input_data = audio_processor.normalize_loudness(input_data, target_sr)
            reference_data = audio_processor.normalize_loudness(reference_data, target_sr)
        
        # Ensure consistent format before OpenVoice (mono, 16-bit PCM compatible, target SR)
        input_data, target_sr = audio_processor.ensure_consistent_format(input_data, target_sr, target_sr)
        reference_data, target_sr = audio_processor.ensure_consistent_format(reference_data, target_sr, target_sr)
        
        # Optimize audio for OpenVoice processing
        print("Optimizing audio for OpenVoice processing...")
        input_data = audio_processor.optimize_for_openvoice(input_data, target_sr)
        reference_data = audio_processor.optimize_for_openvoice(reference_data, target_sr)
        
        # Pad short audio clips to meet minimum requirements (for practice scenarios)
        # OpenVoice works better with longer audio, so pad if too short
        input_duration = len(input_data) / target_sr
        if input_duration < 1.0:
            print(f"Input audio is short ({input_duration:.2f}s), padding to minimum 1.0s for OpenVoice...")
            input_data = audio_processor.pad_audio_to_minimum(input_data, target_sr, min_duration=1.0)
        
        reference_duration = len(reference_data) / target_sr
        # Ensure reference audio is long enough for good voice conversion
        # OpenVoice works better with longer reference audio (at least 2-3 seconds)
        min_reference_duration = 2.0
        if reference_duration < min_reference_duration:
            print(f"Reference audio is short ({reference_duration:.2f}s), padding to minimum {min_reference_duration}s for better voice conversion...")
            reference_data = audio_processor.pad_audio_to_minimum(reference_data, target_sr, min_duration=min_reference_duration)
            reference_duration = len(reference_data) / target_sr
        
        # Analyze voice content for better error messages
        input_analysis = audio_processor.analyze_voice_content(input_data, target_sr)
        reference_analysis = audio_processor.analyze_voice_content(reference_data, target_sr)
        
        print(f"Input audio analysis - Total: {input_analysis['total_duration']:.2f}s, Voice: {input_analysis['voice_duration']:.2f}s")
        print(f"Reference audio analysis - Total: {reference_analysis['total_duration']:.2f}s, Voice: {reference_analysis['voice_duration']:.2f}s")
        
        # Log conversion parameters for debugging
        print(f"Voice conversion parameters:")
        print(f"  Input (native reference): {input_analysis['total_duration']:.2f}s total, {input_analysis['voice_duration']:.2f}s voice")
        print(f"  Reference (user voice): {reference_analysis['total_duration']:.2f}s total, {reference_analysis['voice_duration']:.2f}s voice")
        print(f"  This will convert native accent audio to user's voice timbre")
        
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
        
        # Save audio data to Supabase Storage
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
                print(f"Warning: Failed to save audio to Supabase Storage: {e}")
                # Fallback to file system storage
                output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                if db_service.is_available():
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
        
        # Get public URL from database if available
        public_url = None
        if db_record:
            try:
                conversion = await db_service.get_voice_conversion(conversion_id)
                if conversion and conversion.get("output_public_url"):
                    public_url = conversion["output_public_url"]
            except Exception as e:
                print(f"Warning: Failed to get public URL: {e}")
        
        return ConversionResponse(
            conversion_id=conversion_id,
            status="completed",
            message="Voice conversion completed successfully",
            output_file=output_filename,
            file_size=file_size,
            download_url=f"/api/v1/play-voice/{conversion_id}",
            play_url=f"/api/v1/play-voice/{conversion_id}",
            public_url=public_url,  # Add public URL for direct access
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
        if db_record and db_service.is_available():
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
            description="Stream the voice conversion audio file from Supabase Storage by conversion ID")
async def play_voice_conversion_audio(conversion_id: str):
    """Play voice conversion audio file from Supabase Storage"""
    
    try:
        # Get conversion record to find the storage filename
        conversion = None
        if db_service.is_available():
            conversion = await db_service.get_voice_conversion(conversion_id)
            if not conversion:
                raise HTTPException(status_code=404, detail="Conversion not found")
        
        # If no database or no conversion record, try to find file by ID
        if not conversion:
            # Fallback: look for file in outputs directory
            filename = f"converted_{conversion_id}.wav"
            output_path = os.path.join(settings.OUTPUT_DIR, filename)
            if os.path.exists(output_path):
                # Return file directly
                return FileResponse(
                    path=output_path,
                    filename=filename,
                    media_type="audio/wav"
                )
            else:
                raise HTTPException(status_code=404, detail="Conversion not found")
        
        filename = conversion.get("output_filename")
        if not filename:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Download from Supabase Storage
        from app.services.storage_service import storage_service
        
        try:
            # Get the file from storage bucket
            file_path = f"voice_conversions/{filename}"
            audio_data = await storage_service.get_audio_file(file_path)
            
            if not audio_data:
                raise HTTPException(status_code=404, detail="Audio file not found in storage")
            
            # Return the audio data as a response
            output_format = conversion.get("output_format", "wav")
            
        except Exception as storage_error:
            raise HTTPException(status_code=404, detail=f"Failed to retrieve audio from storage: {str(storage_error)}")
        
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
