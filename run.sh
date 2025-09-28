#!/bin/bash

# OpenVoice API Startup Script
echo "🎵 Starting OpenVoice API"
echo "========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."

# First install setuptools and wheel
echo "🔧 Installing build tools..."
pip install --upgrade pip setuptools wheel

# Then install other dependencies
echo "📦 Installing main dependencies..."
pip install -r requirements.txt

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
