#!/usr/bin/env python3
"""
Test script for voice-to-voice transformation endpoint
"""

import requests
import json
import base64
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_voice_to_voice_endpoints():
    """Test the voice-to-voice transformation endpoints"""
    
    print("🎤 Testing Voice-to-Voice Transformation API")
    print("=" * 50)
    
    # Test 1: Get transformation types
    print("\n1. Testing transformation types endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/transformation-types")
        if response.status_code == 200:
            data = response.json()
            print("✅ Transformation types retrieved successfully")
            print(f"   Available types: {len(data['transformation_types'])}")
            for t in data['transformation_types']:
                print(f"   - {t['id']}: {t['name']}")
        else:
            print(f"❌ Failed to get transformation types: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting transformation types: {e}")
    
    # Test 2: Test with sample audio files (if they exist)
    print("\n2. Testing voice transformation with sample files...")
    
    # Look for sample audio files in the project
    sample_files = []
    for ext in ['.wav', '.mp3', '.flac']:
        sample_files.extend(Path('.').glob(f"**/*{ext}"))
    
    if len(sample_files) >= 2:
        input_file = str(sample_files[0])
        reference_file = str(sample_files[1])
        
        print(f"   Using input file: {input_file}")
        print(f"   Using reference file: {reference_file}")
        
        try:
            # Test form-based endpoint
            with open(input_file, 'rb') as f1, open(reference_file, 'rb') as f2:
                files = {
                    'input_audio': ('input.wav', f1, 'audio/wav'),
                    'reference_audio': ('reference.wav', f2, 'audio/wav')
                }
                data = {
                    'transformation_type': 'voice_conversion',
                    'device': 'cpu',
                    'normalize': True,
                    'output_format': 'wav',
                    'quality': 'high'
                }
                
                response = requests.post(f"{BASE_URL}/transform-voice", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Voice transformation completed successfully")
                    print(f"   Conversion ID: {result['conversion_id']}")
                    print(f"   Status: {result['status']}")
                    print(f"   Output file: {result['output_file']}")
                    print(f"   Processing time: {result.get('processing_time', 'N/A')}s")
                else:
                    print(f"❌ Voice transformation failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error during voice transformation: {e}")
    else:
        print("⚠️  No sample audio files found for testing")
        print("   Please add some .wav, .mp3, or .flac files to test with")
    
    # Test 3: Test JSON endpoint with base64 data
    print("\n3. Testing JSON endpoint with base64 data...")
    
    if len(sample_files) >= 2:
        try:
            # Read and encode sample files
            with open(sample_files[0], 'rb') as f:
                input_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            with open(sample_files[1], 'rb') as f:
                reference_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Create JSON request
            json_data = {
                "input_audio": input_b64,
                "reference_audio": reference_b64,
                "transformation_type": "voice_conversion",
                "device": "cpu",
                "normalize": True,
                "output_format": "wav",
                "quality": "high",
                "voice_characteristics": {
                    "pitch_shift": 2.0,
                    "speed_change": 1.1,
                    "volume_adjustment": 1.2
                }
            }
            
            response = requests.post(
                f"{BASE_URL}/transform-voice-json",
                json=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ JSON voice transformation completed successfully")
                print(f"   Conversion ID: {result['conversion_id']}")
                print(f"   Status: {result['status']}")
                print(f"   Transformation type: {result['transformation_type']}")
                print(f"   Processing time: {result.get('processing_time', 'N/A')}s")
            else:
                print(f"❌ JSON voice transformation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during JSON voice transformation: {e}")
    else:
        print("⚠️  No sample audio files found for JSON testing")
    
    # Test 4: Test download endpoint (if we have a successful conversion)
    print("\n4. Testing download endpoint...")
    try:
        # Try to download a file (this will fail if no files exist, which is expected)
        response = requests.get(f"{BASE_URL}/download/test_file.wav")
        if response.status_code == 404:
            print("✅ Download endpoint is working (404 for non-existent file is expected)")
        elif response.status_code == 200:
            print("✅ Download endpoint is working")
        else:
            print(f"⚠️  Unexpected response from download endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing download endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Voice-to-Voice API testing completed!")


def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   OpenVoice available: {data.get('openvoice_available', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error during health check: {e}")


if __name__ == "__main__":
    print("🚀 Starting Voice-to-Voice API Tests")
    print("Make sure the API server is running on http://localhost:8000")
    print()
    
    # Test health first
    test_health_endpoint()
    
    # Test voice-to-voice endpoints
    test_voice_to_voice_endpoints()
    
    print("\n📝 Test Summary:")
    print("   - Check the output above for any errors")
    print("   - If you see ❌ errors, check the API server logs")
    print("   - If you see ⚠️ warnings, they are usually not critical")
    print("   - If you see ✅ success messages, the endpoints are working!")
