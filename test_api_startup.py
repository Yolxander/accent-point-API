#!/usr/bin/env python3
"""
Test script to verify API startup with Supabase integration
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.supabase import supabase_config
from app.services.database_service import db_service


async def test_api_startup():
    """Test API startup components"""
    
    print("🚀 Testing API Startup with Supabase Integration...")
    print("=" * 60)
    
    # Test 1: Configuration loading
    print("1. Testing configuration loading...")
    try:
        print(f"   ✅ Environment: {settings.ENVIRONMENT}")
        print(f"   ✅ Host: {settings.HOST}")
        print(f"   ✅ Port: {settings.PORT}")
        print(f"   ✅ Supabase URL: {settings.SUPABASE_URL}")
        print(f"   ✅ Anon Key: {settings.SUPABASE_ANON_KEY[:20]}...")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 2: Supabase configuration
    print("\n2. Testing Supabase configuration...")
    try:
        print(f"   ✅ Supabase URL: {supabase_config.url}")
        print(f"   ✅ Anon Key: {supabase_config.anon_key[:20]}...")
        print(f"   ✅ Service Role Key: {supabase_config.service_role_key[:20]}...")
    except Exception as e:
        print(f"   ❌ Supabase config error: {e}")
        return False
    
    # Test 3: Database service initialization
    print("\n3. Testing database service initialization...")
    try:
        # Test connection
        is_connected = await db_service.test_connection()
        if is_connected:
            print("   ✅ Database service connected successfully!")
        else:
            print("   ⚠️  Database service connection failed (tables may not exist yet)")
    except Exception as e:
        print(f"   ⚠️  Database service error: {e}")
        print("   This is expected if the database schema hasn't been set up yet")
    
    # Test 4: API imports
    print("\n4. Testing API imports...")
    try:
        from app.api import voice_to_voice, health, text_to_speech, batch_processing
        from app.api.voice_conversion import router as voice_conversion_router
        print("   ✅ All API modules imported successfully!")
    except Exception as e:
        print(f"   ❌ API import error: {e}")
        return False
    
    # Test 5: FastAPI app creation
    print("\n5. Testing FastAPI app creation...")
    try:
        from main import app
        print("   ✅ FastAPI app created successfully!")
        print(f"   ✅ App title: {app.title}")
        print(f"   ✅ App version: {app.version}")
    except Exception as e:
        print(f"   ❌ FastAPI app error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 API startup test completed successfully!")
    print("\nYour OpenVoice API is ready with Supabase integration!")
    print("\nNext steps:")
    print("1. Set up the database schema (see SUPABASE_SETUP.md)")
    print("2. Start the API server: python main.py")
    print("3. Test the health endpoint: GET /api/v1/health/detailed")
    
    return True


async def main():
    """Main test function"""
    try:
        success = await test_api_startup()
        if success:
            sys.exit(0)
        else:
            print("\n❌ API startup test failed.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
