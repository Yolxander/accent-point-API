# Supabase Storage Integration

This document describes the integration of Supabase Storage for audio file management in the OpenVoice API.

## Overview

The API has been updated to use Supabase Storage instead of storing audio files directly in the database. This provides better scalability, performance, and cost-effectiveness for audio file storage.

## Changes Made

### 1. New Storage Service (`app/services/storage_service.py`)

A new service class `StorageService` has been created to handle all Supabase Storage operations:

- **Bucket Management**: Automatically creates and manages the `audio-files` bucket
- **File Upload**: Uploads audio files to Supabase Storage with unique filenames
- **File Download**: Retrieves audio files from Supabase Storage
- **Public URLs**: Generates public URLs for direct access to audio files
- **File Management**: Lists, deletes, and manages audio files

### 2. Updated Database Service (`app/services/database_service.py`)

The `DatabaseService` has been updated to use Supabase Storage:

- **Storage Integration**: All audio storage methods now use Supabase Storage
- **Metadata Storage**: Stores file paths and public URLs in the database
- **Fallback Support**: Maintains fallback to file system storage if Supabase Storage fails

### 3. Updated API Models (`app/models/conversion.py`)

Response models have been updated to include Supabase Storage URLs:

- **ConversionResponse**: Added `public_url` field for direct access
- **TTSResponse**: Added `public_url` field for direct access
- **VoiceToVoiceResponse**: Added `public_url` field for direct access

### 4. Updated Configuration (`app/core/config.py`)

Added S3 storage configuration:

```python
# S3 Storage (for Supabase Storage)
S3_ACCESS_KEY: str = "625729a08b95bf1b7ff351a663f3a23c"
S3_SECRET_KEY: str = "850181e4652dd023b7a98c58ae0d2d34bd487ee0cc3254aed6eda37307425907"
S3_BUCKET_NAME: str = "audio-files"
```

### 5. Updated Supabase Configuration (`app/core/supabase.py`)

Added S3 credentials to the Supabase configuration:

```python
self.s3_access_key: str = os.getenv("S3_ACCESS_KEY", "625729a08b95bf1b7ff351a663f3a23c")
self.s3_secret_key: str = os.getenv("S3_SECRET_KEY", "850181e4652dd023b7a98c58ae0d2d34bd487ee0cc3254aed6eda37307425907")
```

## API Response Changes

### Voice Conversion Response

The `/api/v1/convert-voice` endpoint now returns a `public_url` field:

```json
{
  "conversion_id": "uuid",
  "status": "completed",
  "message": "Voice conversion completed successfully",
  "output_file": "converted_uuid.wav",
  "file_size": 1234567,
  "download_url": "/api/v1/play-voice/uuid",
  "play_url": "/api/v1/play-voice/uuid",
  "public_url": "http://127.0.0.1:54321/storage/v1/object/public/audio-files/voice_conversions/uuid.wav",
  "output_duration": 30.5,
  "processing_time": 5.2,
  "completed_at": "2024-01-01T12:00:00Z"
}
```

## Storage Structure

Audio files are organized in Supabase Storage as follows:

```
audio-files/
├── voice_conversions/
│   ├── uuid1.wav
│   ├── uuid2.wav
│   └── ...
├── tts_conversions/
│   ├── uuid1.wav
│   ├── uuid2.wav
│   └── ...
└── batch_processing/
    ├── uuid1.wav
    ├── uuid2.wav
    └── ...
```

## Database Schema Updates

The database tables now include additional fields for Supabase Storage:

- `output_file_path`: Path to the file in Supabase Storage
- `output_public_url`: Public URL for direct access to the file

## Testing

### Test Storage Integration

Run the storage integration test:

```bash
cd accent-point-API
python test_storage_integration.py
```

### Test Voice Conversion

Run the voice conversion test:

```bash
cd accent-point-API
python test_voice_conversion_storage.py
```

## Environment Variables

Make sure to set the following environment variables:

```bash
# Supabase Configuration
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU

# S3 Storage Configuration
S3_ACCESS_KEY=625729a08b95bf1b7ff351a663f3a23c
S3_SECRET_KEY=850181e4652dd023b7a98c58ae0d2d34bd487ee0cc3254aed6eda37307425907
S3_BUCKET_NAME=audio-files
```

## Benefits

1. **Scalability**: Supabase Storage can handle large amounts of audio files
2. **Performance**: Faster file access and streaming
3. **Cost-Effectiveness**: More efficient storage than database binary data
4. **Public Access**: Direct URLs for easy integration with frontend applications
5. **CDN Support**: Supabase Storage can be configured with CDN for global distribution
6. **Backup & Recovery**: Built-in backup and recovery features

## Migration Notes

- Existing audio files stored in the database will continue to work
- New audio files will be stored in Supabase Storage
- The API maintains backward compatibility with existing endpoints
- Fallback to file system storage is maintained for reliability

## Troubleshooting

### Common Issues

1. **Bucket Creation Fails**: Check Supabase Storage permissions and S3 credentials
2. **Upload Fails**: Verify file size limits and MIME type restrictions
3. **Public URL Not Working**: Check bucket public access settings
4. **Download Fails**: Verify file path and storage permissions

### Debug Mode

Enable debug logging to troubleshoot storage issues:

```python
import logging
logging.getLogger("app.services.storage_service").setLevel(logging.DEBUG)
```

## Future Enhancements

1. **CDN Integration**: Configure CDN for global audio file distribution
2. **File Compression**: Implement audio file compression before storage
3. **Retention Policies**: Add automatic file cleanup for old conversions
4. **Analytics**: Track storage usage and file access patterns
5. **Encryption**: Add client-side encryption for sensitive audio files
