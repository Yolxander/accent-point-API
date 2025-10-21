#!/usr/bin/env python3
"""
Example script demonstrating voice conversion with Supabase Storage
"""

import requests
import json
import os
from pathlib import Path

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"
CONVERT_ENDPOINT = f"{API_BASE_URL}/api/v1/convert-voice"

def create_test_audio_file(filename: str, content: bytes = b"fake audio data") -> str:
    """Create a test audio file"""
    file_path = f"/tmp/{filename}"
    with open(file_path, 'wb') as f:
        f.write(content)
    return file_path

def test_voice_conversion_with_storage():
    """Test voice conversion with Supabase Storage"""
    print("=" * 60)
    print("VOICE CONVERSION WITH SUPABASE STORAGE EXAMPLE")
    print("=" * 60)
    
    try:
        # Create test audio files
        print("\n1. Creating test audio files...")
        input_file = create_test_audio_file("input_test.wav", b"input audio data for testing")
        reference_file = create_test_audio_file("reference_test.wav", b"reference audio data for testing")
        
        print(f"   Input file: {input_file}")
        print(f"   Reference file: {reference_file}")
        
        # Prepare the request
        print("\n2. Preparing API request...")
        files = {
            'input_audio': ('input_test.wav', open(input_file, 'rb'), 'audio/wav'),
            'reference_audio': ('reference_test.wav', open(reference_file, 'rb'), 'audio/wav')
        }
        
        data = {
            'device': 'cpu',
            'normalize': True,
            'target_sample_rate': 22050
        }
        
        print("   Files and parameters prepared")
        
        # Make the API request
        print("\n3. Making API request...")
        print(f"   POST {CONVERT_ENDPOINT}")
        
        response = requests.post(CONVERT_ENDPOINT, files=files, data=data)
        
        # Close file handles
        files['input_audio'][1].close()
        files['reference_audio'][1].close()
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Request successful!")
            
            print("\n4. Response details:")
            print(f"   Conversion ID: {result.get('conversion_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Output File: {result.get('output_file')}")
            print(f"   File Size: {result.get('file_size')} bytes")
            print(f"   Duration: {result.get('output_duration')} seconds")
            print(f"   Processing Time: {result.get('processing_time')} seconds")
            
            # Check for Supabase Storage URL
            public_url = result.get('public_url')
            if public_url:
                print(f"   🎉 Public URL: {public_url}")
                print("   This URL provides direct access to the audio file in Supabase Storage!")
            else:
                print("   ⚠️  No public URL found - check Supabase Storage configuration")
            
            # Test the play URL
            play_url = result.get('play_url')
            if play_url:
                full_play_url = f"{API_BASE_URL}{play_url}"
                print(f"   Play URL: {full_play_url}")
                
                # Test the play endpoint
                print("\n5. Testing play endpoint...")
                play_response = requests.get(full_play_url)
                if play_response.status_code == 200:
                    print("   ✅ Play endpoint working!")
                    print(f"   Audio data size: {len(play_response.content)} bytes")
                else:
                    print(f"   ❌ Play endpoint failed: {play_response.status_code}")
            
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed!")
        print("   Make sure the API server is running:")
        print("   cd accent-point-API && python main.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        # Clean up test files
        try:
            os.unlink(input_file)
            os.unlink(reference_file)
            print(f"\n6. Cleaned up test files")
        except:
            pass

def main():
    """Main function"""
    print("This example demonstrates voice conversion with Supabase Storage integration.")
    print("Make sure the API server is running before executing this script.")
    print()
    
    # Check if API server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API server is running")
            test_voice_conversion_with_storage()
        else:
            print("❌ API server is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        print("   Start the server with: cd accent-point-API && python main.py")

if __name__ == "__main__":
    main()
