"""
Voice conversion service using OpenVoice CLI
"""

import os
import tempfile
import logging
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.core.exceptions import ConversionError

logger = logging.getLogger(__name__)


class VoiceConverter:
    """Service for voice conversion using OpenVoice AI"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._openvoice_available = None
    
    async def _check_openvoice_availability(self) -> bool:
        """Check if OpenVoice CLI is available"""
        if self._openvoice_available is not None:
            return self._openvoice_available
        
        try:
            import openvoice_cli.__main__ as openvoice_main
            self._openvoice_available = True
            logger.info("OpenVoice CLI is available")
            return True
        except ImportError as e:
            logger.error(f"OpenVoice CLI not available: {str(e)}")
            self._openvoice_available = False
            return False
    
    async def convert_voice(self, input_file: str, reference_file: str, 
                          output_file: str, device: str = "cpu") -> None:
        """
        Convert voice using OpenVoice AI
        
        Args:
            input_file: Path to input audio file
            reference_file: Path to reference audio file
            output_file: Path to output audio file
            device: Processing device ('cpu' or 'cuda')
        """
        try:
            # Check OpenVoice availability
            if not await self._check_openvoice_availability():
                raise ConversionError("OpenVoice CLI is not available")
            
            # Validate input files
            if not os.path.exists(input_file):
                raise ConversionError(f"Input file not found: {input_file}")
            
            if not os.path.exists(reference_file):
                raise ConversionError(f"Reference file not found: {reference_file}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            logger.info(f"Starting voice conversion: {input_file} -> {output_file}")
            logger.info(f"Using device: {device}")
            
            # Run conversion in thread pool to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._run_openvoice_conversion,
                input_file,
                reference_file,
                output_file,
                device
            )
            
            # Verify output file was created
            if not os.path.exists(output_file):
                raise ConversionError("Voice conversion failed - no output file generated")
            
            logger.info(f"Voice conversion completed successfully: {output_file}")
            
        except Exception as e:
            logger.error(f"Voice conversion failed: {str(e)}")
            raise ConversionError(f"Voice conversion failed: {str(e)}")
    
    def _run_openvoice_conversion(self, input_file: str, reference_file: str, 
                                output_file: str, device: str) -> None:
        """
        Run OpenVoice conversion (blocking operation)
        
        Args:
            input_file: Path to input audio file
            reference_file: Path to reference audio file
            output_file: Path to output audio file
            device: Processing device
        """
        try:
            # Import OpenVoice CLI
            import openvoice_cli.__main__ as openvoice_main
            tune_one = openvoice_main.tune_one
            
            # Run the conversion
            tune_one(
                input_file=input_file,
                ref_file=reference_file,
                output_file=output_file,
                device=device
            )
            
        except Exception as e:
            logger.error(f"OpenVoice conversion error: {str(e)}")
            raise ConversionError(f"OpenVoice conversion error: {str(e)}")
    
    async def get_conversion_info(self, input_file: str, reference_file: str) -> dict:
        """
        Get information about the conversion process
        
        Args:
            input_file: Path to input audio file
            reference_file: Path to reference audio file
            
        Returns:
            Dictionary with conversion information
        """
        try:
            # Check file sizes
            input_size = os.path.getsize(input_file) if os.path.exists(input_file) else 0
            ref_size = os.path.getsize(reference_file) if os.path.exists(reference_file) else 0
            
            # Estimate processing time (rough approximation)
            estimated_time = (input_size + ref_size) / (1024 * 1024) * 2  # 2 seconds per MB
            
            return {
                "input_file_size": input_size,
                "reference_file_size": ref_size,
                "estimated_processing_time": max(estimated_time, 10),  # Minimum 10 seconds
                "device": settings.OPENVOICE_DEVICE,
                "openvoice_available": await self._check_openvoice_availability()
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversion info: {str(e)}")
            return {
                "error": str(e),
                "openvoice_available": await self._check_openvoice_availability()
            }
    
    async def cleanup_temp_files(self, *file_paths: str) -> None:
        """
        Clean up temporary files
        
        Args:
            *file_paths: Paths to files to clean up
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up file {file_path}: {str(e)}")
    
    def __del__(self):
        """Cleanup executor on destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
