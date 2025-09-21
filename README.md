# OpenVoice AI Audio Converter Interface

A user-friendly web interface for OpenVoice AI voice conversion that allows you to upload audio files, preview them, convert voices, and download the results.

## Features

- 🎵 **Audio Upload**: Upload input audio and reference voice files
- 🎧 **Audio Preview**: Play uploaded audio files directly in the browser
- 🔄 **Voice Conversion**: Convert voice using OpenVoice AI
- 💾 **Download Results**: Download converted audio files
- ⚙️ **Device Selection**: Choose between CPU and GPU processing
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your browser and go to `http://localhost:8501`

## Usage

1. **Upload Files**: 
   - Upload your input audio file (the voice you want to convert)
   - Upload a reference voice file (the target voice style)

2. **Preview Audio**: 
   - Listen to both uploaded files using the built-in audio players

3. **Convert Voice**: 
   - Click the "Convert Voice" button to start the conversion process
   - Wait for the conversion to complete (may take a few minutes)

4. **Download Results**: 
   - Listen to the converted audio
   - Download the converted voice file

## Supported Audio Formats

- WAV
- MP3
- FLAC
- M4A

## Requirements

- Python 3.7+
- OpenVoice CLI
- PyTorch
- Streamlit
- SoundFile
- Librosa

## Notes

- For Intel Mac users, use CPU device selection
- For NVIDIA GPU users, CUDA is recommended for faster processing
- Large audio files may take longer to process
- Ensure you have sufficient disk space for temporary files

## Troubleshooting

If you encounter any issues:
1. Make sure all dependencies are properly installed
2. Check that your audio files are in supported formats
3. Ensure you have enough disk space for temporary files
4. Try using CPU device if CUDA fails
