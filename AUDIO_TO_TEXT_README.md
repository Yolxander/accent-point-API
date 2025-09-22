# 🎤 Audio to Text Converter

This is a separate page in the OpenVoice AI Suite that allows you to convert your processed audio files to text using OpenAI's Whisper AI transcription.

## Features

- **🤖 AI-Powered Transcription**: Uses OpenAI Whisper for high-accuracy speech-to-text conversion
- **�� Multi-language Support**: Supports 99+ languages with automatic detection
- **📊 Detailed Segments**: Provides timestamped transcription segments
- **🎧 Audio Preview**: Listen to audio files before and during transcription
- **💾 Export Options**: Download transcribed text as .txt files
- **📋 Copy to Clipboard**: Easy copying of transcribed text

## How to Use

### 1. Install Dependencies

First, make sure you have the required dependencies installed:

```bash
pip install openai-whisper
```

### 2. Launch the Audio to Text App

You can run the audio-to-text converter in several ways:

#### Option A: Using the Suite Launcher (Recommended)
```bash
./run_suite.sh
```
Then navigate to the "Audio to Text" section.

#### Option B: Run Directly
```bash
streamlit run app_audio_to_text.py
```

#### Option C: Run with Navigation
```bash
streamlit run launcher.py
```
Then go to `http://localhost:8501/?page=audio_to_text`

### 3. Using the App

1. **Load a Whisper Model**: Select the model size and click "Load Model"
   - `tiny`: Fastest, least accurate
   - `base`: Good balance (recommended)
   - `small`: More accurate, slower
   - `medium`: High accuracy, slower
   - `large`: Best accuracy, slowest

2. **Select Language** (Optional): Choose a specific language for better accuracy, or leave as "Auto-detect"

3. **Choose Audio File**: Select from your processed audio files (from the `processed/` directory)

4. **Start Transcription**: Click "Start Transcription" to convert audio to text

5. **View Results**: 
   - See the transcribed text
   - Copy to clipboard
   - Download as text file
   - View detailed segments with timestamps

## Supported Audio Formats

- WAV files (recommended)
- MP3 files
- M4A files
- FLAC files
- And more formats supported by Whisper

## Model Performance

| Model Size | Speed | Accuracy | Memory Usage |
|------------|-------|----------|--------------|
| tiny       | Fastest | Good | ~1 GB |
| base       | Fast | Better | ~1 GB |
| small      | Medium | Good | ~2 GB |
| medium     | Slow | Better | ~5 GB |
| large      | Slowest | Best | ~10 GB |

## Workflow Integration

This audio-to-text converter works perfectly with the main OpenVoice voice conversion app:

1. **Step 1**: Use the Voice Conversion app to convert your audio files with different accents
2. **Step 2**: Use this Audio to Text app to transcribe the converted audio files
3. **Step 3**: Export the transcribed text for further use

## Troubleshooting

### Common Issues

1. **"No audio files found"**: Make sure you have processed audio files in the `processed/` directory
2. **Model loading fails**: Check your internet connection and available disk space
3. **Transcription errors**: Try a different model size or specify the language explicitly

### Performance Tips

- Use `tiny` or `base` models for faster processing
- Specify the language for better accuracy
- Ensure sufficient disk space for model downloads
- Close other applications to free up memory

## File Structure

The app looks for audio files in this structure:
```
processed/
├── folder1/
│   └── wavs/
│       ├── file1.wav
│       └── file2.wav
└── folder2/
    └── wavs/
        └── file3.wav
```

## Technical Details

- **Backend**: OpenAI Whisper
- **Frontend**: Streamlit
- **Audio Processing**: librosa, soundfile
- **Caching**: Model caching for faster subsequent loads
- **Export**: Plain text files with UTF-8 encoding

## License

This tool uses OpenAI Whisper, which is licensed under the MIT License.
