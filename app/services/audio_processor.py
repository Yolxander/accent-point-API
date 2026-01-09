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
    
    def save_audio(self, file_path: str, audio_data: np.ndarray, sample_rate: int, 
                   subtype: str = 'PCM_16') -> None:
        """
        Save audio to file as 16-bit PCM WAV
        
        Args:
            file_path: Output file path
            audio_data: Audio data array
            sample_rate: Sample rate
            subtype: Audio subtype (default: 'PCM_16' for 16-bit PCM)
        """
        try:
            # Ensure mono if stereo
            if audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Save as 16-bit PCM WAV
            sf.write(file_path, audio_data, sample_rate, subtype=subtype)
            logger.info(f"Saved audio to {file_path} ({subtype}, {sample_rate}Hz)")
            
        except Exception as e:
            logger.error(f"Failed to save audio to {file_path}: {str(e)}")
            raise AudioProcessingError(f"Failed to save audio: {str(e)}")
    
    def normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalize audio data (peak normalization - legacy method)
        
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
    
    def normalize_loudness(self, audio_data: np.ndarray, sample_rate: int, 
                          target_lufs: float = -16.0, peak_limit_db: float = -1.0) -> np.ndarray:
        """
        Normalize audio using loudness normalization (LUFS) with peak limiting
        
        This provides better quality than peak normalization by targeting
        perceived loudness rather than peak amplitude.
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate of the audio
            target_lufs: Target loudness in LUFS (default: -16.0 for speech)
            peak_limit_db: Peak limit in dB (default: -1.0)
            
        Returns:
            Loudness-normalized audio data
        """
        try:
            import pyloudnorm as pyln
            
            # Ensure audio is in the right format (mono, float32)
            if audio_data.ndim > 1:
                # Convert stereo to mono
                audio_data = np.mean(audio_data, axis=1)
            
            # Measure loudness
            meter = pyln.Meter(sample_rate)
            loudness = meter.integrated_loudness(audio_data)
            
            # Calculate gain adjustment
            if not np.isnan(loudness):
                gain_db = target_lufs - loudness
                gain_linear = 10 ** (gain_db / 20.0)
                normalized = audio_data * gain_linear
            else:
                # If loudness measurement fails, use peak normalization as fallback
                logger.warning("Loudness measurement failed, using peak normalization")
                normalized = librosa.util.normalize(audio_data)
            
            # Apply peak limiting to prevent clipping
            peak_limit_linear = 10 ** (peak_limit_db / 20.0)
            peak = np.max(np.abs(normalized))
            if peak > peak_limit_linear:
                normalized = normalized * (peak_limit_linear / peak)
            
            logger.debug(f"Loudness normalized: {loudness:.2f} LUFS -> {target_lufs:.2f} LUFS (peak limit: {peak_limit_db:.1f} dB)")
            return normalized
            
        except ImportError:
            logger.warning("pyloudnorm not available, falling back to peak normalization")
            return librosa.util.normalize(audio_data)
        except Exception as e:
            logger.error(f"Failed to normalize loudness: {str(e)}")
            # Fallback to peak normalization
            return librosa.util.normalize(audio_data)
    
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
    
    def ensure_consistent_format(self, audio_data: np.ndarray, sample_rate: int,
                                target_sr: int = 22050) -> Tuple[np.ndarray, int]:
        """
        Ensure audio is in consistent format: mono, 16-bit PCM compatible, target sample rate
        
        This ensures all audio is in the same format before OpenVoice processing,
        reducing format-related artifacts.
        
        Args:
            audio_data: Input audio data
            sample_rate: Current sample rate
            target_sr: Target sample rate (default: 22050)
            
        Returns:
            Tuple of (formatted_audio_data, target_sample_rate)
        """
        try:
            # Convert to mono if stereo
            if audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=1)
                logger.debug("Converted stereo to mono")
            
            # Resample to target sample rate if needed
            if sample_rate != target_sr:
                audio_data = self.resample_audio(audio_data, sample_rate, target_sr)
                sample_rate = target_sr
            
            # Ensure float32 format (librosa/soundfile will handle 16-bit conversion on save)
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            logger.debug(f"Audio format ensured: mono, {target_sr}Hz, float32")
            return audio_data, target_sr
            
        except Exception as e:
            logger.error(f"Failed to ensure consistent format: {str(e)}")
            raise AudioProcessingError(f"Failed to ensure consistent format: {str(e)}")
    
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
    
    def analyze_voice_content(self, audio_data: np.ndarray, sample_rate: int) -> dict:
        """
        Analyze voice content in audio data
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            
        Returns:
            Dictionary with voice analysis results
        """
        try:
            # Use librosa's voice activity detection
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Calculate frame times
            hop_length = 512
            frame_times = librosa.frames_to_time(range(len(spectral_centroids)), sr=sample_rate, hop_length=hop_length)
            
            # Voice activity detection
            voice_threshold = 0.1
            voice_frames = []
            
            for i, (centroid, rolloff, zcr) in enumerate(zip(spectral_centroids, spectral_rolloff, zero_crossing_rate)):
                if centroid > voice_threshold and zcr < 0.1:
                    voice_frames.append(i)
            
            # Convert to time segments
            voice_segments = []
            if voice_frames:
                start_frame = voice_frames[0]
                current_frame = voice_frames[0]
                
                for i in range(1, len(voice_frames)):
                    if voice_frames[i] - current_frame > 1:
                        end_time = frame_times[current_frame]
                        start_time = frame_times[start_frame]
                        if end_time - start_time > 0.1:
                            voice_segments.append((start_time, end_time))
                        start_frame = voice_frames[i]
                    current_frame = voice_frames[i]
                
                # Add final segment
                end_time = frame_times[current_frame]
                start_time = frame_times[start_frame]
                if end_time - start_time > 0.1:
                    voice_segments.append((start_time, end_time))
            
            # Calculate total voice duration
            voice_duration = sum(end - start for start, end in voice_segments)
            total_duration = len(audio_data) / sample_rate
            
            return {
                "voice_segments": voice_segments,
                "voice_duration": voice_duration,
                "total_duration": total_duration,
                "voice_ratio": voice_duration / total_duration if total_duration > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze voice content: {str(e)}")
            raise AudioProcessingError(f"Failed to analyze voice content: {str(e)}")
    
    def pad_audio_to_minimum(self, audio_data: np.ndarray, sample_rate: int, 
                            min_duration: float = 5.0) -> np.ndarray:
        """
        Pad audio with silence to meet minimum duration requirement
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            min_duration: Minimum duration in seconds
            
        Returns:
            Padded audio data
        """
        try:
            current_duration = len(audio_data) / sample_rate
            
            if current_duration >= min_duration:
                return audio_data
            
            # Calculate padding needed
            padding_duration = min_duration - current_duration
            padding_samples = int(padding_duration * sample_rate)
            
            # Add silence at the end
            padding = np.zeros(padding_samples, dtype=audio_data.dtype)
            padded_audio = np.concatenate([audio_data, padding])
            
            logger.info(f"Padded audio from {current_duration:.2f}s to {len(padded_audio) / sample_rate:.2f}s")
            return padded_audio
            
        except Exception as e:
            logger.error(f"Failed to pad audio: {str(e)}")
            raise AudioProcessingError(f"Failed to pad audio: {str(e)}")
    
    def optimize_for_openvoice(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Optimize audio for OpenVoice processing
        
        Args:
            audio_data: Input audio data
            sample_rate: Sample rate
            
        Returns:
            Optimized audio data
        """
        try:
            original_duration = len(audio_data) / sample_rate
            logger.info(f"Starting OpenVoice optimization: {original_duration:.2f}s")
            
            # Only trim if audio is longer than 8 seconds to preserve short recordings
            if original_duration > 8.0:
                # Use less aggressive trimming for better preservation
                trimmed_audio = self.trim_silence(audio_data, sample_rate, top_db=30.0)
                trimmed_duration = len(trimmed_audio) / sample_rate
                logger.info(f"Trimmed silence: {original_duration:.2f}s -> {trimmed_duration:.2f}s")
                
                # Safety check: if trimming made it too short, use less aggressive trimming
                if trimmed_duration < 4.0:
                    logger.warning(f"Trimming too aggressive ({trimmed_duration:.2f}s), trying less aggressive approach")
                    trimmed_audio = self.trim_silence(audio_data, sample_rate, top_db=40.0)
                    trimmed_duration = len(trimmed_audio) / sample_rate
                    logger.info(f"Less aggressive trimming: {original_duration:.2f}s -> {trimmed_duration:.2f}s")
                
                # If still too short, skip trimming entirely
                if trimmed_duration < 3.0:
                    logger.warning(f"Audio too short after trimming ({trimmed_duration:.2f}s), skipping trim")
                    trimmed_audio = audio_data
                    trimmed_duration = original_duration
            else:
                # For short recordings, skip trimming to preserve all content
                logger.info(f"Short recording ({original_duration:.2f}s), skipping silence trimming")
                trimmed_audio = audio_data
                trimmed_duration = original_duration
            
            # Apply gentle fade in/out to prevent clicks
            faded_audio = self.apply_fade(trimmed_audio, sample_rate, fade_in=0.05, fade_out=0.05)
            
            # Ensure minimum duration for OpenVoice with safety margin
            optimized_audio = self.pad_audio_to_minimum(faded_audio, sample_rate, min_duration=6.0)
            
            final_duration = len(optimized_audio) / sample_rate
            logger.info(f"OpenVoice optimization complete: {original_duration:.2f}s -> {final_duration:.2f}s")
            return optimized_audio
            
        except Exception as e:
            logger.error(f"Failed to optimize audio for OpenVoice: {str(e)}")
            raise AudioProcessingError(f"Failed to optimize audio for OpenVoice: {str(e)}")

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