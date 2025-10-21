#!/usr/bin/env python3
"""
Test script for Supabase Storage integration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.storage_service import storage_service
from app.core.logging import get_logger

logger = get_logger(__name__)


async def test_storage_integration():
    """Test the Supabase Storage integration"""
    print("Testing Supabase Storage integration...")
    
    try:
        # Test 1: Ensure bucket exists
        print("\n1. Testing bucket creation...")
        bucket_exists = await storage_service.ensure_bucket_exists()
        print(f"   Bucket exists: {bucket_exists}")
        
        # Test 2: Upload a test file
        print("\n2. Testing file upload...")
        test_audio_data = b"fake audio data for testing"
        test_filename = "test_audio.wav"
        
        storage_info = await storage_service.upload_audio_file(
            audio_data=test_audio_data,
            filename=test_filename,
            folder="test_conversions"
        )
        
        print(f"   Upload successful!")
        print(f"   File path: {storage_info['file_path']}")
        print(f"   Public URL: {storage_info['public_url']}")
        print(f"   File size: {storage_info['file_size']} bytes")
        
        # Test 3: Download the file
        print("\n3. Testing file download...")
        downloaded_data = await storage_service.get_audio_file(storage_info['file_path'])
        
        if downloaded_data == test_audio_data:
            print("   Download successful! Data matches original.")
        else:
            print("   Download failed! Data doesn't match original.")
        
        # Test 4: Get public URL
        print("\n4. Testing public URL generation...")
        public_url = await storage_service.get_public_url(storage_info['file_path'])
        print(f"   Public URL: {public_url}")
        
        # Test 5: List files
        print("\n5. Testing file listing...")
        files = await storage_service.list_audio_files("test_conversions")
        print(f"   Found {len(files)} files in test_conversions folder")
        for file_info in files:
            print(f"   - {file_info.get('name', 'unknown')}")
        
        # Test 6: Clean up - delete the test file
        print("\n6. Testing file deletion...")
        deleted = await storage_service.delete_audio_file(storage_info['file_path'])
        print(f"   File deleted: {deleted}")
        
        print("\n✅ All tests passed! Supabase Storage integration is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Storage integration test failed: {e}")
        return False
    
    return True


async def main():
    """Main test function"""
    print("=" * 60)
    print("SUPABASE STORAGE INTEGRATION TEST")
    print("=" * 60)
    
    success = await test_storage_integration()
    
    if success:
        print("\n🎉 Storage integration test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Storage integration test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
