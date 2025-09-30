#!/usr/bin/env python3
"""
Test script to verify Supabase connection and database setup
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.supabase import supabase_config
from app.services.database_service import db_service


async def test_supabase_connection():
    """Test Supabase connection and basic operations"""
    
    print("🔍 Testing Supabase Connection...")
    print("=" * 50)
    
    # Test 1: Basic connection
    print("1. Testing basic connection...")
    try:
        is_connected = await supabase_config.test_connection()
        if is_connected:
            print("✅ Supabase connection successful!")
        else:
            print("❌ Supabase connection failed!")
            return False
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False
    
    # Test 2: Database service connection
    print("\n2. Testing database service...")
    try:
        is_connected = await db_service.test_connection()
        if is_connected:
            print("✅ Database service connection successful!")
        else:
            print("❌ Database service connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database service error: {e}")
        return False
    
    # Test 3: Create a test voice conversion record
    print("\n3. Testing voice conversion record creation...")
    try:
        test_record = await db_service.create_voice_conversion(
            user_id=None,
            session_id="test_session_123",
            transformation_type="voice_conversion",
            source_audio_filename="test_input.wav",
            source_audio_size=1024000,
            source_audio_duration=30.5,
            reference_audio_filename="test_reference.wav",
            reference_audio_size=512000,
            reference_audio_duration=15.2,
            pitch_shift=0,
            speed_multiplier=1.0,
            volume_multiplier=1.0,
            noise_reduction=False,
            echo_removal=False,
            voice_enhancement=False,
            output_format="wav",
            quality="high"
        )
        
        if test_record and test_record.get("id"):
            print(f"✅ Test record created successfully! ID: {test_record['id']}")
            test_id = test_record["id"]
        else:
            print("❌ Failed to create test record!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test record: {e}")
        return False
    
    # Test 4: Retrieve the test record
    print("\n4. Testing record retrieval...")
    try:
        retrieved_record = await db_service.get_voice_conversion(test_id)
        if retrieved_record:
            print(f"✅ Test record retrieved successfully!")
            print(f"   - Status: {retrieved_record.get('status')}")
            print(f"   - Transformation Type: {retrieved_record.get('transformation_type')}")
            print(f"   - Created At: {retrieved_record.get('created_at')}")
        else:
            print("❌ Failed to retrieve test record!")
            return False
    except Exception as e:
        print(f"❌ Error retrieving test record: {e}")
        return False
    
    # Test 5: Update the test record
    print("\n5. Testing record update...")
    try:
        updated_record = await db_service.update_voice_conversion(
            test_id,
            status="completed",
            output_filename="test_output.wav",
            output_file_size=2048000,
            output_duration=30.5,
            processing_time_seconds=15.2,
            completed_at="2024-01-01T12:00:00Z"
        )
        
        if updated_record:
            print(f"✅ Test record updated successfully!")
            print(f"   - New Status: {updated_record.get('status')}")
            print(f"   - Output File: {updated_record.get('output_filename')}")
        else:
            print("❌ Failed to update test record!")
            return False
    except Exception as e:
        print(f"❌ Error updating test record: {e}")
        return False
    
    # Test 6: Test API usage stats
    print("\n6. Testing API usage stats...")
    try:
        await db_service.update_api_usage_stats(
            user_id=None,
            endpoint="test_endpoint",
            processing_time=15.2,
            file_size=1024000
        )
        print("✅ API usage stats updated successfully!")
    except Exception as e:
        print(f"❌ Error updating usage stats: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All Supabase tests passed successfully!")
    print("✅ Your OpenVoice API is now connected to Supabase!")
    print("\nNext steps:")
    print("1. Run the database schema: supabase_schema.sql")
    print("2. Start your API server: python main.py")
    print("3. Test the health endpoint: GET /api/v1/health/detailed")
    
    return True


async def main():
    """Main test function"""
    print("🚀 OpenVoice API - Supabase Connection Test")
    print("=" * 50)
    
    try:
        success = await test_supabase_connection()
        if success:
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check your Supabase configuration.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
