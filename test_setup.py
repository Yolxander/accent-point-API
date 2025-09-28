#!/usr/bin/env python3
"""
Test script to verify OpenVoice API setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test FastAPI imports
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ FastAPI imports successful")
        
        # Test app modules
        from app.core.config import settings
        print("✅ App config import successful")
        
        from app.core.logging import setup_logging
        print("✅ App logging import successful")
        
        from app.core.exceptions import setup_exception_handlers
        print("✅ App exceptions import successful")
        
        # Test API modules
        from app.api import health, voice_conversion, text_to_speech, batch_processing
        print("✅ API modules import successful")
        
        # Test service modules
        from app.services.audio_processor import AudioProcessor
        from app.services.voice_converter import VoiceConverter
        from app.services.tts_service import TTSService
        print("✅ Service modules import successful")
        
        # Test model modules
        from app.models.conversion import ConversionRequest, ConversionResponse
        print("✅ Model modules import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_directories():
    """Test if required directories exist"""
    print("\n📁 Testing directories...")
    
    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/services',
        'app/utils',
        'tests'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            all_exist = False
    
    return all_exist

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from app.core.config import settings
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        print(f"✅ Host: {settings.HOST}")
        print(f"✅ Port: {settings.PORT}")
        print(f"✅ Allowed origins: {settings.ALLOWED_ORIGINS}")
        print(f"✅ OpenVoice device: {settings.OPENVOICE_DEVICE}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_openvoice():
    """Test OpenVoice availability"""
    print("\n🎵 Testing OpenVoice availability...")
    
    try:
        import openvoice_cli.__main__ as openvoice_main
        print("✅ OpenVoice CLI is available")
        return True
    except ImportError:
        print("❌ OpenVoice CLI not available")
        print("   Install with: pip install openvoice-cli")
        return False
    except Exception as e:
        print(f"❌ OpenVoice error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 OpenVoice API Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_directories,
        test_config,
        test_openvoice
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! OpenVoice API is ready to run.")
        print("Run with: python main.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
