"""
Pronunciation analysis service using Wav2Vec2 XLSR-53 and Montreal Forced Aligner
"""

import logging
import tempfile
import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import torch
import torchaudio
# Lazy import transformers to avoid import errors at startup
# from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from scipy.spatial.distance import cosine
import requests

from app.services.audio_processor import AudioProcessor
from app.services.native_reference_generator import NativeReferenceGenerator
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PhonemeSegment:
    """Phoneme segment with timing and score"""
    phoneme: str
    start_time: float
    end_time: float
    score: float
    issue: Optional[str] = None


@dataclass
class WordSegment:
    """Word segment with timing and score"""
    word: str
    start_time: float
    end_time: float
    score: float
    phonemes: List[PhonemeSegment]


@dataclass
class ProblemArea:
    """Problem area (sound category) with aggregated scores"""
    sound: str
    score: float
    difficulty: str  # 'high' | 'medium' | 'low'
    phonemes: List[PhonemeSegment]


@dataclass
class AssessmentAnalysis:
    """Complete assessment analysis result"""
    overall_score: float
    level: str  # 'starter' | 'intermediate' | 'advanced'
    problem_areas: List[ProblemArea]
    word_timestamps: List[WordSegment]
    focus_sounds_order: List[str]
    strengths: List[str]


