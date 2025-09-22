#!/bin/bash

# OpenVoice AI Suite Launcher
echo "🎵 Starting OpenVoice AI Suite..."
echo ""

# Check if we're in the right directory
if [ ! -f "launcher.py" ]; then
    echo "❌ Error: launcher.py not found. Please run this script from the openvoice-project directory."
    exit 1
fi

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: Conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi

# Activate openvoice environment
echo "🔄 Activating openvoice environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate openvoice

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Error: Streamlit not found. Please install it first:"
    echo "   conda activate openvoice"
    echo "   pip install streamlit"
    exit 1
fi

# Run the launcher
echo "🚀 Launching OpenVoice AI Suite..."
echo "   - Voice Conversion: http://localhost:8501/?page=voice_conversion"
echo "   - Audio to Text: http://localhost:8501/?page=audio_to_text"
echo "   - Main Menu: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run launcher.py
