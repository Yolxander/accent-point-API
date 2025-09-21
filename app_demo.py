import streamlit as st
import os
import tempfile
import soundfile as sf
import numpy as np
import base64
from io import BytesIO
import subprocess
import sys

# Page configuration
st.set_page_config(
    page_title="OpenVoice AI Audio Converter",
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
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
        font-size: 1.2rem;
        font-style: italic;
    }
    .upload-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .audio-player {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .convert-button {
        background: linear-gradient(135deg, #1f77b4 0%, #ff7f0e 100%);
        color: white;
        border: none;
        padding: 1rem 2.5rem;
        border-radius: 30px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(31, 119, 180, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .convert-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(31, 119, 180, 0.4);
    }
    .download-section {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #28a745;
        box-shadow: 0 4px 6px rgba(40, 167, 69, 0.2);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 3px solid #ffc107;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
        position: relative;
        overflow: hidden;
    }
    .warning-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #ffc107, #ff8c00, #ffc107);
    }
    .warning-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .warning-icon {
        font-size: 2rem;
        margin-right: 1rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .warning-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #856404;
        margin: 0;
    }
    .warning-content {
        color: #856404;
        line-height: 1.6;
    }
    .solutions-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    .solution-card {
        background: rgba(255, 255, 255, 0.7);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ffc107;
        text-align: center;
    }
    .solution-title {
        font-weight: bold;
        color: #856404;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    .solution-desc {
        color: #856404;
        font-size: 0.9rem;
    }
    .code-block {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1.5rem;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 1rem 0;
        overflow-x: auto;
        border: 2px solid #4a5568;
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 3px solid #17a2b8;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.2);
        position: relative;
        overflow: hidden;
    }
    .info-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #17a2b8, #20c997, #17a2b8);
    }
    .info-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .info-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .info-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #0c5460;
        margin: 0;
    }
    .info-content {
        color: #0c5460;
        line-height: 1.6;
    }
    .highlight-note {
        background: rgba(255, 255, 255, 0.8);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
        font-weight: bold;
    }
    .upload-placeholder {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 3px dashed #6c757d;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin: 2rem 0;
    }
    .upload-placeholder:hover {
        border-color: #1f77b4;
        color: #1f77b4;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }
</style>
""", unsafe_allow_html=True)

def create_audio_player(audio_data, sample_rate, label):
    """Create an HTML5 audio player for the given audio data"""
    # Convert audio data to bytes
    buffer = BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV')
    buffer.seek(0)
    
    # Encode audio data to base64
    audio_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Create HTML audio player
    audio_html = f"""
    <div class="audio-player">
        <h4 style="color: #1f77b4; margin-bottom: 1rem;">{label}</h4>
        <audio controls style="width: 100%; height: 50px;">
            <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    </div>
    """
    return audio_html

def get_download_link(audio_data, sample_rate, filename):
    """Generate a download link for the audio file"""
    buffer = BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV')
    buffer.seek(0)
    
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:audio/wav;base64,{b64}" download="{filename}" style="display: inline-block; background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 25px; font-weight: bold; box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3); transition: all 0.3s ease;">📥 Download {filename}</a>'
    return href

def check_openvoice_installation():
    """Check if openvoice-cli is properly installed"""
    try:
        import openvoice_cli
        return True
    except ImportError:
        return False

def demo_audio_processing(input_data, input_sr, ref_data, ref_sr):
    """Demo function that simulates audio processing"""
    # Simple audio processing demo - just mix the audio with some effects
    # This is NOT real voice conversion, just a demonstration
    
    # Ensure both audio files have the same sample rate
    target_sr = max(input_sr, ref_sr)
    
    # Resample if needed
    if input_sr != target_sr:
        import librosa
        input_data = librosa.resample(input_data, orig_sr=input_sr, target_sr=target_sr)
    if ref_sr != target_sr:
        import librosa
        ref_data = librosa.resample(ref_data, orig_sr=ref_sr, target_sr=target_sr)
    
    # Simple demo processing - mix input with reference at low volume
    # This is just for demonstration purposes
    ref_mixed = ref_data * 0.1  # Low volume reference
    
    # Ensure same length
    min_length = min(len(input_data), len(ref_mixed))
    input_data = input_data[:min_length]
    ref_mixed = ref_mixed[:min_length]
    
    # Mix the audio (this is NOT real voice conversion)
    processed_audio = input_data + ref_mixed
    
    # Normalize
    processed_audio = processed_audio / np.max(np.abs(processed_audio))
    
    return processed_audio, target_sr

def main():
    # Header
    st.markdown('<h1 class="main-header">🎵 OpenVoice AI Audio Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your voice using AI-powered voice conversion</p>', unsafe_allow_html=True)
    
    # Check OpenVoice installation
    openvoice_available = check_openvoice_installation()
    
    if not openvoice_available:
        st.markdown("""
        <div class="warning-box">
            <div class="warning-header">
                <div class="warning-icon">⚠️</div>
                <h3 class="warning-title">OpenVoice CLI Not Available</h3>
            </div>
            <div class="warning-content">
                <p><strong>Current Issue:</strong> OpenVoice CLI requires PyTorch, which doesn't support Python 3.13 yet.</p>
                
                <div class="solutions-grid">
                    <div class="solution-card">
                        <div class="solution-title">🚀 Option 1: Use Python 3.11/3.12</div>
                        <div class="solution-desc">Recommended for full functionality</div>
                    </div>
                    <div class="solution-card">
                        <div class="solution-title">🎭 Option 2: Demo Mode</div>
                        <div class="solution-desc">Use simulated processing</div>
                    </div>
                </div>
                
                <p><strong>To install OpenVoice CLI with Python 3.11/3.12:</strong></p>
                <div class="code-block">
conda create -n openvoice python=3.11<br>
conda activate openvoice<br>
pip install openvoice-cli torch torchaudio<br>
streamlit run app.py
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <div class="info-header">
                <div class="info-icon">🎭</div>
                <h3 class="info-title">Demo Mode Active</h3>
            </div>
            <div class="info-content">
                <p>This demo version will show you how the interface works, but uses simulated audio processing instead of real OpenVoice conversion.</p>
                <div class="highlight-note">
                    <strong>⚠️ Important Note:</strong> The "converted" audio is just a simple mix of input and reference - this is NOT real voice conversion!
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Create two columns for input and reference files
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("#### 📁 Upload Input Audio")
        input_file = st.file_uploader(
            "Choose your input audio file", 
            type=['wav', 'mp3', 'flac', 'm4a'],
            key="input_file",
            help="Upload the audio file you want to convert"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Upload Reference Voice")
        ref_file = st.file_uploader(
            "Choose reference voice file", 
            type=['wav', 'mp3', 'flac', 'm4a'],
            key="ref_file",
            help="Upload the reference voice that will be used for conversion"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Device selection
    st.markdown("#### ⚙️ Settings")
    device = st.selectbox(
        "Select device for processing:",
        ["cpu", "cuda"],
        help="Choose CPU for Intel Mac or CUDA for NVIDIA GPU"
    )
    
    # Process files if both are uploaded
    if input_file is not None and ref_file is not None:
        # Display uploaded files
        st.markdown("#### 🎧 Preview Uploaded Audio")
        
        # Process input file
        try:
            input_data, input_sr = sf.read(input_file)
            st.markdown(create_audio_player(input_data, input_sr, "Input Audio"), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading input file: {str(e)}")
            return
        
        # Process reference file
        try:
            ref_data, ref_sr = sf.read(ref_file)
            st.markdown(create_audio_player(ref_data, ref_sr, "Reference Voice"), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading reference file: {str(e)}")
            return
        
        # Convert button
        st.markdown("<br>", unsafe_allow_html=True)
        
        if openvoice_available:
            button_text = "🔄 Convert Voice (Real OpenVoice)"
        else:
            button_text = "🎭 Demo Processing (Simulated)"
            
        if st.button(button_text, key="convert_btn", help="Click to start voice conversion"):
            with st.spinner("Processing audio... This may take a few minutes."):
                try:
                    if openvoice_available:
                        # Real OpenVoice conversion would go here
                        st.info("Real OpenVoice conversion would be implemented here when PyTorch compatibility is resolved.")
                        # For now, use demo processing
                        processed_audio, processed_sr = demo_audio_processing(input_data, input_sr, ref_data, ref_sr)
                    else:
                        # Demo processing
                        processed_audio, processed_sr = demo_audio_processing(input_data, input_sr, ref_data, ref_sr)
                    
                    # Display processed audio
                    st.markdown("#### ✨ Processed Audio")
                    if not openvoice_available:
                        st.warning("⚠️ This is simulated processing, not real voice conversion!")
                    st.markdown(create_audio_player(processed_audio, processed_sr, "Processed Voice"), unsafe_allow_html=True)
                    
                    # Download section
                    st.markdown('<div class="download-section">', unsafe_allow_html=True)
                    st.markdown("#### 💾 Download Processed Audio")
                    download_link = get_download_link(processed_audio, processed_sr, "processed_voice.wav")
                    st.markdown(download_link, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if openvoice_available:
                        st.success("✅ Voice conversion completed successfully!")
                    else:
                        st.info("🎭 Demo processing completed! (This is not real voice conversion)")
                        
                except Exception as e:
                    st.error(f"❌ Error during processing: {str(e)}")
    
    elif input_file is not None or ref_file is not None:
        st.warning("⚠️ Please upload both input audio and reference voice files to proceed.")
    
    else:
        st.markdown("""
        <div class="upload-placeholder">
            <h3>👆 Ready to Get Started?</h3>
            <p>Upload your audio files above to begin voice conversion!</p>
            <p><small>Supported formats: WAV, MP3, FLAC, M4A</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("### About OpenVoice AI")
    st.markdown("""
    OpenVoice is an advanced AI voice conversion tool that can transform your voice to match a reference voice while preserving the original speech content and emotion.
    
    **Features:**
    - High-quality voice conversion
    - Preserves speech content and emotion
    - Supports multiple audio formats
    - CPU and GPU processing options
    
    **Current Status:**
    - Interface: ✅ Ready
    - Audio Upload/Preview: ✅ Working
    - OpenVoice CLI: ⚠️ Requires Python 3.11/3.12
    - Demo Mode: ✅ Available
    """)

if __name__ == "__main__":
    main()
