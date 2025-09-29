# Postman Setup Guide for Voice-to-Voice API

## 🚀 Quick Start

### 1. Import the Collection
1. Open Postman
2. Click **Import** button
3. Select the `Postman_Collection.json` file from this project
4. The collection will be imported with all endpoints ready to use

### 2. Set Up Environment Variables
The collection uses these variables:
- `base_url`: `http://localhost:8000` (default)
- `conversion_id`: Auto-populated from responses
- `output_filename`: Auto-populated from responses

### 3. Start the API Server
```bash
# Make sure you're in the project directory
cd /Users/humancontact/Downloads/demos/nextjs/accent-point-API

# Activate virtual environment
source venv/bin/activate  # or openvoice_env/bin/activate

# Start the server
python main.py
```

## 📋 Available Endpoints

### 1. **Health Check** (GET)
- **URL**: `{{base_url}}/api/v1/health`
- **Purpose**: Check if API is running and OpenVoice is available
- **No parameters needed**

### 2. **Get Transformation Types** (GET)
- **URL**: `{{base_url}}/api/v1/transformation-types`
- **Purpose**: Get available transformation types and supported formats
- **No parameters needed**

### 3. **Transform Voice (Form Data)** (POST)
- **URL**: `{{base_url}}/api/v1/transform-voice`
- **Purpose**: Transform voice using uploaded audio files
- **Parameters**:
  - `input_audio` (file): Your input audio file
  - `reference_audio` (file): Reference voice file
  - `transformation_type` (text): Type of transformation
  - `device` (text): "cpu" or "cuda"
  - `normalize` (text): "true" or "false"
  - `output_format` (text): "wav", "mp3", "flac"
  - `quality` (text): "low", "medium", "high"
  - `pitch_shift` (text): -12 to 12 semitones
  - `speed_change` (text): 0.5 to 2.0 multiplier
  - `volume_adjustment` (text): 0.1 to 3.0 multiplier
  - `noise_reduction` (text): "true" or "false"
  - `echo_removal` (text): "true" or "false"
  - `voice_enhancement` (text): "true" or "false"

### 4. **Transform Voice (JSON)** (POST)
- **URL**: `{{base_url}}/api/v1/transform-voice-json`
- **Purpose**: Transform voice using base64 encoded audio data
- **Body**: JSON with base64 audio data and parameters

### 5. **Get Transformation Status** (GET)
- **URL**: `{{base_url}}/api/v1/transformation-status/{{conversion_id}}`
- **Purpose**: Check status of a transformation
- **Uses auto-populated conversion_id**

### 6. **Download Transformed Audio** (GET)
- **URL**: `{{base_url}}/api/v1/download/{{output_filename}}`
- **Purpose**: Download the transformed audio file
- **Uses auto-populated output_filename**

## 🧪 Testing Workflow

### Step 1: Health Check
1. Run the **Health Check** request
2. Verify you get a 200 response with OpenVoice status

### Step 2: Get Available Options
1. Run **Get Transformation Types**
2. See what transformation types are available

### Step 3: Basic Voice Transformation
1. Run **Transform Voice (Form Data)**
2. Upload your input audio file
3. Upload your reference audio file
4. Set desired parameters
5. Send the request
6. Note the `conversion_id` and `output_filename` from the response

### Step 4: Download Result
1. Run **Download Transformed Audio**
2. The `output_filename` should be auto-populated
3. Download and listen to your transformed audio

### Step 5: Advanced Testing
1. Try **Transform Voice - Advanced Options** with all enhancements enabled
2. Test different transformation types in the **Test Different Transformation Types** folder
3. Experiment with different parameter combinations

## 📁 Sample Audio Files

For testing, you can use any audio files in these formats:
- WAV (.wav)
- MP3 (.mp3)
- FLAC (.flac)
- M4A (.m4a)
- OGG (.ogg)

**Tip**: Use short audio files (5-30 seconds) for faster processing during testing.

## 🔧 Troubleshooting

### Common Issues:

1. **Connection Refused**
   - Make sure the API server is running on `http://localhost:8000`
   - Check if the port is available

2. **File Upload Errors**
   - Ensure audio files are in supported formats
   - Check file size (max 50MB)
   - Verify both input and reference files are selected

3. **OpenVoice Not Available**
   - Check the health endpoint response
   - Make sure OpenVoice is properly installed
   - Check server logs for detailed error messages

4. **Transformation Fails**
   - Check the response for error details
   - Verify audio files are valid
   - Try with different parameter values

### Debug Steps:
1. Check server logs in the terminal where you started the API
2. Use the Health Check endpoint to verify OpenVoice availability
3. Try with simpler parameters first (no enhancements)
4. Test with different audio files

## 📊 Expected Responses

### Successful Transformation:
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

### Error Response:
```json
{
  "conversion_id": "uuid-string",
  "status": "failed",
  "message": "Voice transformation failed",
  "transformation_type": "voice_conversion",
  "error_message": "Detailed error description",
  "processing_time": 2.1
}
```

## 🎯 Pro Tips

1. **Start Simple**: Begin with basic voice conversion before trying advanced options
2. **Use Short Files**: Test with 5-10 second audio clips for faster results
3. **Check Variables**: The collection auto-populates `conversion_id` and `output_filename`
4. **Monitor Logs**: Keep an eye on the server terminal for detailed processing information
5. **Save Responses**: Postman will save your responses for easy reference

Happy testing! 🎤✨
