#!/usr/bin/env python3
"""
Test script for the 3-page OpenVoice AI Suite
"""

import os
import sys

def test_files_exist():
    """Test if all required files exist"""
    required_files = [
        'app_3pages.py',
        'app_text_to_speech.py',
        'app_audio_to_text.py',
        'app.py',
        'run_3pages.sh'
    ]
    
    print("📁 Testing file existence...")
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test if required modules can be imported"""
    print("\n📦 Testing imports...")
    
    try:
        import streamlit as st
        print("   ✅ Streamlit")
    except ImportError as e:
        print(f"   ❌ Streamlit: {e}")
        return False
    
    try:
        import soundfile as sf
        print("   ✅ SoundFile")
    except ImportError as e:
        print(f"   ❌ SoundFile: {e}")
        return False
    
    try:
        import whisper
        print("   ✅ Whisper")
    except ImportError as e:
        print(f"   ⚠️ Whisper: {e} (Audio to Text will not work)")
    
    try:
        import torch
        import torchaudio
        print("   ✅ PyTorch + TorchAudio")
    except ImportError as e:
        print(f"   ⚠️ PyTorch: {e} (Text to Speech will not work)")
    
    return True

def test_audio_files():
    """Test if audio files are available"""
    print("\n📁 Testing audio files...")
    
    processed_dir = "processed"
    if not os.path.exists(processed_dir):
        print("   ❌ No processed directory found")
        return False
    
    audio_count = 0
    for folder in os.listdir(processed_dir):
        folder_path = os.path.join(processed_dir, folder)
        if os.path.isdir(folder_path):
            wavs_dir = os.path.join(folder_path, "wavs")
            if os.path.exists(wavs_dir):
                audio_count += len([f for f in os.listdir(wavs_dir) if f.endswith('.wav')])
    
    print(f"   ✅ Found {audio_count} audio files")
    return audio_count > 0

def test_syntax():
    """Test if Python files have valid syntax"""
    print("\n🔍 Testing syntax...")
    
    python_files = [
        'app_3pages.py',
        'app_text_to_speech.py',
        'app_audio_to_text.py'
    ]
    
    all_valid = True
    
    for file in python_files:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"   ✅ {file}")
        except SyntaxError as e:
            print(f"   ❌ {file}: {e}")
            all_valid = False
        except Exception as e:
            print(f"   ⚠️ {file}: {e}")
    
    return all_valid

def main():
    print("🧪 Testing 3-Page OpenVoice AI Suite")
    print("=" * 50)
    
    # Test files
    files_ok = test_files_exist()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test audio files
    audio_ok = test_audio_files()
    
    # Test syntax
    syntax_ok = test_syntax()
    
    print("\n" + "=" * 50)
    
    if files_ok and imports_ok and audio_ok and syntax_ok:
        print("✅ All tests passed! 3-page system should work.")
        print("\n🚀 To run the system:")
        print("   ./run_3pages.sh")
        print("\n📖 Available pages:")
        print("   - Main Menu: http://localhost:8501")
        print("   - Voice Conversion: http://localhost:8501/?page=voice_conversion")
        print("   - Text to Speech: http://localhost:8501/?page=text_to_speech")
        print("   - Audio to Text: http://localhost:8501/?page=audio_to_text")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        if not files_ok:
            print("   Missing required files.")
        if not imports_ok:
            print("   Install missing dependencies.")
        if not audio_ok:
            print("   Create some audio files first using Voice Conversion.")
        if not syntax_ok:
            print("   Fix syntax errors in Python files.")

if __name__ == "__main__":
    main()
