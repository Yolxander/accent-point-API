# OpenVoice AI Audio Converter - Setup Guide

## Current Status

✅ **Interface Created**: Complete web interface with audio upload, preview, and download  
⚠️ **OpenVoice CLI**: Requires Python 3.11/3.12 (not compatible with Python 3.13)  
✅ **Demo Version**: Working demo with simulated audio processing  

## Quick Start (Demo Version)

The demo version works with your current Python 3.13 setup:

```bash
# Install basic dependencies
pip install -r requirements_simple.txt

# Run demo version
streamlit run app_demo.py
```

Open your browser to `http://localhost:8501`

## Full OpenVoice Setup (Recommended)

For real voice conversion, you need Python 3.11 or 3.12:

### Option 1: Using Conda (Recommended)

```bash
# Create new environment with Python 3.11
conda create -n openvoice python=3.11
conda activate openvoice

# Install OpenVoice CLI and dependencies
pip install openvoice-cli torch torchaudio

# Install interface dependencies
pip install streamlit librosa soundfile numpy scipy

# Run the full application
streamlit run app.py
```

### Option 2: Using pyenv

```bash
# Install Python 3.11
pyenv install 3.11.9
pyenv local 3.11.9

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Files Overview

- `app.py` - Full OpenVoice interface (requires Python 3.11/3.12)
- `app_demo.py` - Demo version (works with Python 3.13)
- `app_simple.py` - Simplified version with subprocess calls
- `requirements.txt` - Full dependencies including PyTorch
- `requirements_simple.txt` - Basic dependencies (no PyTorch)
- `convert.py` - Your original OpenVoice script
- `run_app.sh` - Launcher for full version
- `run_simple.sh` - Launcher for simple version

## Features

### ✅ Working Features (Demo Version)
- Audio file upload (WAV, MP3, FLAC, M4A)
- Audio preview with HTML5 players
- Simulated audio processing
- Download processed audio
- Responsive web interface
- Error handling

### 🔄 Full Features (with Python 3.11/3.12)
- All demo features plus:
- Real OpenVoice AI voice conversion
- PyTorch GPU acceleration
- High-quality voice transformation

## Troubleshooting

### Python 3.13 Compatibility Issues
- **Problem**: PyTorch doesn't support Python 3.13 yet
- **Solution**: Use Python 3.11 or 3.12, or use the demo version

### OpenVoice CLI Installation Issues
- **Problem**: Dependency conflicts
- **Solution**: Use a clean environment with Python 3.11/3.12

### Audio Format Issues
- **Problem**: Unsupported audio format
- **Solution**: Convert to WAV format first

## Usage Instructions

1. **Upload Files**: Upload input audio and reference voice
2. **Preview**: Listen to both files using built-in players
3. **Convert**: Click convert button (real conversion or demo)
4. **Download**: Download the processed audio file

## Next Steps

1. **For immediate testing**: Use `app_demo.py` with your current setup
2. **For production use**: Set up Python 3.11/3.12 environment and use `app.py`
3. **For development**: Modify the interface as needed

The interface is fully functional and ready to use once you have the proper Python environment set up!
