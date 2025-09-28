#!/bin/bash

echo "🎵 Starting OpenVoice AI Suite (2 Pages) with Conda"
echo "=================================================="
echo ""
echo "📋 Features available:"
echo "  1. 🏠 Welcome Page - Overview of all features"
echo "  2. 🎤➡️🎵 Audio to Audio - Voice accent conversion"
echo "  3. 📝➡️🎵 Text to Audio - Convert text using uploaded voice"
echo ""
echo "🔧 Activating conda environment 'openvoice'..."
echo ""

# Initialize conda
eval "$(conda shell.bash hook)"

# Activate the openvoice conda environment
conda activate openvoice

# Check if activation was successful
if [ $? -eq 0 ]; then
    echo "✅ Conda environment 'openvoice' activated successfully!"
    echo ""
    echo "🚀 Launching Streamlit app..."
    echo ""
    
    # Run the Streamlit app
    streamlit run app_3pages.py --server.port 8501 --server.address 0.0.0.0
else
    echo "❌ Failed to activate conda environment 'openvoice'"
    echo "Please make sure the environment exists and try again."
    echo ""
    echo "To create the environment, run:"
    echo "conda create -n openvoice python=3.9"
    echo "conda activate openvoice"
    echo "pip install openvoice-cli"
    exit 1
fi
