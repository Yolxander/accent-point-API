# Voice-to-Voice Transformation API

This document describes the comprehensive voice-to-voice transformation API endpoints that use OpenVoice AI for advanced voice conversion.

## Overview

The Voice-to-Voice API provides two main endpoints for transforming audio:

1. **Form-based endpoint** (`/transform-voice`) - Accepts multipart form data with audio files
2. **JSON endpoint** (`/transform-voice-json`) - Accepts JSON with base64 encoded audio data

## Endpoints

### 1. Transform Voice (Form-based)

**POST** `/api/v1/transform-voice`

Accepts multipart form data with audio files and transformation parameters.

#### Parameters

- `input_audio` (file, required): Input audio file to transform
- `reference_audio` (file, required): Reference audio file for voice characteristics
- `transformation_type` (string, optional): Type of transformation (default: "voice_conversion")
- `device` (string, optional): Processing device - "cpu" or "cuda" (default: "cpu")
- `normalize` (boolean, optional): Normalize audio before processing (default: true)
- `target_sample_rate` (integer, optional): Target sample rate for processing
- `output_format` (string, optional): Output audio format - "wav", "mp3", "flac" (default: "wav")
- `quality` (string, optional): Output quality - "low", "medium", "high" (default: "high")
- `pitch_shift` (float, optional): Pitch shift in semitones (-12 to 12)
- `speed_change` (float, optional): Speed change multiplier (0.5 to 2.0)
- `volume_adjustment` (float, optional): Volume adjustment multiplier (0.1 to 3.0)
- `noise_reduction` (boolean, optional): Apply noise reduction (default: false)
- `echo_removal` (boolean, optional): Remove echo (default: false)
- `voice_enhancement` (boolean, optional): Enhance voice quality (default: false)

#### Response

```json
{
  "conversion_id": "uuid-string",
  "status": "completed",
  "message": "Voice transformation completed successfully",
  "transformation_type": "voice_conversion",
  "input_duration": 5.2,
  "output_duration": 5.2,
  "output_file": "transformed_uuid.wav",
  "file_size": 1048576,
  "download_url": "/api/v1/download/transformed_uuid.wav",
  "processing_time": 12.5,
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:00:12Z"
}
```

### 2. Transform Voice (JSON)

**POST** `/api/v1/transform-voice-json`

Accepts JSON request body with base64 encoded audio data.

#### Request Body

```json
{
  "input_audio": "base64-encoded-audio-data",
  "reference_audio": "base64-encoded-audio-data",
  "transformation_type": "voice_conversion",
  "device": "cpu",
  "normalize": true,
  "target_sample_rate": 22050,
  "output_format": "wav",
  "quality": "high",
  "voice_characteristics": {
    "pitch_shift": 2.0,
    "speed_change": 1.1,
    "volume_adjustment": 1.2
  }
}
```

#### Response

Same as form-based endpoint.

### 3. Get Transformation Types

**GET** `/api/v1/transformation-types`

Returns available transformation types and supported formats.

#### Response

```json
{
  "transformation_types": [
    {
      "id": "voice_conversion",
      "name": "Voice Conversion",
      "description": "Convert voice characteristics using reference audio"
    },
    {
      "id": "accent_change",
      "name": "Accent Change",
      "description": "Change accent while preserving voice characteristics"
    }
  ],
  "supported_formats": ["wav", "mp3", "flac", "m4a", "ogg"],
  "quality_levels": ["low", "medium", "high"]
}
```

### 4. Download Transformed Audio

**GET** `/api/v1/download/{filename}`

Downloads the transformed audio file.

### 5. Get Transformation Status

**GET** `/api/v1/transformation-status/{conversion_id}`

Gets the status of a voice transformation.

## Usage Examples

### Python Example (Form-based)

```python
import requests

# Prepare files
with open('input.wav', 'rb') as input_file, open('reference.wav', 'rb') as ref_file:
    files = {
        'input_audio': ('input.wav', input_file, 'audio/wav'),
        'reference_audio': ('reference.wav', ref_file, 'audio/wav')
    }
    data = {
        'transformation_type': 'voice_conversion',
        'device': 'cpu',
        'normalize': True,
        'output_format': 'wav',
        'quality': 'high',
        'pitch_shift': 2.0,
        'speed_change': 1.1,
        'volume_adjustment': 1.2,
        'noise_reduction': True,
        'voice_enhancement': True
    }
    
    response = requests.post('http://localhost:8000/api/v1/transform-voice', 
                           files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Conversion ID: {result['conversion_id']}")
        print(f"Download URL: {result['download_url']}")
```

### JavaScript Example (JSON)

```javascript
// Convert audio file to base64
async function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
    });
}

// Transform voice
async function transformVoice(inputFile, referenceFile) {
    const inputB64 = await fileToBase64(inputFile);
    const referenceB64 = await fileToBase64(referenceFile);
    
    const response = await fetch('/api/v1/transform-voice-json', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            input_audio: inputB64,
            reference_audio: referenceB64,
            transformation_type: 'voice_conversion',
            device: 'cpu',
            normalize: true,
            output_format: 'wav',
            quality: 'high',
            voice_characteristics: {
                pitch_shift: 2.0,
                speed_change: 1.1,
                volume_adjustment: 1.2
            }
        })
    });
    
    const result = await response.json();
    return result;
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid parameters or file format
- `413 Payload Too Large`: File size exceeds limit
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Processing errors

## Testing

Run the test script to verify the API functionality:

```bash
python test_voice_to_voice.py
```

## Notes

- Maximum file size: 50MB
- Supported audio formats: WAV, MP3, FLAC, M4A, OGG
- Processing is done asynchronously for large files
- Temporary files are automatically cleaned up
- The API uses OpenVoice AI for voice conversion
