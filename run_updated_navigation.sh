#!/bin/bash

# OpenVoice AI Suite - Updated Navigation Launcher
echo "🎵 Starting OpenVoice AI Suite with Updated Navigation..."
echo ""

# Check if we're in the right directory
if [ ! -f "app_navigation.py" ]; then
    echo "❌ Error: app_navigation.py not found. Please run this script from the openvoice-project directory."
    exit 1
fi

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Error: Conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi

# Activate openvoice environment
echo "🔄 Activating openvoice environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate openvoice

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Error: Streamlit not found. Please install it first:"
    echo "   conda activate openvoice"
    echo "   pip install streamlit"
    exit 1
fi

# Run the updated navigation app
echo "🚀 Launching OpenVoice AI Suite with Updated Navigation..."
echo "   Main App: http://localhost:8501"
echo "   Landing Page: http://localhost:8501/?page=landing"
echo "   Audio to Audio: http://localhost:8501/?page=audio_to_audio"
echo "   Text to Audio: http://localhost:8501/?page=text_to_audio"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app_navigation.py
