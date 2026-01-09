"""
Assessment analysis endpoints
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.pronunciation_analyzer import PronunciationAnalyzer, AssessmentAnalysis
from app.core.exceptions import AudioProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service lazily (only when needed)
_pronunciation_analyzer: Optional[PronunciationAnalyzer] = None

def get_pronunciation_analyzer() -> PronunciationAnalyzer:
    """Get or create pronunciation analyzer instance (lazy initialization)"""
    global _pronunciation_analyzer
    if _pronunciation_analyzer is None:
        _pronunciation_analyzer = PronunciationAnalyzer()
    return _pronunciation_analyzer


class AssessmentRequest(BaseModel):
    """Request model for assessment analysis"""
    audio_url: str
    text: str
    target_accent: str


class PhonemeDetail(BaseModel):
    """Phoneme detail with timing and score"""
    phoneme: str
    start_time: float
    end_time: float
    score: float
    issue: Optional[str] = None


class WordTimestamp(BaseModel):
    """Word timestamp with score"""
    word: str
    start_time: float
    end_time: float
    score: float


class ProblemAreaResponse(BaseModel):
    """Problem area response"""
    sound: str
    score: float
    difficulty: str
    phonemes: list[PhonemeDetail]


class AssessmentResponse(BaseModel):
    """Assessment analysis response"""
    overall_score: float
    level: str
    problem_areas: list[ProblemAreaResponse]
    word_timestamps: list[WordTimestamp]
    focus_sounds_order: list[str]
    strengths: list[str]


@router.post("/analyze-assessment", response_model=AssessmentResponse)
async def analyze_assessment(request: AssessmentRequest):
    """
    Analyze pronunciation assessment using Wav2Vec2 and MFA
    
    - **audio_url**: URL to the user's recorded audio
    - **text**: The text that was read (paragraph)
    - **target_accent**: Target accent for comparison (e.g., 'neutral-na', 'rp-british')
    
    Returns detailed analysis with:
    - Overall score and level
    - Problem areas with phoneme-level details
    - Word timestamps with scores
    - Recommended focus sounds order
    - Identified strengths
    """
    try:
        logger.info(f"Assessment analysis request: accent={request.target_accent}, text_length={len(request.text)}")
        
        # Analyze pronunciation (lazy load analyzer)
        analyzer = get_pronunciation_analyzer()
        analysis: AssessmentAnalysis = await analyzer.analyze_assessment(
            audio_url=request.audio_url,
            text=request.text,
            target_accent=request.target_accent
        )
        
        # Convert to response format
        problem_areas_response = [
            ProblemAreaResponse(
                sound=pa.sound,
                score=pa.score,
                difficulty=pa.difficulty,
                phonemes=[
                    PhonemeDetail(
                        phoneme=p.phoneme,
                        start_time=p.start_time,
                        end_time=p.end_time,
                        score=p.score,
                        issue=p.issue
                    )
                    for p in pa.phonemes
                ]
            )
            for pa in analysis.problem_areas
        ]
        
        word_timestamps_response = [
            WordTimestamp(
                word=ws.word,
                start_time=ws.start_time,
                end_time=ws.end_time,
                score=ws.score
            )
            for ws in analysis.word_timestamps
        ]
        
        return AssessmentResponse(
            overall_score=analysis.overall_score,
            level=analysis.level,
            problem_areas=problem_areas_response,
            word_timestamps=word_timestamps_response,
            focus_sounds_order=analysis.focus_sounds_order,
            strengths=analysis.strengths
        )
        
    except AudioProcessingError as e:
        logger.error(f"Audio processing error: {e}")
        raise HTTPException(status_code=400, detail=f"Audio processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Assessment analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment analysis failed: {str(e)}")

