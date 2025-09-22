import streamlit as st
import os
import tempfile
import soundfile as sf
import numpy as np
import base64
from io import BytesIO
import librosa
import subprocess
import sys

# Page configuration
st.set_page_config(
    page_title="OpenVoice AI Suite",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
        font-size: 1.3rem;
        font-style: italic;
    }
    .page-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem;
        border: 3px solid #dee2e6;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        height: 100%;
        text-align: center;
        cursor: pointer;
    }
    .page-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    .page-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
    }
    .page-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .page-description {
        color: #7f8c8d;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .page-features {
        text-align: left;
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border: 1px solid #e9ecef;
    }
    .feature-item {
        margin: 0.5rem 0;
        color: #495057;
    }
    .launch-button {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
        display: inline-block;
    }
    .launch-button:hover {
        background: linear-gradient(45deg, #0056b3, #004085);
        transform: scale(1.05);
        text-decoration: none;
        color: white;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .status-ready {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .workflow-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #90caf9;
        text-align: center;
    }
    .workflow-step {
        display: inline-block;
        margin: 0.5rem;
        padding: 0.5rem 1rem;
        background: white;
        border-radius: 20px;
        border: 2px solid #007bff;
        font-weight: 600;
        color: #007bff;
    }
    .workflow-arrow {
        font-size: 1.5rem;
        color: #007bff;
        margin: 0 0.5rem;
    }
    .back-button {
        background: #6c757d;
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        text-decoration: none;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .back-button:hover {
        background: #5a6268;
        text-decoration: none;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def check_openvoice_installation():
    """Check if OpenVoice CLI is installed"""
    try:
        import openvoice_cli
        return True
    except ImportError:
        return False

def check_tts_installation():
    """Check if TTS libraries are available"""
    try:
        import torch
        import torchaudio
        return True
    except ImportError:
        return False

def main():
    # Get the page parameter from URL
    query_params = st.query_params
    page = query_params.get("page", "landing")
    
    if page == "voice_conversion":
        show_voice_conversion_page()
    elif page == "text_to_speech":
        show_text_to_speech_page()
    elif page == "audio_to_text":
        show_audio_to_text_page()
    else:
        show_landing_page()

def show_landing_page():
    """Show the main landing page"""
    st.markdown('<h1 class="main-header">🎵 OpenVoice AI Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Complete AI-powered voice processing and synthesis toolkit</p>', unsafe_allow_html=True)
    
    # Check dependencies
    openvoice_available = check_openvoice_installation()
    tts_available = check_tts_installation()
    
    # Workflow information
    st.markdown("""
    <div class="workflow-info">
        <h3>🔄 Complete Voice Processing Workflow</h3>
        <div>
            <span class="workflow-step">1. Voice Conversion</span>
            <span class="workflow-arrow">→</span>
            <span class="workflow-step">2. Text to Speech</span>
            <span class="workflow-arrow">→</span>
            <span class="workflow-step">3. Final Audio</span>
        </div>
        <p>Transform your voice accent, then create new audio with custom text using your converted voice!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for the pages
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Voice Conversion Page
        st.markdown("""
        <div class="page-card" onclick="window.location.href='?page=voice_conversion'">
            <span class="page-icon">🎤➡️🎵</span>
            <div class="status-badge status-ready">✅ Ready</div>
            <div class="page-title">Voice Conversion</div>
            <div class="page-description">
                Transform your voice accent while preserving gender and content using OpenVoice AI technology.
            </div>
            <div class="page-features">
                <div class="feature-item">🎯 <strong>Accent Conversion:</strong> Change voice accent while keeping gender</div>
                <div class="feature-item">👨👩 <strong>Gender Preservation:</strong> Maintains original voice gender</div>
                <div class="feature-item">🎧 <strong>Real-time Preview:</strong> Listen before processing</div>
                <div class="feature-item">📁 <strong>Batch Processing:</strong> Process multiple audio files</div>
            </div>
            <a href="?page=voice_conversion" class="launch-button">Launch Voice Conversion</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Text to Speech Page
        tts_status = "✅ Ready" if tts_available else "⚠️ Install Required"
        status_class = "status-ready" if tts_available else "status-experimental"
        
        st.markdown(f"""
        <div class="page-card" onclick="window.location.href='?page=text_to_speech'">
            <span class="page-icon">📝➡️🎵</span>
            <div class="status-badge {status_class}">{tts_status}</div>
            <div class="page-title">Text to Speech</div>
            <div class="page-description">
                Create new audio using your converted voice files and custom text input.
            </div>
            <div class="page-features">
                <div class="feature-item">🎤 <strong>Voice Cloning:</strong> Use your converted voice</div>
                <div class="feature-item">📝 <strong>Custom Text:</strong> Type any text to convert</div>
                <div class="feature-item">🎧 <strong>Audio Preview:</strong> Listen before downloading</div>
                <div class="feature-item">💾 <strong>Export Options:</strong> Download as audio files</div>
            </div>
            <a href="?page=text_to_speech" class="launch-button">Launch Text to Speech</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Audio to Text Page (existing)
        st.markdown("""
        <div class="page-card" onclick="window.location.href='?page=audio_to_text'">
            <span class="page-icon">🎵➡️📝</span>
            <div class="status-badge status-ready">✅ Ready</div>
            <div class="page-title">Audio to Text</div>
            <div class="page-description">
                Convert your processed audio files to text using AI transcription.
            </div>
            <div class="page-features">
                <div class="feature-item">🤖 <strong>AI Transcription:</strong> Powered by OpenAI Whisper</div>
                <div class="feature-item">🌍 <strong>Multi-language:</strong> Supports 99+ languages</div>
                <div class="feature-item">📊 <strong>Detailed Segments:</strong> Timestamped transcription</div>
                <div class="feature-item">💾 <strong>Export Options:</strong> Download as text files</div>
            </div>
            <a href="?page=audio_to_text" class="launch-button">Launch Audio to Text</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Installation instructions
    if not tts_available:
        st.markdown("### 📦 Installation Required")
        st.warning("The Text to Speech feature requires additional dependencies. Install with:")
        st.code("pip install torch torchaudio", language="bash")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎵 OpenVoice AI Suite | Complete Voice Processing Toolkit</p>
        <p>Powered by OpenVoice AI, PyTorch, and OpenAI Whisper</p>
    </div>
    """, unsafe_allow_html=True)

def show_voice_conversion_page():
    """Show the voice conversion page (existing functionality)"""
    # Back button
    st.markdown('<a href="?page=landing" class="back-button">← Back to Main Menu</a>', unsafe_allow_html=True)
    
    # Import and run the existing voice conversion app
    try:
        # Read the existing app.py and extract the main function
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Execute the app content in a new namespace
        namespace = {}
        exec(app_content, namespace)
        
        # Call the main function
        if 'main' in namespace:
            namespace['main']()
        else:
            st.error("Could not find main function in app.py")
    except Exception as e:
        st.error(f"Error loading voice conversion app: {e}")
        st.info("Make sure app.py exists in the current directory.")

def show_text_to_speech_page():
    """Show the text to speech page"""
    # Back button
    st.markdown('<a href="?page=landing" class="back-button">← Back to Main Menu</a>', unsafe_allow_html=True)
    
    # Import and run the text to speech app
    try:
        # Read the text to speech app and extract the main function
        with open('app_text_to_speech.py', 'r') as f:
            tts_content = f.read()
        
        # Execute the app content in a new namespace
        namespace = {}
        exec(tts_content, namespace)
        
        # Call the main function
        if 'main' in namespace:
            namespace['main']()
        else:
            st.error("Could not find main function in app_text_to_speech.py")
    except Exception as e:
        st.error(f"Error loading text to speech app: {e}")
        st.info("Make sure app_text_to_speech.py exists in the current directory.")

def show_audio_to_text_page():
    """Show the audio to text page"""
    # Back button
    st.markdown('<a href="?page=landing" class="back-button">← Back to Main Menu</a>', unsafe_allow_html=True)
    
    # Import and run the audio to text app
    try:
        # Read the audio to text app and extract the main function
        with open('app_audio_to_text.py', 'r') as f:
            att_content = f.read()
        
        # Execute the app content in a new namespace
        namespace = {}
        exec(att_content, namespace)
        
        # Call the main function
        if 'main' in namespace:
            namespace['main']()
        else:
            st.error("Could not find main function in app_audio_to_text.py")
    except Exception as e:
        st.error(f"Error loading audio to text app: {e}")
        st.info("Make sure app_audio_to_text.py exists in the current directory.")

if __name__ == "__main__":
    main()
