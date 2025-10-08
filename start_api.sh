#!/bin/bash

# OpenVoice API Startup Script
echo "🎵 Starting OpenVoice API"
echo "========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "📥 Installing dependencies..."
    ./venv/bin/pip install --upgrade pip setuptools wheel
    ./venv/bin/pip install -r requirements.txt
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs temp processed

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
echo "ReDoc Documentation: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server using uvicorn directly
./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload
