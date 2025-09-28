#!/usr/bin/env python3
"""
Basic test script for OpenVoice API setup
"""

import sys
import os

def test_basic_imports():
    """Test if basic modules can be imported"""
    print("🧪 Testing basic imports...")
    
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
        from app.api import health
        print("✅ Health API module import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from app.core.config import settings
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        print(f"✅ Host: {settings.HOST}")
        print(f"✅ Port: {settings.PORT}")
        print(f"✅ Allowed origins: {settings.ALLOWED_ORIGINS}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
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
        'app/utils'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🚀 OpenVoice API Basic Setup Test")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_config,
        test_directories
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
        print("\n🎉 Basic setup is working! You can now run:")
        print("   python main-basic.py")
        print("\nFor full functionality, install OpenVoice CLI:")
        print("   pip install openvoice-cli")
        print("   python main.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
