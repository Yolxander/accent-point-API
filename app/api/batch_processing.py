"""
Batch processing endpoints for multiple file conversions
"""

import os
import tempfile
import uuid
import zipfile
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.exceptions import AudioProcessingError, FileValidationError, ConversionError
from app.services.audio_processor import AudioProcessor
from app.services.voice_converter import VoiceConverter
from app.services.batch_processor import BatchProcessor

router = APIRouter()

# Initialize services
audio_processor = AudioProcessor()
voice_converter = VoiceConverter()
batch_processor = BatchProcessor()


class BatchConversionRequest(BaseModel):
    """Request model for batch conversion"""
    device: str = "cpu"
    normalize: bool = True
    target_sample_rate: Optional[int] = None
    max_concurrent: int = 3


class BatchConversionResponse(BaseModel):
    """Response model for batch conversion"""
    batch_id: str
    status: str
    message: str
    total_files: int
    processed_files: int
    failed_files: int
    results: List[dict]
    download_url: Optional[str] = None


@router.post("/batch/convert-voices", response_model=BatchConversionResponse)
async def batch_convert_voices(
    input_files: List[UploadFile] = File(..., description="List of input audio files"),
    reference_audio: UploadFile = File(..., description="Reference audio file for voice characteristics"),
    device: str = Form("cpu"),
    normalize: bool = Form(True),
    target_sample_rate: Optional[int] = Form(None),
    max_concurrent: int = Form(3)
):
    """
    Convert multiple voice files using the same reference audio
    
    - **input_files**: List of audio files to convert
    - **reference_audio**: Reference audio file for voice characteristics
    - **device**: Processing device ('cpu' or 'cuda')
    - **normalize**: Whether to normalize audio before processing
    - **target_sample_rate**: Target sample rate for processing
    - **max_concurrent**: Maximum number of concurrent conversions
    """
    
    # Validate inputs
    if len(input_files) == 0:
        raise FileValidationError("No input files provided")
    
    if len(input_files) > 20:  # Reasonable batch limit
        raise FileValidationError("Too many files. Maximum 20 files per batch")
    
    if not reference_audio.content_type.startswith('audio/'):
        raise FileValidationError("Reference file must be an audio file")
    
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    
    try:
        # Process batch conversion
        results = await batch_processor.process_batch_conversion(
            input_files=input_files,
            reference_audio=reference_audio,
            batch_id=batch_id,
            device=device,
            normalize=normalize,
            target_sample_rate=target_sample_rate,
            max_concurrent=max_concurrent
        )
        
        # Count results
        total_files = len(input_files)
        processed_files = len([r for r in results if r.get('status') == 'completed'])
        failed_files = len([r for r in results if r.get('status') == 'failed'])
        
        # Create zip file if all conversions completed
        download_url = None
        if processed_files > 0:
            zip_filename = f"batch_conversion_{batch_id}.zip"
            zip_path = os.path.join(settings.OUTPUT_DIR, zip_filename)
            
            # Create zip file with all converted audio files
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for result in results:
                    if result.get('status') == 'completed' and result.get('output_file'):
                        file_path = os.path.join(settings.OUTPUT_DIR, result['output_file'])
                        if os.path.exists(file_path):
                            zip_file.write(file_path, result['output_file'])
            
            download_url = f"/api/v1/download/{zip_filename}"
        
        return BatchConversionResponse(
            batch_id=batch_id,
            status="completed" if failed_files == 0 else "partial",
            message=f"Batch conversion completed. {processed_files}/{total_files} files processed successfully.",
            total_files=total_files,
            processed_files=processed_files,
            failed_files=failed_files,
            results=results,
            download_url=download_url
        )
        
    except Exception as e:
        raise ConversionError(f"Batch conversion failed: {str(e)}")


@router.post("/batch/convert-texts", response_model=BatchConversionResponse)
async def batch_convert_texts(
    texts: List[str] = Form(..., description="List of texts to convert"),
    reference_audio: UploadFile = File(..., description="Reference audio file for voice characteristics"),
    device: str = Form("cpu"),
    normalize: bool = Form(True),
    target_sample_rate: Optional[int] = Form(None),
    voice_speed: float = Form(1.0),
    voice_pitch: float = Form(1.0),
    max_concurrent: int = Form(3)
):
    """
    Convert multiple texts to speech using reference audio characteristics
    
    - **texts**: List of texts to convert to speech
    - **reference_audio**: Reference audio file for voice characteristics
    - **device**: Processing device ('cpu' or 'cuda')
    - **normalize**: Whether to normalize audio before processing
    - **target_sample_rate**: Target sample rate for processing
    - **voice_speed**: Speed multiplier for generated speech
    - **voice_pitch**: Pitch multiplier for generated speech
    - **max_concurrent**: Maximum number of concurrent conversions
    """
    
    # Validate inputs
    if len(texts) == 0:
        raise FileValidationError("No texts provided")
    
    if len(texts) > 20:  # Reasonable batch limit
        raise FileValidationError("Too many texts. Maximum 20 texts per batch")
    
    if not reference_audio.content_type.startswith('audio/'):
        raise FileValidationError("Reference file must be an audio file")
    
    # Generate batch ID
    batch_id = str(uuid.uuid4())
    
    try:
        # Process batch TTS conversion
        results = await batch_processor.process_batch_tts_conversion(
            texts=texts,
            reference_audio=reference_audio,
            batch_id=batch_id,
            device=device,
            normalize=normalize,
            target_sample_rate=target_sample_rate,
            voice_speed=voice_speed,
            voice_pitch=voice_pitch,
            max_concurrent=max_concurrent
        )
        
        # Count results
        total_files = len(texts)
        processed_files = len([r for r in results if r.get('status') == 'completed'])
        failed_files = len([r for r in results if r.get('status') == 'failed'])
        
        # Create zip file if all conversions completed
        download_url = None
        if processed_files > 0:
            zip_filename = f"batch_tts_{batch_id}.zip"
            zip_path = os.path.join(settings.OUTPUT_DIR, zip_filename)
            
            # Create zip file with all converted audio files
            with zipfile.ZipFile(zip_path, 'w') as zip_file:
                for result in results:
                    if result.get('status') == 'completed' and result.get('output_file'):
                        file_path = os.path.join(settings.OUTPUT_DIR, result['output_file'])
                        if os.path.exists(file_path):
                            zip_file.write(file_path, result['output_file'])
            
            download_url = f"/api/v1/download/{zip_filename}"
        
        return BatchConversionResponse(
            batch_id=batch_id,
            status="completed" if failed_files == 0 else "partial",
            message=f"Batch TTS conversion completed. {processed_files}/{total_files} files processed successfully.",
            total_files=total_files,
            processed_files=processed_files,
            failed_files=failed_files,
            results=results,
            download_url=download_url
        )
        
    except Exception as e:
        raise ConversionError(f"Batch TTS conversion failed: {str(e)}")


@router.get("/batch/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch conversion"""
    
    # This would typically check a database or cache
    # For now, we'll return a simple status
    return {
        "batch_id": batch_id,
        "status": "completed",
        "message": "Batch processing completed"
    }
