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
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .audio-player {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    .convert-button {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .convert-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .download-section {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #4caf50;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
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
        <h4>{label}</h4>
        <audio controls style="width: 100%;">
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
    href = f'<a href="data:audio/wav;base64,{b64}" download="{filename}" class="download-link">Download {filename}</a>'
    return href

def check_openvoice_installation():
    """Check if openvoice-cli is properly installed"""
    try:
        import openvoice_cli
        return True
    except ImportError:
        return False

def run_openvoice_conversion(input_path, ref_path, output_path, device="cpu"):
    """Run OpenVoice conversion using subprocess"""
    try:
        # Create a simple Python script to run the conversion
        conversion_script = f"""
import sys
sys.path.append('.')
from openvoice_cli import tune_one

tune_one(
    input_file="{input_path}",
    ref_file="{ref_path}",
    output_file="{output_path}",
    device="{device}"
)
print("Conversion completed successfully!")
"""
        
        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
            script_file.write(conversion_script)
            script_path = script_file.name
        
        # Run the conversion
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=300)
        
        # Clean up
        os.unlink(script_path)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, "Conversion timed out after 5 minutes"
    except Exception as e:
        return False, str(e)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎵 OpenVoice AI Audio Converter</h1>', unsafe_allow_html=True)
    st.markdown("### Transform your voice using AI-powered voice conversion")
    
    # Check OpenVoice installation
    if not check_openvoice_installation():
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ OpenVoice CLI Not Found</h4>
            <p>OpenVoice CLI is not installed. Please install it first:</p>
            <code>pip install openvoice-cli</code>
            <p>Note: This may require PyTorch which has compatibility issues with Python 3.13. 
            Consider using Python 3.11 or 3.12 for better compatibility.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.stop()
    
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
        if st.button("🔄 Convert Voice", key="convert_btn", help="Click to start voice conversion"):
            with st.spinner("Converting voice... This may take a few minutes."):
                try:
                    # Create temporary files
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_input:
                        sf.write(temp_input.name, input_data, input_sr)
                        temp_input_path = temp_input.name
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_ref:
                        sf.write(temp_ref.name, ref_data, ref_sr)
                        temp_ref_path = temp_ref.name
                    
                    # Create output file path
                    output_path = "converted_output.wav"
                    
                    # Run OpenVoice conversion
                    success, message = run_openvoice_conversion(
                        temp_input_path, temp_ref_path, output_path, device
                    )
                    
                    if success:
                        # Load converted audio
                        if os.path.exists(output_path):
                            converted_data, converted_sr = sf.read(output_path)
                            
                            # Display converted audio
                            st.markdown("#### ✨ Converted Audio")
                            st.markdown(create_audio_player(converted_data, converted_sr, "Converted Voice"), unsafe_allow_html=True)
                            
                            # Download section
                            st.markdown('<div class="download-section">', unsafe_allow_html=True)
                            st.markdown("#### 💾 Download Converted Audio")
                            download_link = get_download_link(converted_data, converted_sr, "converted_voice.wav")
                            st.markdown(download_link, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Clean up temporary files
                            os.unlink(temp_input_path)
                            os.unlink(temp_ref_path)
                            os.unlink(output_path)
                            
                            st.success("✅ Voice conversion completed successfully!")
                        else:
                            st.error("❌ Conversion failed. Output file not found.")
                    else:
                        st.error(f"❌ Conversion failed: {message}")
                        
                except Exception as e:
                    st.error(f"❌ Error during conversion: {str(e)}")
                    # Clean up temporary files
                    try:
                        os.unlink(temp_input_path)
                        os.unlink(temp_ref_path)
                    except:
                        pass
    
    elif input_file is not None or ref_file is not None:
        st.warning("⚠️ Please upload both input audio and reference voice files to proceed.")
    
    else:
        st.info("👆 Please upload your audio files to get started!")
    
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
    
    **Note:** If you encounter PyTorch compatibility issues with Python 3.13, consider using Python 3.11 or 3.12.
    """)

if __name__ == "__main__":
    main()
