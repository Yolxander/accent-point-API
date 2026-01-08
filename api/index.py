"""
Vercel serverless function entry point for FastAPI application
"""
import sys
import os

# Add the parent directory to the path so we can import from the app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Change to parent directory to ensure relative imports work
os.chdir(parent_dir)

# Import the FastAPI app from main.py
from main import app

# Export the app for Vercel (ASGI application)
handler = app

