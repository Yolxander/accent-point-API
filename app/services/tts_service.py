"""
Text-to-Speech service for generating speech from text
"""

import logging
import asyncio
from typing import Tuple
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from app.core.exceptions import ConversionError

logger = logging.getLogger(__name__)


class TTSService:
    """Service for text-to-speech generation"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._gtts_available = None
        self._pyttsx3_available = None
    
    async def _check_gtts_availability(self) -> bool:
        """Check if Google TTS is available"""
        if self._gtts_available is not None:
            return self._gtts_available
        
        try:
            from gtts import gTTS
            self._gtts_available = True
            logger.info("Google TTS is available")
            return True
        except ImportError:
            logger.warning("Google TTS not available")
            self._gtts_available = False
            return False
    
    async def _check_pyttsx3_availability(self) -> bool:
        """Check if pyttsx3 is available"""
        if self._pyttsx3_available is not None:
            return self._pyttsx3_available
        
        try:
            import pyttsx3
            self._pyttsx3_available = True
            logger.info("pyttsx3 is available")
            return True
        except ImportError:
            logger.warning("pyttsx3 not available")
            self._pyttsx3_available = False
            return False
    
    async def generate_speech(self, text: str, speed: float = 1.0, 
                            pitch: float = 1.0, language: str = "en") -> Tuple[np.ndarray, int]:
        """
        Generate speech from text
        
        Args:
            text: Text to convert to speech
            speed: Speech speed multiplier (0.5-2.0)
            pitch: Speech pitch multiplier (0.5-2.0)
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            # Try Google TTS first
            if await self._check_gtts_availability():
                return await self._generate_with_gtts(text, speed, pitch, language)
            
            # Fallback to pyttsx3
            elif await self._check_pyttsx3_availability():
                return await self._generate_with_pyttsx3(text, speed, pitch)
            
            else:
                raise ConversionError("No TTS engine available. Please install gtts or pyttsx3")
                
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            raise ConversionError(f"TTS generation failed: {str(e)}")
    
    async def _generate_with_gtts(self, text: str, speed: float, 
                                pitch: float, language: str) -> Tuple[np.ndarray, int]:
        """Generate speech using Google TTS"""
        try:
            # Run in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._gtts_generate_sync,
                text, speed, pitch, language
            )
            return result
            
        except Exception as e:
            logger.error(f"Google TTS generation failed: {str(e)}")
            raise ConversionError(f"Google TTS generation failed: {str(e)}")
    
    def _gtts_generate_sync(self, text: str, speed: float, 
                          pitch: float, language: str) -> Tuple[np.ndarray, int]:
        """Synchronous Google TTS generation"""
        from gtts import gTTS
        import io
        import librosa
        
        # Create TTS object
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Generate audio to bytes
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        # Load audio with librosa
        audio_data, sample_rate = librosa.load(audio_io, sr=None)
        
        # Apply speed and pitch modifications
        if speed != 1.0:
            audio_data = librosa.effects.time_stretch(audio_data, rate=speed)
        
        if pitch != 1.0:
            # Pitch shifting using librosa
            audio_data = librosa.effects.pitch_shift(audio_data, sr=sample_rate, n_steps=12 * np.log2(pitch))
        
        return audio_data, sample_rate
    
    async def _generate_with_pyttsx3(self, text: str, speed: float, 
                                   pitch: float) -> Tuple[np.ndarray, int]:
        """Generate speech using pyttsx3"""
        try:
            # Run in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._pyttsx3_generate_sync,
                text, speed, pitch
            )
            return result
            
        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {str(e)}")
            raise ConversionError(f"pyttsx3 generation failed: {str(e)}")
    
    def _pyttsx3_generate_sync(self, text: str, speed: float, 
                             pitch: float) -> Tuple[np.ndarray, int]:
        """Synchronous pyttsx3 generation"""
        import pyttsx3
        import io
        import librosa
        import tempfile
        import os
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Set properties
        engine.setProperty('rate', int(200 * speed))  # Base rate is 200
        engine.setProperty('volume', 0.9)
        
        # Get available voices
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        # Generate audio to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save to temporary file
            engine.save_to_file(text, temp_path)
            engine.runAndWait()
            
            # Load audio with librosa
            audio_data, sample_rate = librosa.load(temp_path, sr=None)
            
            # Apply pitch modification
            if pitch != 1.0:
                audio_data = librosa.effects.pitch_shift(audio_data, sr=sample_rate, n_steps=12 * np.log2(pitch))
            
            return audio_data, sample_rate
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def get_available_voices(self) -> list:
        """Get list of available voices"""
        voices = []
        
        try:
            if await self._check_pyttsx3_availability():
                import pyttsx3
                engine = pyttsx3.init()
                pyttsx3_voices = engine.getProperty('voices')
                
                for voice in pyttsx3_voices:
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'languages': voice.languages,
                        'engine': 'pyttsx3'
                    })
                
                engine.stop()
        except Exception as e:
            logger.warning(f"Failed to get pyttsx3 voices: {str(e)}")
        
        # Add Google TTS languages
        if await self._check_gtts_availability():
            gtts_languages = [
                'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar'
            ]
            for lang in gtts_languages:
                voices.append({
                    'id': f'gtts_{lang}',
                    'name': f'Google TTS {lang.upper()}',
                    'languages': [lang],
                    'engine': 'gtts'
                })
        
        return voices
    
    def __del__(self):
        """Cleanup executor on destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
