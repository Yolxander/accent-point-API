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
    
    async def _validate_audio_length(self, input_file: str, reference_file: str) -> None:
        """Validate that audio files meet minimum length requirements"""
        logger.info(f"Validating audio length for input: {input_file}, reference: {reference_file}")
        
        try:
            import librosa
            
            # Load audio files to check duration
            input_duration = librosa.get_duration(filename=input_file)
            reference_duration = librosa.get_duration(filename=reference_file)
            
            # OpenVoice requires minimum audio length for reliable conversion
            # Reduced to 1.0 second for practice scenarios (short clips, words, phrases)
            # Longer audio (5+ seconds) works better, but we support shorter clips
            min_duration = 1.0
            
            logger.info(f"Audio durations - Input: {input_duration:.2f}s, Reference: {reference_duration:.2f}s")
            
            # Analyze voice content in input audio
            input_audio_data, input_sr = librosa.load(input_file, sr=None)
            voice_segments = await self._analyze_voice_content(input_audio_data, input_sr)
            voice_duration = sum(end - start for start, end in voice_segments)
            
            logger.info(f"Voice analysis - Total duration: {input_duration:.2f}s, Voice content: {voice_duration:.2f}s")
            logger.info(f"Voice segments: {voice_segments}")
            logger.info(f"Voice content percentage: {(voice_duration/input_duration)*100:.1f}%")
            
            if input_duration < min_duration:
                raise ConversionError(
                    f"Input audio too short: {input_duration:.2f}s. "
                    f"Minimum required: {min_duration}s. "
                    f"Please record for at least {min_duration} seconds of continuous speech."
                )
            
            if voice_duration < 0.5:  # Require at least 0.5 seconds of actual voice content (reduced for practice)
                raise ConversionError(
                    f"Insufficient voice content: {voice_duration:.2f}s detected out of {input_duration:.2f}s total. "
                    f"Voice content percentage: {(voice_duration/input_duration)*100:.1f}%. "
                    f"Please speak clearly for at least 1 second. "
                    f"Try speaking louder or closer to the microphone."
                )
            
            # Reference audio can be shorter (minimum 0.5s) as it's just for voice characteristics
            if reference_duration < 0.5:
                raise ConversionError(
                    f"Reference audio too short: {reference_duration:.2f}s. "
                    f"Minimum required: 0.5s. "
                    f"Please use a reference audio that is at least 0.5 seconds long."
                )
            
            logger.info(f"Audio validation passed - Input: {input_duration:.2f}s (voice: {voice_duration:.2f}s), Reference: {reference_duration:.2f}s")
            
        except ImportError:
            # If librosa is not available, skip validation but log warning
            logger.warning("librosa not available for audio duration validation - trying wave module")
            # Try alternative method using wave module
            try:
                import wave
                with wave.open(input_file, 'r') as wav_file:
                    input_duration = wav_file.getnframes() / wav_file.getframerate()
                with wave.open(reference_file, 'r') as wav_file:
                    reference_duration = wav_file.getnframes() / wav_file.getframerate()
                
                min_duration = 1.0
                
                logger.info(f"Audio durations (wave) - Input: {input_duration:.2f}s, Reference: {reference_duration:.2f}s")
                
                if input_duration < min_duration:
                    raise ConversionError(
                        f"Input audio too short: {input_duration:.2f}s. "
                        f"Minimum required: {min_duration}s. "
                        f"Please record for at least {min_duration} seconds."
                    )
                
                if reference_duration < min_duration:
                    raise ConversionError(
                        f"Reference audio too short: {reference_duration:.2f}s. "
                        f"Minimum required: {min_duration}s. "
                        f"Please use a reference audio that is at least {min_duration} seconds long."
                    )
                
                logger.info(f"Audio validation passed (wave) - Input: {input_duration:.2f}s, Reference: {reference_duration:.2f}s")
                
            except Exception as e:
                logger.warning(f"Could not validate audio length: {e}")
        except Exception as e:
            logger.error(f"Error validating audio length: {str(e)}")
            raise ConversionError(f"Audio validation failed: {str(e)}")
    
    async def _analyze_voice_content(self, audio_data, sample_rate: int) -> list:
        """Analyze voice content in audio data using VAD-like approach"""
        try:
            import librosa
            
            # Use librosa's voice activity detection
            # Get spectral features for voice detection
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)[0]
            
            # Calculate frame times
            hop_length = 512
            frame_times = librosa.frames_to_time(range(len(spectral_centroids)), sr=sample_rate, hop_length=hop_length)
            
            # Simple voice activity detection based on energy and spectral features
            voice_threshold = 0.1  # Adjust based on testing
            voice_frames = []
            
            for i, (centroid, rolloff, zcr) in enumerate(zip(spectral_centroids, spectral_rolloff, zero_crossing_rate)):
                # Voice is detected if there's sufficient spectral energy and reasonable zero crossing rate
                if centroid > voice_threshold and zcr < 0.1:  # Low ZCR indicates voice
                    voice_frames.append(i)
            
            # Convert frame indices to time segments
            voice_segments = []
            if voice_frames:
                # Group consecutive voice frames
                start_frame = voice_frames[0]
                current_frame = voice_frames[0]
                
                for i in range(1, len(voice_frames)):
                    if voice_frames[i] - current_frame > 1:  # Gap in voice frames
                        # End current segment
                        end_time = frame_times[current_frame]
                        start_time = frame_times[start_frame]
                        if end_time - start_time > 0.1:  # Only include segments longer than 0.1s
                            voice_segments.append((start_time, end_time))
                        # Start new segment
                        start_frame = voice_frames[i]
                    current_frame = voice_frames[i]
                
                # Add final segment
                end_time = frame_times[current_frame]
                start_time = frame_times[start_frame]
                if end_time - start_time > 0.1:
                    voice_segments.append((start_time, end_time))
            
            logger.info(f"Voice analysis completed - Found {len(voice_segments)} voice segments")
            return voice_segments
            
        except Exception as e:
            logger.warning(f"Voice analysis failed: {e}")
            # Fallback: assume entire audio is voice content
            duration = len(audio_data) / sample_rate
            return [(0.0, duration)]
    
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
            
            # Validate audio length before conversion
            await self._validate_audio_length(input_file, reference_file)
            
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
            
            logger.info(f"Running OpenVoice conversion with:")
            logger.info(f"  Input: {input_file}")
            logger.info(f"  Reference: {reference_file}")
            logger.info(f"  Output: {output_file}")
            logger.info(f"  Device: {device}")
            
            # Run the conversion
            tune_one(
                input_file=input_file,
                ref_file=reference_file,
                output_file=output_file,
                device=device
            )
            
            logger.info("OpenVoice conversion completed successfully")
            
        except ImportError as e:
            error_msg = f"OpenVoice CLI import failed: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg)
        except FileNotFoundError as e:
            error_msg = f"Required file not found: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg)
        except Exception as e:
            error_msg = f"OpenVoice conversion error: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            raise ConversionError(error_msg)
    
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
