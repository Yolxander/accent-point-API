"""
Validation utilities for the OpenVoice API
"""

import os
import magic
from typing import List, Optional
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileValidationError


class FileValidator:
    """Utility class for file validation"""
    
    @staticmethod
    def validate_audio_file(file: UploadFile) -> None:
        """
        Validate uploaded audio file
        
        Args:
            file: Uploaded file object
            
        Raises:
            FileValidationError: If file validation fails
        """
        # Check file size
        if file.size > settings.MAX_FILE_SIZE:
            raise FileValidationError(
                f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Check content type
        if not file.content_type.startswith('audio/'):
            raise FileValidationError("File must be an audio file")
        
        # Check file extension
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ['.wav', '.mp3', '.flac', '.m4a', '.ogg']:
                raise FileValidationError(
                    f"Unsupported file format: {file_ext}. "
                    f"Supported formats: .wav, .mp3, .flac, .m4a, .ogg"
                )
    
    @staticmethod
    def validate_text_input(text: str, max_length: int = 5000) -> None:
        """
        Validate text input
        
        Args:
            text: Text to validate
            max_length: Maximum allowed length
            
        Raises:
            FileValidationError: If text validation fails
        """
        if not text or not text.strip():
            raise FileValidationError("Text cannot be empty")
        
        if len(text) > max_length:
            raise FileValidationError(f"Text too long. Maximum length: {max_length} characters")
    
    @staticmethod
    def validate_device(device: str) -> None:
        """
        Validate processing device
        
        Args:
            device: Device string to validate
            
        Raises:
            FileValidationError: If device validation fails
        """
        if device not in ['cpu', 'cuda']:
            raise FileValidationError("Device must be 'cpu' or 'cuda'")
    
    @staticmethod
    def validate_voice_parameters(speed: float, pitch: float) -> None:
        """
        Validate voice parameters
        
        Args:
            speed: Voice speed multiplier
            pitch: Voice pitch multiplier
            
        Raises:
            FileValidationError: If parameter validation fails
        """
        if not 0.5 <= speed <= 2.0:
            raise FileValidationError("Voice speed must be between 0.5 and 2.0")
        
        if not 0.5 <= pitch <= 2.0:
            raise FileValidationError("Voice pitch must be between 0.5 and 2.0")
    
    @staticmethod
    def validate_batch_size(file_count: int, max_files: int = 20) -> None:
        """
        Validate batch size
        
        Args:
            file_count: Number of files in batch
            max_files: Maximum allowed files
            
        Raises:
            FileValidationError: If batch size validation fails
        """
        if file_count == 0:
            raise FileValidationError("No files provided")
        
        if file_count > max_files:
            raise FileValidationError(f"Too many files. Maximum: {max_files} files per batch")


class AudioFileAnalyzer:
    """Utility class for analyzing audio files"""
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get audio file information
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with file information
        """
        try:
            import librosa
            
            # Load audio file
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            
            # Calculate duration
            duration = len(audio_data) / sample_rate
            
            # Get number of channels
            channels = 1 if audio_data.ndim == 1 else audio_data.shape[1]
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': channels,
                'samples': len(audio_data),
                'file_size': file_size,
                'format': 'PCM'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
    
    @staticmethod
    def detect_audio_format(file_path: str) -> Optional[str]:
        """
        Detect audio format using python-magic
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Detected MIME type or None
        """
        try:
            mime_type = magic.from_file(file_path, mime=True)
            return mime_type
        except Exception:
            return None
