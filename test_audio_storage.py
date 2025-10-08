#!/usr/bin/env python3
"""
Test script to verify audio storage in database functionality
"""

import asyncio
import os
import sys
import tempfile
import wave
import numpy as np

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.database_service import db_service
from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_test_audio():
    """Create a simple test audio file"""
    # Generate a simple sine wave
    sample_rate = 22050
    duration = 2.0  # 2 seconds
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convert to 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Create temporary WAV file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        with wave.open(temp_file.name, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        # Read the file as bytes
        with open(temp_file.name, 'rb') as f:
            audio_bytes = f.read()
        
        # Clean up
        os.unlink(temp_file.name)
    
    return audio_bytes, sample_rate


async def test_voice_conversion_storage():
    """Test voice conversion audio storage"""
    print("Testing voice conversion audio storage...")
    
    try:
        # Create test audio
        audio_data, sample_rate = await create_test_audio()
        print(f"Created test audio: {len(audio_data)} bytes, {sample_rate} Hz")
        
        # Create a test conversion record
        conversion = await db_service.create_voice_conversion(
            user_id=None,
            session_id="test_session",
            transformation_type="voice_conversion",
            source_audio_filename="test_input.wav",
            source_audio_size=len(audio_data),
            reference_audio_filename="test_ref.wav",
            reference_audio_size=len(audio_data)
        )
        
        conversion_id = conversion['id']
        print(f"Created conversion record: {conversion_id}")
        
        # Save audio to conversion
        await db_service.save_audio_to_conversion(
            conversion_id,
            audio_data,
            "test_output.wav",
            len(audio_data),
            2.0
        )
        print("Saved audio data to conversion")
        
        # Retrieve audio from conversion
        retrieved_audio = await db_service.get_audio_from_conversion(conversion_id)
        
        if retrieved_audio and retrieved_audio == audio_data:
            print("✅ Audio storage and retrieval successful!")
            return True
        else:
            print("❌ Audio retrieval failed or data mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


async def test_tts_conversion_storage():
    """Test text-to-speech conversion audio storage"""
    print("\nTesting TTS conversion audio storage...")
    
    try:
        # Create test audio
        audio_data, sample_rate = await create_test_audio()
        print(f"Created test audio: {len(audio_data)} bytes, {sample_rate} Hz")
        
        # Create a test TTS conversion record
        conversion = await db_service.create_text_to_speech_conversion(
            text_content="Hello, this is a test.",
            user_id=None,
            session_id="test_tts_session",
            text_length=25,
            language="en"
        )
        
        conversion_id = conversion['id']
        print(f"Created TTS conversion record: {conversion_id}")
        
        # Save audio to TTS conversion
        await db_service.save_audio_to_tts_conversion(
            conversion_id,
            audio_data,
            "test_tts_output.wav",
            len(audio_data),
            2.0
        )
        print("Saved audio data to TTS conversion")
        
        # Retrieve audio from TTS conversion
        retrieved_audio = await db_service.get_audio_from_tts_conversion(conversion_id)
        
        if retrieved_audio and retrieved_audio == audio_data:
            print("✅ TTS audio storage and retrieval successful!")
            return True
        else:
            print("❌ TTS audio retrieval failed or data mismatch")
            return False
            
    except Exception as e:
        print(f"❌ TTS test failed with error: {e}")
        return False


async def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        result = await db_service.test_connection()
        if result:
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("Starting audio storage tests...\n")
    
    # Test database connection first
    if not await test_database_connection():
        print("\n❌ Cannot proceed without database connection")
        return
    
    # Run tests
    voice_test_passed = await test_voice_conversion_storage()
    tts_test_passed = await test_tts_conversion_storage()
    
    print(f"\n{'='*50}")
    print("Test Results:")
    print(f"Voice Conversion Storage: {'✅ PASSED' if voice_test_passed else '❌ FAILED'}")
    print(f"TTS Conversion Storage: {'✅ PASSED' if tts_test_passed else '❌ FAILED'}")
    
    if voice_test_passed and tts_test_passed:
        print("\n🎉 All tests passed! Audio storage in database is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    asyncio.run(main())