class PronunciationAnalyzer:
    """Analyze pronunciation using Wav2Vec2 and MFA"""
    
    # Phoneme to sound category mapping
    PHONEME_TO_SOUND: Dict[str, str] = {
        # R sounds
        'ɹ': 'R', 'r': 'R', 'ɚ': 'R', 'ɝ': 'R',
        # TH sounds
        'θ': 'th', 'ð': 'th',
        # Vowels
        'i': 'vowels', 'ɪ': 'vowels', 'e': 'vowels', 'ɛ': 'vowels',
        'æ': 'vowels', 'ɑ': 'vowels', 'ɔ': 'vowels', 'o': 'vowels',
        'ʊ': 'vowels', 'u': 'vowels', 'ʌ': 'vowels', 'ə': 'vowels',
        'aɪ': 'vowels', 'aʊ': 'vowels', 'ɔɪ': 'vowels',
        'eɪ': 'vowels', 'oʊ': 'vowels',
        # L sounds
        'l': 'L', 'ɫ': 'L',
        # W sounds
        'w': 'W',
        # V sounds
        'v': 'V',
        # Other common problem sounds
        'z': 'Z', 's': 'S', 'ʃ': 'S', 'ʒ': 'S',
    }
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.native_reference_generator = NativeReferenceGenerator()
        
        # Initialize Wav2Vec2 model (lazy loading)
        self._processor = None
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"PronunciationAnalyzer initialized (device: {self._device})")
    
    def _load_model(self):
        """Lazy load Wav2Vec2 model"""
        if self._model is None:
            # Lazy import transformers to avoid import errors at startup
            try:
                from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
            except ImportError as e:
                logger.error(f"Failed to import transformers: {e}")
                raise ImportError("transformers library is required for pronunciation analysis. Install with: pip install transformers")
            
            logger.info("Loading Wav2Vec2 XLSR-53 model...")
            model_name = "facebook/wav2vec2-xlsr-53"
            self._processor = Wav2Vec2Processor.from_pretrained(model_name)
            self._model = Wav2Vec2ForCTC.from_pretrained(model_name)
            self._model.to(self._device)
            self._model.eval()
            logger.info("Wav2Vec2 model loaded")
    
    async def _forced_align_simple(
        self,
        audio_path: str,
        text: str
    ) -> List[WordSegment]:
        """
        Simple forced alignment using word-level segmentation
        This is a simplified version - full MFA would require model downloads
        For now, we'll use a heuristic approach based on audio duration
        """
        try:
            # Load audio to get duration
            audio_data, sample_rate = await self.audio_processor.load_audio_from_file(audio_path)
            duration = len(audio_data) / sample_rate
            
            # Simple word-level segmentation
            words = text.lower().split()
            num_words = len(words)
            
            if num_words == 0:
                return []
            
            # Estimate word boundaries (simple heuristic)
            time_per_word = duration / num_words
            word_segments = []
            
            current_time = 0.0
            for i, word in enumerate(words):
                # Add some variation to word boundaries
                word_duration = time_per_word * (0.8 + np.random.random() * 0.4)
                word_segments.append(WordSegment(
                    word=word,
                    start_time=current_time,
                    end_time=current_time + word_duration,
                    score=0.0,  # Will be calculated later
                    phonemes=[]  # Will be populated with phoneme analysis
                ))
                current_time += word_duration
            
            return word_segments
            
        except Exception as e:
            logger.error(f"Forced alignment error: {e}")
            raise
    
    async def _get_embeddings(
        self,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> np.ndarray:
        """Extract embeddings from audio using Wav2Vec2"""
        try:
            self._load_model()
            
            # Resample to 16kHz if needed (Wav2Vec2 requirement)
            if sample_rate != 16000:
                audio_data = self.audio_processor.resample_audio(
                    audio_data, sample_rate, 16000
                )
                sample_rate = 16000
            
            # Convert to tensor
            audio_tensor = torch.from_numpy(audio_data).float()
            
            # Process audio
            inputs = self._processor(
                audio_tensor,
                sampling_rate=sample_rate,
                return_tensors="pt",
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Get embeddings (before CTC head)
            with torch.no_grad():
                outputs = self._model.wav2vec2(**inputs)
                # Use the last hidden state as embeddings
                embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
            
            return embeddings[0]  # Return first (and only) batch item
            
        except Exception as e:
            logger.error(f"Embedding extraction error: {e}")
            raise
    
    async def _score_segment(
        self,
        user_embedding: np.ndarray,
        reference_embedding: np.ndarray
    ) -> float:
        """Score pronunciation segment using cosine similarity"""
        try:
            # Calculate cosine similarity (1 - cosine distance)
            similarity = 1 - cosine(user_embedding, reference_embedding)
            # Convert to 0-100 score
            score = max(0, min(100, (similarity + 1) * 50))
            return score
        except Exception as e:
            logger.error(f"Scoring error: {e}")
            return 50.0  # Default score
    
    async def _identify_phonemes(
        self,
        word: str
    ) -> List[str]:
        """
        Simple phoneme identification from word
        This is a placeholder - full implementation would use phonemizer
        """
        # Basic phoneme mapping (simplified)
        phoneme_map = {
            'r': ['ɹ'],
            'th': ['θ'],
            'the': ['ð'],
            'l': ['l'],
            'w': ['w'],
            'v': ['v'],
            'a': ['æ'],
            'e': ['ɛ'],
            'i': ['ɪ'],
            'o': ['ɔ'],
            'u': ['ʌ'],
        }
        
        phonemes = []
        word_lower = word.lower()
        
        # Simple heuristic: check for common phonemes
        for char in word_lower:
            if char in phoneme_map:
                phonemes.extend(phoneme_map[char])
        
        # If no phonemes found, return generic vowel
        if not phonemes:
            phonemes = ['ə']  # Schwa as default
        
        return phonemes
    
    async def analyze_assessment(
        self,
        audio_url: str,
        text: str,
        target_accent: str
    ) -> AssessmentAnalysis:
        """
        Analyze pronunciation assessment
        
        Args:
            audio_url: URL to user's recorded audio
            text: The text that was read
            target_accent: Target accent for comparison
            
        Returns:
            AssessmentAnalysis with scores, problem areas, and timestamps
        """
        try:
            logger.info(f"Analyzing assessment: {text[:50]}... (accent: {target_accent})")
            
            # Download user audio
            response = requests.get(audio_url, timeout=30)
            response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(response.content)
                user_audio_path = temp_file.name
            
            try:
                # Load user audio
                user_audio, user_sr = await self.audio_processor.load_audio_from_file(user_audio_path)
                
                # Generate native reference audio
                logger.info("Generating native reference audio...")
                ref_audio, ref_sr = await self.native_reference_generator.generate_native_reference(
                    text, target_accent
                )
                
                # Get embeddings for full audio
                logger.info("Extracting embeddings...")
                user_embedding = await self._get_embeddings(user_audio, user_sr)
                ref_embedding = await self._get_embeddings(ref_audio, ref_sr)
                
                # Calculate overall score
                overall_score = await self._score_segment(user_embedding, ref_embedding)
                
                # Forced alignment
                logger.info("Performing forced alignment...")
                word_segments = await self._forced_align_simple(user_audio_path, text)
                
                # Analyze each word segment
                problem_areas_dict: Dict[str, List[PhonemeSegment]] = {}
                
                for word_seg in word_segments:
                    # Extract word audio segment
                    start_sample = int(word_seg.start_time * user_sr)
                    end_sample = int(word_seg.end_time * user_sr)
                    word_audio = user_audio[start_sample:end_sample]
                    
                    # Get word reference segment
                    ref_start_sample = int(word_seg.start_time * ref_sr)
                    ref_end_sample = int(word_seg.end_time * ref_sr)
                    ref_word_audio = ref_audio[ref_start_sample:ref_end_sample]
                    
                    # Score word
                    if len(word_audio) > 0 and len(ref_word_audio) > 0:
                        word_emb = await self._get_embeddings(word_audio, user_sr)
                        ref_word_emb = await self._get_embeddings(ref_word_audio, ref_sr)
                        word_score = await self._score_segment(word_emb, ref_word_emb)
                        word_seg.score = word_score
                        
                        # Identify phonemes in word
                        phonemes = await self._identify_phonemes(word_seg.word)
                        
                        # Create phoneme segments
                        phoneme_duration = (word_seg.end_time - word_seg.start_time) / len(phonemes)
                        for i, phoneme in enumerate(phonemes):
                            phoneme_start = word_seg.start_time + i * phoneme_duration
                            phoneme_end = phoneme_start + phoneme_duration
                            
                            # Map phoneme to sound category
                            sound_category = self.PHONEME_TO_SOUND.get(phoneme, 'other')
                            
                            # Create phoneme segment
                            phoneme_seg = PhonemeSegment(
                                phoneme=phoneme,
                                start_time=phoneme_start,
                                end_time=phoneme_end,
                                score=word_score,  # Use word score as approximation
                                issue=f"/{phoneme}/ score: {word_score:.1f}" if word_score < 60 else None
                            )
                            
                            word_seg.phonemes.append(phoneme_seg)
                            
                            # Add to problem areas
                            if sound_category not in problem_areas_dict:
                                problem_areas_dict[sound_category] = []
                            problem_areas_dict[sound_category].append(phoneme_seg)
                
                # Aggregate problem areas
                problem_areas = []
                for sound, phonemes in problem_areas_dict.items():
                    avg_score = np.mean([p.score for p in phonemes])
                    difficulty = 'high' if avg_score < 40 else 'medium' if avg_score < 60 else 'low'
                    
                    problem_areas.append(ProblemArea(
                        sound=sound,
                        score=float(avg_score),
                        difficulty=difficulty,
                        phonemes=phonemes
                    ))
                
                # Sort by score (worst first)
                problem_areas.sort(key=lambda x: x.score)
                
                # Determine level
                level = 'starter' if overall_score < 50 else 'intermediate' if overall_score < 75 else 'advanced'
                
                # Generate focus sounds order (worst sounds first)
                focus_sounds_order = [pa.sound for pa in problem_areas[:6]]
                
                # Generate strengths
                strengths = []
                if overall_score >= 60:
                    strengths.append('Good overall pronunciation clarity')
                if len(problem_areas) <= 2:
                    strengths.append('Few problem areas identified')
                if not strengths:
                    strengths.append('Ready to begin structured practice')
                
                return AssessmentAnalysis(
                    overall_score=float(overall_score),
                    level=level,
                    problem_areas=problem_areas,
                    word_timestamps=word_segments,
                    focus_sounds_order=focus_sounds_order,
                    strengths=strengths
                )
                
            finally:
                # Cleanup temp file
                if os.path.exists(user_audio_path):
                    os.unlink(user_audio_path)
                    
        except Exception as e:
            logger.error(f"Assessment analysis error: {e}")
            raise

