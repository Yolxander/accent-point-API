#!/bin/bash

# OpenVoice AI Suite - 3 Pages Launcher
echo "🎵 Starting OpenVoice AI Suite (3 Pages)..."
echo ""

# Check if we're in the right directory
if [ ! -f "app_3pages.py" ]; then
    echo "❌ Error: app_3pages.py not found. Please run this script from the openvoice-project directory."
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

# Run the 3-page app
echo "🚀 Launching OpenVoice AI Suite (3 Pages)..."
echo "   - Main Menu: http://localhost:8501"
echo "   - Voice Conversion: http://localhost:8501/?page=voice_conversion"
echo "   - Text to Speech: http://localhost:8501/?page=text_to_speech"
echo "   - Audio to Text: http://localhost:8501/?page=audio_to_text"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app_3pages.py
