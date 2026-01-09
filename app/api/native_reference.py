"""
Native reference audio generation endpoints
"""

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

from app.services.native_reference_generator import NativeReferenceGenerator
from app.core.config import settings

router = APIRouter()
generator = NativeReferenceGenerator()


@router.post("/generate-native-reference")
async def generate_native_reference(
    sentence: str = Form(..., description="Sentence to generate native reference for"),
    accent: str = Form(..., description="Target accent (e.g., 'neutral-na', 'rp-british')"),
    language: str = Form("en", description="Language code")
):
    """
    Generate native reference audio for a sentence using TTS
    
    This creates perfect native pronunciation that can be used with OpenVoice
    to generate "user voice + perfect accent" audio.
    """
    try:
        # Generate native reference file
        output_file = await generator.generate_native_reference_file(
            sentence=sentence,
            accent=accent,
            language=language
        )
        
        return FileResponse(
            output_file,
            media_type="audio/wav",
            filename=f"native_reference_{accent}.wav",
            background=lambda: os.unlink(output_file)  # Cleanup after sending
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

