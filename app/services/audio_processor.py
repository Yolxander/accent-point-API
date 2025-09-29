"""
Audio processing service for handling audio file operations
"""

import librosa
import soundfile as sf
import numpy as np
from typing import Tuple, Optional
import io
import logging

from app.core.exceptions import AudioProcessingError

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for audio processing operations"""
    
    def __init__(self):
        self.supported_formats = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    
    async def load_audio_from_bytes(self, audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """
        Load audio from bytes
        
        Args:
            audio_bytes: Audio file bytes
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            # Create a BytesIO object from the bytes
            audio_io = io.BytesIO(audio_bytes)
            
            # Load audio using librosa
            audio_data, sample_rate = librosa.load(audio_io, sr=None)
            
            logger.info(f"Loaded audio: {len(audio_data)} samples at {sample_rate}Hz")
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to load audio from bytes: {str(e)}")
            raise AudioProcessingError(f"Failed to load audio: {str(e)}")
    
    async def load_audio_from_file(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio from file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            logger.info(f"Loaded audio from {file_path}: {len(audio_data)} samples at {sample_rate}Hz")
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to load audio from file {file_path}: {str(e)}")
            raise AudioProcessingError(f"Failed to load audio from file: {str(e)}")
    
    def save_audio(self, file_path: str, audio_data: np.ndarray, sample_rate: int) -> None:
        """
        Save audio to file
        
        Args:
            file_path: Output file path
            audio_data: Audio data array
            sample_rate: Sample rate
        """
        try:
            sf.write(file_path, audio_data, sample_rate)
            logger.info(f"Saved audio to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save audio to {file_path}: {str(e)}")
            raise AudioProcessingError(f"Failed to save audio: {str(e)}")
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio data
        
        Args:
            audio_data: Input audio data
            
        Returns:
            Normalized audio data
        """
        try:
            normalized = librosa.util.normalize(audio_data)
            logger.debug("Audio normalized successfully")
            return normalized
            
        except Exception as e:
            logger.error(f"Failed to normalize audio: {str(e)}")
            raise AudioProcessingError(f"Failed to normalize audio: {str(e)}")
    
    def resample_audio(self, audio_data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """
        Resample audio to target sample rate
        
        Args:
            audio_data: Input audio data
            orig_sr: Original sample rate
            target_sr: Target sample rate
            
        Returns:
            Resampled audio data
        """
        try:
            if orig_sr == target_sr:
                return audio_data
                
            resampled = librosa.resample(audio_data, orig_sr=orig_sr, target_sr=target_sr)
            logger.info(f"Resampled audio from {orig_sr}Hz to {target_sr}Hz")
            return resampled
            
        except Exception as e:
            logger.error(f"Failed to resample audio: {str(e)}")
            raise AudioProcessingError(f"Failed to resample audio: {str(e)}")
    
    def get_audio_info(self, audio_data: np.ndarray, sample_rate: int) -> dict:
        """
        Get audio information
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate
            
        Returns:
            Dictionary with audio information
        """
        try:
            duration = len(audio_data) / sample_rate
            channels = 1 if audio_data.ndim == 1 else audio_data.shape[1]
            
            return {
                "duration": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "samples": len(audio_data),
                "bit_depth": 16,  # Assuming 16-bit
                "format": "PCM"
            }
            
        except Exception as e:
            logger.error(f"Failed to get audio info: {str(e)}")
            raise AudioProcessingError(f"Failed to get audio info: {str(e)}")
    
    def trim_silence(self, audio_data: np.ndarray, sample_rate: int, 
                    top_db: float = 20.0) -> np.ndarray:
        """
        Trim silence from audio
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            top_db: Silence threshold in dB
            
        Returns:
            Trimmed audio data
        """
        try:
            trimmed, _ = librosa.effects.trim(audio_data, top_db=top_db)
            logger.info(f"Trimmed silence: {len(audio_data)} -> {len(trimmed)} samples")
            return trimmed
            
        except Exception as e:
            logger.error(f"Failed to trim silence: {str(e)}")
            raise AudioProcessingError(f"Failed to trim silence: {str(e)}")
    
    def apply_fade(self, audio_data: np.ndarray, sample_rate: int, 
                   fade_in: float = 0.1, fade_out: float = 0.1) -> np.ndarray:
        """
        Apply fade in/out to audio
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            fade_in: Fade in duration in seconds
            fade_out: Fade out duration in seconds
            
        Returns:
            Audio data with fade effects
        """
        try:
            # Convert to samples
            fade_in_samples = int(fade_in * sample_rate)
            fade_out_samples = int(fade_out * sample_rate)
            
            # Apply fade in
            if fade_in_samples > 0:
                fade_in_curve = np.linspace(0, 1, fade_in_samples)
                audio_data[:fade_in_samples] *= fade_in_curve
            
            # Apply fade out
            if fade_out_samples > 0:
                fade_out_curve = np.linspace(1, 0, fade_out_samples)
                audio_data[-fade_out_samples:] *= fade_out_curve
            
            logger.debug(f"Applied fade in/out: {fade_in}s in, {fade_out}s out")
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to apply fade: {str(e)}")
            raise AudioProcessingError(f"Failed to apply fade: {str(e)}")
    
    async def pitch_shift(self, audio_data: np.ndarray, sample_rate: int, 
                         semitones: float) -> np.ndarray:
        """
        Apply pitch shift to audio
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            semitones: Pitch shift in semitones (-12 to 12)
            
        Returns:
            Pitch-shifted audio data
        """
        try:
            if semitones == 0:
                return audio_data
                
            # Convert semitones to ratio
            pitch_ratio = 2 ** (semitones / 12.0)
            
            # Apply pitch shift
            shifted = librosa.effects.pitch_shift(audio_data, sr=sample_rate, n_steps=semitones)
            
            logger.info(f"Applied pitch shift: {semitones} semitones")
            return shifted
            
        except Exception as e:
            logger.error(f"Failed to apply pitch shift: {str(e)}")
            raise AudioProcessingError(f"Failed to apply pitch shift: {str(e)}")
    
    async def speed_change(self, audio_data: np.ndarray, sample_rate: int, 
                          speed_factor: float) -> np.ndarray:
        """
        Change speed of audio
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            speed_factor: Speed multiplier (0.5 to 2.0)
            
        Returns:
            Speed-changed audio data
        """
        try:
            if speed_factor == 1.0:
                return audio_data
                
            # Apply speed change
            changed = librosa.effects.time_stretch(audio_data, rate=speed_factor)
            
            logger.info(f"Applied speed change: {speed_factor}x")
            return changed
            
        except Exception as e:
            logger.error(f"Failed to apply speed change: {str(e)}")
            raise AudioProcessingError(f"Failed to apply speed change: {str(e)}")
    
    async def volume_adjust(self, audio_data: np.ndarray, volume_factor: float) -> np.ndarray:
        """
        Adjust volume of audio
        
        Args:
            audio_data: Input audio data
            volume_factor: Volume multiplier (0.1 to 3.0)
            
        Returns:
            Volume-adjusted audio data
        """
        try:
            if volume_factor == 1.0:
                return audio_data
                
            # Apply volume adjustment
            adjusted = audio_data * volume_factor
            
            # Prevent clipping
            if np.max(np.abs(adjusted)) > 1.0:
                adjusted = adjusted / np.max(np.abs(adjusted))
            
            logger.info(f"Applied volume adjustment: {volume_factor}x")
            return adjusted
            
        except Exception as e:
            logger.error(f"Failed to apply volume adjustment: {str(e)}")
            raise AudioProcessingError(f"Failed to apply volume adjustment: {str(e)}")
    
    async def noise_reduction(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply noise reduction to audio
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            
        Returns:
            Noise-reduced audio data
        """
        try:
            # Simple noise reduction using spectral gating
            # This is a basic implementation - more sophisticated methods could be used
            
            # Compute STFT
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimate noise floor (using first 10% of audio)
            noise_frames = int(0.1 * stft.shape[1])
            noise_floor = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # Apply spectral gating
            gate_threshold = noise_floor * 2.0
            mask = magnitude > gate_threshold
            magnitude_clean = magnitude * mask
            
            # Reconstruct audio
            stft_clean = magnitude_clean * np.exp(1j * phase)
            audio_clean = librosa.istft(stft_clean)
            
            logger.info("Applied noise reduction")
            return audio_clean
            
        except Exception as e:
            logger.error(f"Failed to apply noise reduction: {str(e)}")
            raise AudioProcessingError(f"Failed to apply noise reduction: {str(e)}")
    
    async def echo_removal(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Remove echo from audio
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            
        Returns:
            Echo-removed audio data
        """
        try:
            # Simple echo removal using spectral subtraction
            # This is a basic implementation
            
            # Compute STFT
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Apply spectral subtraction (reduce low-magnitude components)
            alpha = 0.1  # Subtraction factor
            magnitude_clean = magnitude - alpha * np.mean(magnitude, axis=1, keepdims=True)
            magnitude_clean = np.maximum(magnitude_clean, 0.01 * magnitude)  # Prevent over-subtraction
            
            # Reconstruct audio
            stft_clean = magnitude_clean * np.exp(1j * phase)
            audio_clean = librosa.istft(stft_clean)
            
            logger.info("Applied echo removal")
            return audio_clean
            
        except Exception as e:
            logger.error(f"Failed to apply echo removal: {str(e)}")
            raise AudioProcessingError(f"Failed to apply echo removal: {str(e)}")
    
    async def voice_enhancement(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Enhance voice quality
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            
        Returns:
            Voice-enhanced audio data
        """
        try:
            # Apply a combination of enhancements
            
            # 1. Normalize
            enhanced = librosa.util.normalize(audio_data)
            
            # 2. Apply pre-emphasis filter
            enhanced = librosa.effects.preemphasis(enhanced)
            
            # 3. Apply gentle compression
            enhanced = np.tanh(enhanced * 1.2)  # Soft compression
            
            # 4. Apply high-pass filter to remove low-frequency noise
            from scipy import signal
            nyquist = sample_rate / 2
            cutoff = 80  # Hz
            b, a = signal.butter(4, cutoff / nyquist, btype='high')
            enhanced = signal.filtfilt(b, a, enhanced)
            
            logger.info("Applied voice enhancement")
            return enhanced
            
        except Exception as e:
            logger.error(f"Failed to apply voice enhancement: {str(e)}")
            raise AudioProcessingError(f"Failed to apply voice enhancement: {str(e)}")