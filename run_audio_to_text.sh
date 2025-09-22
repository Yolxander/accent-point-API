#!/bin/bash

# Audio to Text App Launcher
echo "🎤 Starting Audio to Text Converter..."
echo ""

# Check if we're in the right directory
if [ ! -f "app_audio_to_text.py" ]; then
    echo "❌ Error: app_audio_to_text.py not found. Please run this script from the openvoice-project directory."
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

# Run the audio to text app
echo "🚀 Launching Audio to Text Converter..."
echo "   URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app_audio_to_text.py
