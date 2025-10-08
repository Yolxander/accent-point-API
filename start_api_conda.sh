#!/bin/bash

# OpenVoice API Startup Script with Conda
echo "🎵 Starting OpenVoice API with Conda Environment"
echo "================================================"
echo ""

# Initialize conda
echo "🔧 Initializing conda..."
eval "$(conda shell.bash hook)"

# Activate the openvoice conda environment
echo "🔧 Activating conda environment 'openvoice'..."
conda activate openvoice

# Check if activation was successful
if [ $? -eq 0 ]; then
    echo "✅ Conda environment 'openvoice' activated successfully!"
    echo ""
    
    # Check if .env file exists, if not create it from env.example
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file from env.example..."
        cp env.example .env
        echo "✅ .env file created successfully!"
    else
        echo "✅ .env file already exists"
    fi
    
    # Create necessary directories
    echo "📁 Creating necessary directories..."
    mkdir -p uploads outputs temp processed
    
    # Set environment variables
    echo "🔧 Setting environment variables..."
    export ENVIRONMENT=development
    export HOST=0.0.0.0
    export PORT=8000
    export ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
    export OPENVOICE_DEVICE=cpu
    export MAX_FILE_SIZE=52428800
    export LOG_LEVEL=INFO
    
    echo ""
    echo "🚀 Starting OpenVoice API server..."
    echo "=================================="
    echo "API will be available at: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/api/v1/health"
    echo "ReDoc Documentation: http://localhost:8000/redoc"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the FastAPI server
    python main.py
    
else
    echo "❌ Failed to activate conda environment 'openvoice'"
    echo ""
    echo "Please make sure the environment exists and try again."
    echo ""
    echo "To create the environment, run:"
    echo "conda create -n openvoice python=3.9"
    echo "conda activate openvoice"
    echo "pip install -r requirements.txt"
    echo ""
    echo "Or use the regular virtual environment:"
    echo "./run.sh"
    exit 1
fi
