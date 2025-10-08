#!/usr/bin/env python3
"""
Quick script to check if Supabase tables exist
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.database_service import db_service

async def check_tables():
    """Check if the required tables exist"""
    print("🔍 Checking Supabase database tables...")
    
    try:
        # Test connection
        if not await db_service.test_connection():
            print("❌ Cannot connect to Supabase database")
            return False
        
        print("✅ Connected to Supabase database")
        
        # Check if voice_conversions table exists and has the audio column
        try:
            result = db_service.client.table("voice_conversions").select("id, output_audio_data").limit(1).execute()
            print("✅ voice_conversions table exists")
            
            # Check if output_audio_data column exists
            if result.data is not None:
                print("✅ output_audio_data column exists")
            else:
                print("⚠️  output_audio_data column may not exist")
                
        except Exception as e:
            print(f"❌ voice_conversions table issue: {e}")
            return False
        
        # Check text_to_speech_conversions table
        try:
            result = db_service.client.table("text_to_speech_conversions").select("id").limit(1).execute()
            print("✅ text_to_speech_conversions table exists")
        except Exception as e:
            print(f"❌ text_to_speech_conversions table issue: {e}")
            return False
        
        # Check batch_processing_files table
        try:
            result = db_service.client.table("batch_processing_files").select("id").limit(1).execute()
            print("✅ batch_processing_files table exists")
        except Exception as e:
            print(f"❌ batch_processing_files table issue: {e}")
            return False
        
        print("\n🎉 All required tables exist! You can now use the play button functionality.")
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

async def main():
    """Main function"""
    print("=" * 50)
    print("Supabase Database Table Checker")
    print("=" * 50)
    
    success = await check_tables()
    
    if not success:
        print("\n🔧 To fix this:")
        print("1. Open Supabase Studio: http://127.0.0.1:54323")
        print("2. Go to SQL Editor")
        print("3. Run the supabase_schema.sql file")
        print("4. Run this script again")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
