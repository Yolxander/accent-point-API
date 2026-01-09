"""
Native reference audio generator using TTS
"""

import logging
import tempfile
import os
from typing import Optional, Tuple
import numpy as np

from app.services.tts_service import TTSService
from app.services.audio_processor import AudioProcessor
from app.core.config import settings

logger = logging.getLogger(__name__)


class NativeReferenceGenerator:
    """Generate native reference audio for sentences using TTS"""
    
    def __init__(self):
        self.tts_service = TTSService()
        self.audio_processor = AudioProcessor()
        # Cache for generated references (optional, for performance)
        self._cache = {}
    
    async def generate_native_reference(
        self,
        sentence: str,
        accent: str,
        language: str = "en"
    ) -> Tuple[np.ndarray, int]:
        """
        Generate native reference audio for a sentence using TTS
        
        Args:
            sentence: The sentence to generate reference for
            accent: Target accent (e.g., 'neutral-na', 'rp-british')
            language: Language code (default: 'en')
            
        Returns:
            Tuple of (audio_data, sample_rate) with perfect native pronunciation
        """
        try:
            # Map accent to TTS language variant
            # Google TTS supports different accents via language codes
            tts_language = self._map_accent_to_language(accent, language)
            
            logger.info(f"Generating native reference for: '{sentence}' (accent: {accent})")
            
            # Generate TTS with native pronunciation
            # This produces perfect native accent automatically
            audio_data, sample_rate = await self.tts_service.generate_speech(
                text=sentence,
                speed=1.0,  # Natural speed
                pitch=1.0,  # Natural pitch
                language=tts_language
            )
            
            # Normalize audio
            audio_data = self.audio_processor.normalize_audio(audio_data)
            
            # Resample to target sample rate
            target_sr = settings.TARGET_SAMPLE_RATE
            if sample_rate != target_sr:
                audio_data = self.audio_processor.resample_audio(
                    audio_data, sample_rate, target_sr
                )
                sample_rate = target_sr
            
            # Check if audio is long enough for OpenVoice
            # OpenVoice requires at least 5 seconds of voice content after VAD
            # Since VAD typically reduces audio by 30-40%, we need at least 7-8 seconds of actual speech
            current_duration = len(audio_data) / sample_rate
            
            # If the generated audio is too short, repeat it to create more voice content
            # This is better than padding with silence since VAD will remove silence anyway
            min_voice_duration = 7.0  # Minimum voice content needed (before VAD)
            if current_duration < min_voice_duration:
                # Repeat the audio to reach minimum length
                repeats_needed = int(min_voice_duration / current_duration) + 1
                repeated_audio = np.tile(audio_data, repeats_needed)
                # Trim to exactly min_voice_duration
                target_samples = int(min_voice_duration * sample_rate)
                audio_data = repeated_audio[:target_samples]
                logger.info(f"Repeated audio {repeats_needed}x times: {current_duration:.2f}s -> {len(audio_data)/sample_rate:.2f}s")
            else:
                logger.info(f"Native reference generated: {current_duration:.2f}s (sufficient length)")
            
            return audio_data, sample_rate
            
        except Exception as e:
            logger.error(f"Failed to generate native reference: {e}")
            raise
    
    async def generate_native_reference_file(
        self,
        sentence: str,
        accent: str,
        output_file: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """
        Generate native reference audio and save to file
        
        Args:
            sentence: The sentence to generate reference for
            accent: Target accent
            output_file: Optional output file path (creates temp file if not provided)
            language: Language code
            
        Returns:
            Path to generated audio file
        """
        try:
            # Generate audio
            audio_data, sample_rate = await self.generate_native_reference(
                sentence, accent, language
            )
            
            # Create output file if not provided
            if not output_file:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=".wav",
                    delete=False,
                    dir=settings.TEMP_DIR
                )
                output_file = temp_file.name
                temp_file.close()
            
            # Save audio
            self.audio_processor.save_audio(output_file, audio_data, sample_rate)
            
            logger.info(f"Native reference saved to: {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Failed to generate native reference file: {e}")
            raise
    
    def _map_accent_to_language(self, accent: str, base_language: str = "en") -> str:
        """
        Map accent name to TTS language code
        
        Google TTS supports regional variants:
        - en-US (American English)
        - en-GB (British English)
        - en-AU (Australian English)
        - en-IN (Indian English)
        - en-CA (Canadian English)
        etc.
        """
        accent_map = {
            'neutral-na': 'en-US',      # American English
            'rp-british': 'en-GB',      # British English
            'australian': 'en-AU',      # Australian English
            'canadian': 'en-CA',        # Canadian English
            'indian': 'en-IN',          # Indian English
            'moscow-standard': 'ru',    # Russian
            # Add more mappings as needed
        }
        
        return accent_map.get(accent.lower(), base_language)

