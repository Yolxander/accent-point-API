# 🎵 OpenVoice AI Audio Converter - Complete Setup Guide

## ✅ Fixed Import Issue

The import error has been resolved! The correct import is:
```python
from openvoice_cli import tune_one
```

## 🚀 Complete Setup Process

### Step 1: Create Python 3.11 Environment

```bash
# Create new conda environment with Python 3.11
conda create -n openvoice python=3.11

# Activate the environment
conda activate openvoice
```

### Step 2: Install Dependencies

```bash
# Install PyTorch (CPU version for compatibility)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install OpenVoice CLI
pip install openvoice-cli

# Install interface dependencies
pip install streamlit librosa soundfile numpy scipy
```

### Step 3: Test Installation

```bash
# Test the installation
python test_openvoice.py
```

### Step 4: Run the Application

```bash
# Run the full OpenVoice interface
streamlit run app.py
```

## 📁 File Structure

- `app.py` - **Main application** with real OpenVoice conversion
- `app_demo.py` - Demo version (works with Python 3.13)
- `convert.py` - Your original script (now fixed)
- `test_openvoice.py` - Test script to verify installation
- `requirements.txt` - Full dependencies
- `requirements_simple.txt` - Basic dependencies (no PyTorch)

## 🎯 What Each Version Does

### `app.py` (Full Version)
- ✅ Real OpenVoice AI voice conversion
- ✅ Upload audio files
- ✅ Preview audio with HTML5 players
- ✅ Download converted audio
- ✅ CPU/GPU device selection
- ✅ Professional UI with gradients and animations

### `app_demo.py` (Demo Version)
- ✅ Simulated audio processing
- ✅ Same interface as full version
- ✅ Works with Python 3.13
- ⚠️ NOT real voice conversion (just audio mixing)

## 🔧 Troubleshooting

### Import Error Fixed
- **Problem**: `ImportError: cannot import name 'tune_one'`
- **Solution**: Use `from openvoice_cli import tune_one` (not from submodule)

### Python Version Issues
- **Problem**: PyTorch doesn't support Python 3.13
- **Solution**: Use Python 3.11 or 3.12 with conda

### Audio Format Issues
- **Problem**: Unsupported audio format
- **Solution**: Convert to WAV format first

## 🎉 Ready to Use!

Once you have the Python 3.11 environment set up:

1. **Activate environment**: `conda activate openvoice`
2. **Run app**: `streamlit run app.py`
3. **Open browser**: Go to `http://localhost:8501`
4. **Upload files**: Input audio + reference voice
5. **Convert**: Click "Convert Voice with OpenVoice AI"
6. **Download**: Get your converted audio file

## 🆚 Demo vs Full Version

| Feature | Demo Version | Full Version |
|---------|-------------|--------------|
| Python 3.13 | ✅ Works | ❌ Requires 3.11/3.12 |
| Real Voice Conversion | ❌ No | ✅ Yes |
| Audio Upload/Preview | ✅ Yes | ✅ Yes |
| Download Feature | ✅ Yes | ✅ Yes |
| Professional UI | ✅ Yes | ✅ Yes |
| AI Processing | ❌ Simulated | ✅ Real OpenVoice |

Choose the version that works best for your current setup!
