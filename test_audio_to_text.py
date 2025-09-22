#!/usr/bin/env python3
"""
Test script for the audio-to-text functionality
"""

import os
import sys

def test_audio_files():
    """Test if audio files are accessible"""
    processed_dir = "processed"
    audio_files = []
    
    if not os.path.exists(processed_dir):
        print("❌ Processed directory not found")
        return False
    
    for folder in os.listdir(processed_dir):
        folder_path = os.path.join(processed_dir, folder)
        if os.path.isdir(folder_path):
            wavs_dir = os.path.join(folder_path, "wavs")
            if os.path.exists(wavs_dir):
                for file in os.listdir(wavs_dir):
                    if file.endswith('.wav'):
                        audio_files.append({
                            'name': file,
                            'path': os.path.join(wavs_dir, file),
                            'folder': folder
                        })
    
    print(f"✅ Found {len(audio_files)} audio files")
    
    if audio_files:
        print("📁 Available audio files:")
        for i, file in enumerate(audio_files[:5]):  # Show first 5
            print(f"   {i+1}. {file['folder']}/{file['name']}")
        if len(audio_files) > 5:
            print(f"   ... and {len(audio_files) - 5} more")
    
    return len(audio_files) > 0

def test_imports():
    """Test if required modules can be imported"""
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import soundfile as sf
        print("✅ SoundFile imported successfully")
    except ImportError as e:
        print(f"❌ SoundFile import failed: {e}")
        return False
    
    try:
        import whisper
        print("✅ Whisper imported successfully")
    except ImportError as e:
        print(f"⚠️ Whisper import failed: {e}")
        print("   Install with: pip install openai-whisper")
        return False
    
    return True

def main():
    print("🧪 Testing Audio-to-Text Setup")
    print("=" * 40)
    
    # Test imports
    print("\n📦 Testing imports...")
    imports_ok = test_imports()
    
    # Test audio files
    print("\n📁 Testing audio files...")
    audio_ok = test_audio_files()
    
    print("\n" + "=" * 40)
    if imports_ok and audio_ok:
        print("✅ All tests passed! Audio-to-text app should work.")
        print("\n🚀 To run the app:")
        print("   streamlit run app_audio_to_text.py")
        print("   or")
        print("   ./run_suite.sh")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        if not imports_ok:
            print("   Install missing dependencies first.")
        if not audio_ok:
            print("   Make sure you have processed audio files.")

if __name__ == "__main__":
    main()
