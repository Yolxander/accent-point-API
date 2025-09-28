"""
Batch processing service for handling multiple conversions
"""

import asyncio
import logging
from typing import List, Dict, Any
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ConversionError
from app.services.audio_processor import AudioProcessor
from app.services.voice_converter import VoiceConverter
from app.services.tts_service import TTSService

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Service for batch processing multiple conversions"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.voice_converter = VoiceConverter()
        self.tts_service = TTSService()
    
    async def process_batch_conversion(self, input_files: List[UploadFile], 
                                     reference_audio: UploadFile, batch_id: str,
                                     device: str = "cpu", normalize: bool = True,
                                     target_sample_rate: int = None,
                                     max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """
        Process batch voice conversion
        
        Args:
            input_files: List of input audio files
            reference_audio: Reference audio file
            batch_id: Unique batch identifier
            device: Processing device
            normalize: Whether to normalize audio
            target_sample_rate: Target sample rate
            max_concurrent: Maximum concurrent conversions
            
        Returns:
            List of conversion results
        """
        try:
            logger.info(f"Starting batch conversion {batch_id} with {len(input_files)} files")
            
            # Load reference audio once
            reference_content = await reference_audio.read()
            reference_data, reference_sr = await self.audio_processor.load_audio_from_bytes(reference_content)
            
            if normalize:
                reference_data = self.audio_processor.normalize_audio(reference_data)
            
            target_sr = target_sample_rate or settings.TARGET_SAMPLE_RATE
            if reference_sr != target_sr:
                reference_data = self.audio_processor.resample_audio(reference_data, reference_sr, target_sr)
            
            # Create semaphore to limit concurrent conversions
            semaphore = asyncio.Semaphore(max_concurrent)
            
            # Process files concurrently
            tasks = []
            for i, input_file in enumerate(input_files):
                task = self._process_single_conversion(
                    input_file, reference_data, target_sr, 
                    batch_id, i, device, normalize, semaphore
                )
                tasks.append(task)
            
            # Wait for all conversions to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'file_index': i,
                        'filename': input_files[i].filename,
                        'status': 'failed',
                        'error': str(result)
                    })
                else:
                    processed_results.append(result)
            
            logger.info(f"Batch conversion {batch_id} completed: {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch conversion {batch_id} failed: {str(e)}")
            raise ConversionError(f"Batch conversion failed: {str(e)}")
    
    async def _process_single_conversion(self, input_file: UploadFile, 
                                       reference_data, target_sr: int,
                                       batch_id: str, file_index: int,
                                       device: str, normalize: bool,
                                       semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Process a single file conversion"""
        async with semaphore:
            try:
                logger.info(f"Processing file {file_index} in batch {batch_id}")
                
                # Load input audio
                input_content = await input_file.read()
                input_data, input_sr = await self.audio_processor.load_audio_from_bytes(input_content)
                
                if normalize:
                    input_data = self.audio_processor.normalize_audio(input_data)
                
                if input_sr != target_sr:
                    input_data = self.audio_processor.resample_audio(input_data, input_sr, target_sr)
                
                # Create temporary files
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_input:
                    self.audio_processor.save_audio(temp_input.name, input_data, target_sr)
                    temp_input_path = temp_input.name
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_ref:
                    self.audio_processor.save_audio(temp_ref.name, reference_data, target_sr)
                    temp_ref_path = temp_ref.name
                
                # Create output file path
                output_filename = f"batch_{batch_id}_file_{file_index}.wav"
                output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
                
                # Perform conversion
                await self.voice_converter.convert_voice(
                    input_file=temp_input_path,
                    reference_file=temp_ref_path,
                    output_file=output_path,
                    device=device
                )
                
                # Clean up temporary files
                os.unlink(temp_input_path)
                os.unlink(temp_ref_path)
                
                # Get file size
                file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                
                return {
                    'file_index': file_index,
                    'filename': input_file.filename,
                    'status': 'completed',
                    'output_file': output_filename,
                    'file_size': file_size,
                    'download_url': f"/api/v1/download/{output_filename}"
                }
                
            except Exception as e:
                logger.error(f"Failed to process file {file_index} in batch {batch_id}: {str(e)}")
                return {
                    'file_index': file_index,
                    'filename': input_file.filename,
                    'status': 'failed',
                    'error': str(e)
                }
    
    async def process_batch_tts_conversion(self, texts: List[str], 
                                         reference_audio: UploadFile, batch_id: str,
                                         device: str = "cpu", normalize: bool = True,
                                         target_sample_rate: int = None,
                                         voice_speed: float = 1.0, voice_pitch: float = 1.0,
                                         max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """
        Process batch text-to-speech conversion
        
        Args:
            texts: List of texts to convert
            reference_audio: Reference audio file
            batch_id: Unique batch identifier
            device: Processing device
            normalize: Whether to normalize audio
            target_sample_rate: Target sample rate
            voice_speed: Speech speed multiplier
            voice_pitch: Speech pitch multiplier
            max_concurrent: Maximum concurrent conversions
            
        Returns:
            List of conversion results
        """
        try:
            logger.info(f"Starting batch TTS conversion {batch_id} with {len(texts)} texts")
            
            # Load reference audio once
            reference_content = await reference_audio.read()
            reference_data, reference_sr = await self.audio_processor.load_audio_from_bytes(reference_content)
            
            if normalize:
                reference_data = self.audio_processor.normalize_audio(reference_data)
            
            target_sr = target_sample_rate or settings.TARGET_SAMPLE_RATE
            if reference_sr != target_sr:
                reference_data = self.audio_processor.resample_audio(reference_data, reference_sr, target_sr)
            
            # Create semaphore to limit concurrent conversions
            semaphore = asyncio.Semaphore(max_concurrent)
            
            # Process texts concurrently
            tasks = []
            for i, text in enumerate(texts):
                task = self._process_single_tts_conversion(
                    text, reference_data, target_sr,
                    batch_id, i, device, normalize,
                    voice_speed, voice_pitch, semaphore
                )
                tasks.append(task)
            
            # Wait for all conversions to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'text_index': i,
                        'text_preview': texts[i][:50] + "..." if len(texts[i]) > 50 else texts[i],
                        'status': 'failed',
                        'error': str(result)
                    })
                else:
                    processed_results.append(result)
            
            logger.info(f"Batch TTS conversion {batch_id} completed: {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch TTS conversion {batch_id} failed: {str(e)}")
            raise ConversionError(f"Batch TTS conversion failed: {str(e)}")
    
    async def _process_single_tts_conversion(self, text: str, reference_data, target_sr: int,
                                           batch_id: str, text_index: int,
                                           device: str, normalize: bool,
                                           voice_speed: float, voice_pitch: float,
                                           semaphore: asyncio.Semaphore) -> Dict[str, Any]:
        """Process a single text-to-speech conversion"""
        async with semaphore:
            try:
                logger.info(f"Processing text {text_index} in batch {batch_id}")
                
                # Generate TTS audio
                tts_audio_data, tts_sample_rate = await self.tts_service.generate_speech(
                    text=text,
                    speed=voice_speed,
                    pitch=voice_pitch
                )
                
                if normalize:
                    tts_audio_data = self.audio_processor.normalize_audio(tts_audio_data)
                
                if tts_sample_rate != target_sr:
                    tts_audio_data = self.audio_processor.resample_audio(tts_audio_data, tts_sample_rate, target_sr)
                
                # Create temporary files
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_tts:
                    self.audio_processor.save_audio(temp_tts.name, tts_audio_data, target_sr)
                    temp_tts_path = temp_tts.name
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=settings.TEMP_DIR) as temp_ref:
                    self.audio_processor.save_audio(temp_ref.name, reference_data, target_sr)
                    temp_ref_path = temp_ref.name
                
                # Create output file path
                output_filename = f"batch_tts_{batch_id}_text_{text_index}.wav"
                output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
                
                # Perform conversion
                await self.voice_converter.convert_voice(
                    input_file=temp_tts_path,
                    reference_file=temp_ref_path,
                    output_file=output_path,
                    device=device
                )
                
                # Clean up temporary files
                os.unlink(temp_tts_path)
                os.unlink(temp_ref_path)
                
                # Get file size
                file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                
                return {
                    'text_index': text_index,
                    'text_preview': text[:50] + "..." if len(text) > 50 else text,
                    'status': 'completed',
                    'output_file': output_filename,
                    'file_size': file_size,
                    'download_url': f"/api/v1/download/{output_filename}"
                }
                
            except Exception as e:
                logger.error(f"Failed to process text {text_index} in batch {batch_id}: {str(e)}")
                return {
                    'text_index': text_index,
                    'text_preview': text[:50] + "..." if len(text) > 50 else text,
                    'status': 'failed',
                    'error': str(e)
                }
