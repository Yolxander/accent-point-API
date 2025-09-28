#!/bin/bash

# OpenVoice API Startup Script (Simplified)
echo "🎵 Starting OpenVoice API (Simplified)"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install build tools first
echo "🔧 Installing build tools..."
pip install setuptools wheel

# Install basic dependencies first
echo "📦 Installing basic dependencies..."
pip install fastapi uvicorn python-multipart pydantic pydantic-settings

# Install audio processing dependencies
echo "🎵 Installing audio processing dependencies..."
pip install librosa soundfile numpy scipy

# Install TTS dependencies
echo "🗣️ Installing TTS dependencies..."
pip install gtts pyttsx3

# Install other utilities
echo "🛠️ Installing utilities..."
pip install psutil aiofiles structlog colorama

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs temp

# Set environment variables
export ENVIRONMENT=development
export HOST=0.0.0.0
export PORT=8000
export ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
export OPENVOICE_DEVICE=cpu
export MAX_FILE_SIZE=52428800
export LOG_LEVEL=INFO

echo "🚀 Starting OpenVoice API server..."
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/api/v1/health"
echo ""

# Start the server
python main.py
