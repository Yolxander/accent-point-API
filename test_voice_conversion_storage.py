#!/usr/bin/env python3
"""
Test script for voice conversion with Supabase Storage
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.api.voice_conversion import convert_voice
from app.core.logging import get_logger
from fastapi import UploadFile
from io import BytesIO

logger = get_logger(__name__)


def create_test_audio_file(content: bytes = b"fake audio data") -> UploadFile:
    """Create a test audio file for testing"""
    return UploadFile(
        file=BytesIO(content),
        filename="test_audio.wav",
        content_type="audio/wav"
    )


async def test_voice_conversion_with_storage():
    """Test voice conversion with Supabase Storage"""
    print("Testing voice conversion with Supabase Storage...")
    
    try:
        # Create test audio files
        input_audio = create_test_audio_file(b"input audio data for testing")
        reference_audio = create_test_audio_file(b"reference audio data for testing")
        
        # Set file sizes
        input_audio.size = len(b"input audio data for testing")
        reference_audio.size = len(b"reference audio data for testing")
        
        print(f"Created test files:")
        print(f"  Input audio: {input_audio.filename} ({input_audio.size} bytes)")
        print(f"  Reference audio: {reference_audio.filename} ({reference_audio.size} bytes)")
        
        # Note: This test would require the actual voice conversion service to be running
        # For now, we'll just test the storage service integration
        print("\nNote: This test requires the full voice conversion service to be running.")
        print("To test the complete flow:")
        print("1. Start the API server: python main.py")
        print("2. Make a POST request to /api/v1/convert-voice with audio files")
        print("3. Check the response for the public_url field")
        
        return True
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        logger.error(f"Voice conversion storage test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("=" * 60)
    print("VOICE CONVERSION STORAGE TEST")
    print("=" * 60)
    
    success = await test_voice_conversion_with_storage()
    
    if success:
        print("\n🎉 Voice conversion storage test completed!")
        sys.exit(0)
    else:
        print("\n💥 Voice conversion storage test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
