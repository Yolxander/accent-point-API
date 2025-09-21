#!/bin/bash

echo "🎵 Starting OpenVoice AI Audio Converter Interface..."
echo "Installing dependencies..."

# Install requirements
pip install -r requirements.txt

echo "Starting Streamlit application..."
echo "The app will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the application"

# Run the Streamlit app
streamlit run app.py
