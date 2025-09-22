import streamlit as st
import subprocess
import sys
import os

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
    .app-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem;
        border: 3px solid #dee2e6;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        height: 100%;
        text-align: center;
    }
    .app-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    .app-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .app-description {
        color: #7f8c8d;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .app-features {
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
    .status-experimental {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    .navigation-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #90caf9;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = {
        'openvoice-cli': False,
        'whisper': False,
        'streamlit': True  # We know this is installed since we're running
    }
    
    try:
        import openvoice_cli
        dependencies['openvoice-cli'] = True
    except ImportError:
        pass
    
    try:
        import whisper
        dependencies['whisper'] = True
    except ImportError:
        pass
    
    return dependencies

def main():
    # Header
    st.markdown('<h1 class="main-header">🎵 OpenVoice AI Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Complete AI-powered voice processing and transcription toolkit</p>', unsafe_allow_html=True)
    
    # Check dependencies
    dependencies = check_dependencies()
    
    # Navigation info
    st.markdown("""
    <div class="navigation-info">
        <h3>🚀 Choose Your AI Tool</h3>
        <p>Select from our suite of AI-powered audio processing tools. Each app is designed for specific use cases and can work together seamlessly.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the apps
    col1, col2 = st.columns(2)
    
    with col1:
        # Voice Conversion App
        st.markdown("""
        <div class="app-card">
            <span class="app-icon">🎤➡️🎵</span>
            <div class="status-badge status-ready">✅ Ready</div>
            <div class="app-title">Voice Conversion</div>
            <div class="app-description">
                Transform your voice accent while preserving gender and content using OpenVoice AI technology.
            </div>
            <div class="app-features">
                <div class="feature-item">🎯 <strong>Accent Conversion:</strong> Change voice accent while keeping gender</div>
                <div class="feature-item">👨👩 <strong>Gender Preservation:</strong> Maintains original voice gender</div>
                <div class="feature-item">🎧 <strong>Real-time Preview:</strong> Listen before processing</div>
                <div class="feature-item">📁 <strong>Batch Processing:</strong> Process multiple audio files</div>
                <div class="feature-item">🔧 <strong>Advanced Settings:</strong> Customize conversion parameters</div>
            </div>
            <a href="?page=voice_conversion" class="launch-button">Launch Voice Conversion</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Audio to Text App
        whisper_status = "✅ Ready" if dependencies['whisper'] else "⚠️ Install Required"
        status_class = "status-ready" if dependencies['whisper'] else "status-experimental"
        
        st.markdown(f"""
        <div class="app-card">
            <span class="app-icon">🎵➡️📝</span>
            <div class="status-badge {status_class}">{whisper_status}</div>
            <div class="app-title">Audio to Text</div>
            <div class="app-description">
                Convert your processed audio files to text using OpenAI's Whisper AI transcription.
            </div>
            <div class="app-features">
                <div class="feature-item">🤖 <strong>AI Transcription:</strong> Powered by OpenAI Whisper</div>
                <div class="feature-item">🌍 <strong>Multi-language:</strong> Supports 99+ languages</div>
                <div class="feature-item">📊 <strong>Detailed Segments:</strong> Timestamped transcription</div>
                <div class="feature-item">💾 <strong>Export Options:</strong> Download as text files</div>
                <div class="feature-item">🎧 <strong>Audio Preview:</strong> Listen while transcribing</div>
            </div>
            <a href="?page=audio_to_text" class="launch-button">Launch Audio to Text</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Installation instructions
    if not dependencies['whisper']:
        st.markdown("### 📦 Installation Required")
        st.warning("The Audio to Text feature requires OpenAI Whisper. Install it with:")
        st.code("pip install openai-whisper", language="bash")
    
    # Workflow information
    st.markdown("### 🔄 Recommended Workflow")
    st.markdown("""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff;">
        <h4>💡 Complete Voice Processing Pipeline:</h4>
        <ol>
            <li><strong>Step 1:</strong> Use <strong>Voice Conversion</strong> to convert your audio files with different accents</li>
            <li><strong>Step 2:</strong> Use <strong>Audio to Text</strong> to transcribe the converted audio files</li>
            <li><strong>Step 3:</strong> Export the transcribed text for further use</li>
        </ol>
        <p><strong>Perfect for:</strong> Content creation, language learning, voice acting, accessibility, and more!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎵 OpenVoice AI Suite | Complete Voice Processing Toolkit</p>
        <p>Powered by OpenVoice AI and OpenAI Whisper</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
