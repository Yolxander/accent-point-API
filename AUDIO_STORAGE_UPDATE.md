# Audio Storage Update - Database Integration

## Overview

This update modifies the OpenVoice API to store generated audio files directly in the database instead of the file system. This allows users to listen to audio without downloading it, providing a better user experience.

## Changes Made

### 1. Database Schema Updates

**File:** `supabase_schema.sql`

Added `output_audio_data BYTEA` column to store binary audio data in:
- `voice_conversions` table
- `text_to_speech_conversions` table  
- `batch_processing_files` table

### 2. Database Service Updates

**File:** `app/services/database_service.py`

Added new methods for audio storage and retrieval:

#### Voice Conversions
- `save_audio_to_conversion(conversion_id, audio_data, filename, file_size, duration)`
- `get_audio_from_conversion(conversion_id)`

#### Text-to-Speech Conversions
- `save_audio_to_tts_conversion(conversion_id, audio_data, filename, file_size, duration)`
- `get_audio_from_tts_conversion(conversion_id)`
- `get_text_to_speech_conversion(conversion_id)`

#### Batch Processing Files
- `save_audio_to_batch_file(file_id, audio_data, filename, file_size, duration)`
- `get_audio_from_batch_file(file_id)`

### 3. API Endpoint Updates

#### Voice-to-Voice API (`app/api/voice_to_voice.py`)

**Changes:**
- Modified `transform_voice()` to save audio to database instead of file system
- Modified `transform_voice_json()` to save audio to database instead of file system
- Updated response URLs to use `/play/{conversion_id}` instead of `/download/{filename}`
- Added new `/play/{conversion_id}` endpoint for streaming audio from database
- Kept `/download/{filename}` as legacy endpoint for file system storage

**New Endpoints:**
- `GET /play/{conversion_id}` - Stream audio from database by conversion ID

#### Text-to-Speech API (`app/api/text_to_speech.py`)

**Changes:**
- Modified `convert_text_to_speech()` to save audio to database
- Modified `preview_tts()` to return audio data directly in response
- Updated response URLs to use `/play-tts/{conversion_id}`
- Added new `/play-tts/{conversion_id}` endpoint for streaming TTS audio from database

**New Endpoints:**
- `GET /play-tts/{conversion_id}` - Stream TTS audio from database by conversion ID

### 4. Response Format Changes

**Before:**
```json
{
  "conversion_id": "uuid",
  "status": "completed",
  "download_url": "/api/v1/download/filename.wav"
}
```

**After:**
```json
{
  "conversion_id": "uuid", 
  "status": "completed",
  "download_url": "/api/v1/play/uuid"
}
```

## Benefits

1. **No File Downloads Required** - Users can listen to audio directly in the browser
2. **Better User Experience** - Instant audio playback without waiting for downloads
3. **Centralized Storage** - All audio data stored in database for better management
4. **Scalability** - Database storage scales better than file system storage
5. **Backup & Recovery** - Audio data included in database backups

## API Usage

### Voice-to-Voice Transformation

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/transform-voice" \
  -F "input_audio=@input.wav" \
  -F "reference_audio=@reference.wav" \
  -F "transformation_type=voice_conversion"
```

**Response:**
```json
{
  "conversion_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "message": "Voice transformation completed successfully",
  "download_url": "/api/v1/play/123e4567-e89b-12d3-a456-426614174000",
  "file_size": 1234567,
  "output_duration": 5.2
}
```

**Play Audio:**
```bash
curl "http://localhost:8000/api/v1/play/123e4567-e89b-12d3-a456-426614174000" \
  --output audio.wav
```

### Text-to-Speech

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/convert-text-to-speech" \
  -F "text=Hello, this is a test" \
  -F "reference_audio=@reference.wav"
```

**Response:**
```json
{
  "conversion_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed", 
  "message": "Text-to-speech conversion completed successfully",
  "download_url": "/api/v1/play-tts/123e4567-e89b-12d3-a456-426614174000",
  "file_size": 987654
}
```

**Play Audio:**
```bash
curl "http://localhost:8000/api/v1/play-tts/123e4567-e89b-12d3-a456-426614174000" \
  --output tts_audio.wav
```

## Frontend Integration

### HTML Audio Player

```html
<audio controls>
  <source src="/api/v1/play/123e4567-e89b-12d3-a456-426614174000" type="audio/wav">
  Your browser does not support the audio element.
</audio>
```

### JavaScript Fetch

```javascript
const response = await fetch('/api/v1/transform-voice', {
  method: 'POST',
  body: formData
});

const result = await response.json();

// Play audio directly
const audio = new Audio(result.download_url);
audio.play();
```

## Testing

### Test Script

Run the test script to verify database storage functionality:

```bash
python test_audio_storage.py
```

### Demo Page

Open `audio_player_demo.html` in a browser to test the complete functionality with a user-friendly interface.

## Migration Notes

1. **Database Migration** - Run the updated `supabase_schema.sql` to add the new columns
2. **Backward Compatibility** - Legacy `/download/{filename}` endpoints still work for existing file system storage
3. **Fallback Mechanism** - If database storage fails, the system falls back to file system storage
4. **Cleanup** - Temporary files are automatically cleaned up after processing

## Configuration

No additional configuration is required. The system automatically uses the existing Supabase configuration for database storage.

## Performance Considerations

1. **Memory Usage** - Audio data is loaded into memory during processing
2. **Database Size** - Binary data will increase database size significantly
3. **Network Transfer** - Audio streaming may use more bandwidth than file downloads
4. **Caching** - Consider implementing caching for frequently accessed audio files

## Security

1. **Access Control** - Audio access is controlled by conversion ID
2. **Data Validation** - Audio data is validated before storage
3. **Size Limits** - Existing file size limits still apply
4. **Cleanup** - Temporary files are properly cleaned up

## Future Enhancements

1. **Audio Compression** - Implement audio compression to reduce storage size
2. **CDN Integration** - Use CDN for better audio delivery performance
3. **Caching Layer** - Add Redis caching for frequently accessed audio
4. **Audio Streaming** - Implement proper audio streaming with range requests
5. **Audio Metadata** - Store additional audio metadata (bitrate, channels, etc.)
