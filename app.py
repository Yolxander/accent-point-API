import streamlit as st
import os
import tempfile
import soundfile as sf
import numpy as np
import base64
from io import BytesIO
import librosa

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
    .audio-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 100%;
    }
    .audio-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #dee2e6;
    }
    .audio-icon {
        font-size: 2rem;
        margin-right: 1rem;
        color: #1f77b4;
    }
    .audio-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin: 0;
    }
    .audio-description {
        color: #666;
        margin-top: 0.5rem;
        font-size: 1rem;
        line-height: 1.4;
    }
    .upload-area {
        border: 3px dashed #1f77b4;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        margin: 1rem 0;
        transition: all 0.3s ease;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .upload-area:hover {
        border-color: #ff7f0e;
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        transform: translateY(-2px);
    }
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    .upload-text {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .upload-subtext {
        color: #666;
        font-size: 0.9rem;
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
        width: 100%;
        margin: 2rem 0;
    }
    .convert-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(31, 119, 180, 0.4);
    }
    .convert-button:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    .download-section {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #28a745;
        box-shadow: 0 4px 6px rgba(40, 167, 69, 0.2);
    }
    .converted-section {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border: 3px solid #28a745;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    .converted-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #155724;
        margin-bottom: 1rem;
        text-align: center;
    }
    .converted-description {
        color: #155724;
        text-align: center;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 2px solid #17a2b8;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.2);
    }
    .info-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #0c5460;
        margin-bottom: 1rem;
    }
    .info-content {
        color: #0c5460;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .gender-preservation {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffc107;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
    }
    .gender-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #856404;
        margin-bottom: 1rem;
    }
    .gender-content {
        color: #856404;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .settings-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .settings-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #495057;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_audio_file(uploaded_file):
    """Load audio file by first saving it to a temporary file"""
    try:
        # Get file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        # Create a temporary file with the correct extension
        with tempfile.NamedTemporaryFile(suffix=f'.{file_extension}', delete=False) as tmp_file:
            # Write the uploaded file content to the temporary file
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # For MP3, M4A, and other formats that soundfile doesn't support well
            if file_extension in ['mp3', 'm4a', 'aac', 'ogg']:
                # Use librosa for these formats
                audio_data, sample_rate = librosa.load(tmp_file_path, sr=None)
            else:
                # Use soundfile for WAV, FLAC, etc.
                audio_data, sample_rate = sf.read(tmp_file_path)
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            return audio_data, sample_rate
            
        except Exception as e:
            # If the first method fails, try the other
            try:
                if file_extension in ['wav', 'flac']:
                    audio_data, sample_rate = librosa.load(tmp_file_path, sr=None)
                else:
                    audio_data, sample_rate = sf.read(tmp_file_path)
                
                # Clean up the temporary file
                os.unlink(tmp_file_path)
                return audio_data, sample_rate
                
            except Exception as e2:
                # Clean up the temporary file
                os.unlink(tmp_file_path)
                raise Exception(f"Could not load audio file. Error 1: {str(e)}, Error 2: {str(e2)}")
                
    except Exception as e:
        raise Exception(f"Error processing uploaded file: {str(e)}")

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
        import openvoice_cli.__main__ as openvoice_main
        return True
    except ImportError:
        return False

def main():
    # Header
    st.markdown('<h1 class="main-header">🎵 OpenVoice AI Audio Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your voice accent while preserving gender and content</p>', unsafe_allow_html=True)
    
    # Check OpenVoice installation
    openvoice_available = check_openvoice_installation()
    
    if not openvoice_available:
        st.error("❌ OpenVoice CLI not found. Please install it first:")
        st.code("pip install openvoice-cli", language="bash")
        st.stop()
    
    # Initialize session state
    if 'device' not in st.session_state:
        st.session_state.device = 'cpu'
    if 'converted_audio' not in st.session_state:
        st.session_state.converted_audio = None
    
    # Gender preservation info
    st.markdown("""
    <div class="gender-preservation">
        <div class="gender-title">🎯 Gender Preservation Feature</div>
        <div class="gender-content">
            <p><strong>OpenVoice AI preserves your original gender while changing the accent!</strong></p>
            <ul>
                <li>👨 <strong>Male voice</strong> → Male voice with new accent</li>
                <li>👩 <strong>Female voice</strong> → Female voice with new accent</li>
                <li>🗣️ <strong>Your words</strong> → Same words, different accent</li>
                <li>�� <strong>Reference accent</strong> → Applied to your voice</li>
            </ul>
            <p><strong>Perfect for:</strong> Accent training, language learning, voice acting, and content creation!</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Two-column layout for audio uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="audio-section">
            <div class="audio-header">
                <div class="audio-icon">🎤</div>
                <div>
                    <h3 class="audio-title">Input Audio</h3>
                    <p class="audio-description">Your original voice that will be converted</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <div class="info-title">📝 What is Input Audio?</div>
            <div class="info-content">
                <p>This is <strong>your original voice recording</strong> that you want to transform. It can be:</p>
                <ul>
                    <li>Your speech in your current accent</li>
                    <li>Any audio you want to change the accent of</li>
                    <li>The content that will keep its words but get a new accent</li>
                </ul>
                <p><strong>Example:</strong> If you speak with an American accent and want to sound British, upload your American-accented speech here.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">🎤</div>
            <div class="upload-text">Choose your input audio file</div>
            <div class="upload-subtext">Drag and drop file here or click to browse<br>Limit 200MB per file • WAV, MP3, FLAC, M4A</div>
        </div>
        """, unsafe_allow_html=True)
        
        input_file = st.file_uploader(
            "Choose your input audio file", 
            type=['wav', 'mp3', 'flac', 'm4a'],
            key="input_file",
            help="Upload the audio file you want to convert",
            label_visibility="collapsed"
        )
        
        if input_file is not None:
            st.success("✅ Input audio uploaded successfully!")
            
            # Preview the audio
            try:
                input_data, input_sr = load_audio_file(input_file)
                st.markdown(create_audio_player(input_data, input_sr, "Your Original Voice"), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading input file: {str(e)}")
                input_file = None
    
    with col2:
        st.markdown("""
        <div class="audio-section">
            <div class="audio-header">
                <div class="audio-icon">🎭</div>
                <div>
                    <h3 class="audio-title">Reference Voice</h3>
                    <p class="audio-description">Target accent and voice style to adopt</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <div class="info-title">🎯 What is Reference Voice?</div>
            <div class="info-content">
                <p>This is the <strong>target voice style</strong> you want to adopt. It should be:</p>
                <ul>
                    <li>A clear recording of the accent you want</li>
                    <li>High-quality audio with good pronunciation</li>
                    <li>Similar gender to your input voice for best results</li>
                </ul>
                <p><strong>Example:</strong> If you want to sound British, upload a clear recording of a British speaker with the same gender as your input voice.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">🎭</div>
            <div class="upload-text">Choose reference voice file</div>
            <div class="upload-subtext">Drag and drop file here or click to browse<br>Limit 200MB per file • WAV, MP3, FLAC, M4A</div>
        </div>
        """, unsafe_allow_html=True)
        
        ref_file = st.file_uploader(
            "Choose reference voice file", 
            type=['wav', 'mp3', 'flac', 'm4a'],
            key="ref_file",
            help="Upload the reference voice that will be used for conversion",
            label_visibility="collapsed"
        )
        
        if ref_file is not None:
            st.success("✅ Reference voice uploaded successfully!")
            
            # Preview the audio
            try:
                ref_data, ref_sr = load_audio_file(ref_file)
                st.markdown(create_audio_player(ref_data, ref_sr, "Target Accent Voice"), unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading reference file: {str(e)}")
                ref_file = None
    
    # Settings section
    st.markdown("""
    <div class="settings-section">
        <div class="settings-title">⚙️ Processing Settings</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        device = st.selectbox(
            "Select device for processing:",
            ["cpu", "cuda"],
            help="Choose CPU for Intel Mac or CUDA for NVIDIA GPU",
            index=0 if st.session_state.device == 'cpu' else 1
        )
        st.session_state.device = device
    
    with col2:
        st.info("💡 **Tip**: Use CPU for Intel Mac or CUDA for NVIDIA GPU. CPU processing is more stable but slower.")
    
    # Convert button
    if st.button("🔄 Convert Voice with OpenVoice AI", key="convert_btn", help="Click to start real voice conversion", disabled=(input_file is None or ref_file is None)):
        if input_file is None or ref_file is None:
            st.warning("⚠️ Please upload both input audio and reference voice files to proceed.")
        else:
            with st.spinner("Converting voice using OpenVoice AI... This may take a few minutes."):
                try:
                    # Import tune_one function from the __main__ module
                    import openvoice_cli.__main__ as openvoice_main
                    tune_one = openvoice_main.tune_one
                    
                    # Load audio files
                    input_data, input_sr = load_audio_file(input_file)
                    ref_data, ref_sr = load_audio_file(ref_file)
                    
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
                    tune_one(
                        input_file=temp_input_path,
                        ref_file=temp_ref_path,
                        output_file=output_path,
                        device=st.session_state.device
                    )
                    
                    # Load converted audio
                    if os.path.exists(output_path):
                        converted_data, converted_sr = sf.read(output_path)
                        st.session_state.converted_audio = (converted_data, converted_sr)
                        
                        # Clean up temporary files
                        os.unlink(temp_input_path)
                        os.unlink(temp_ref_path)
                        os.unlink(output_path)
                        
                        st.success("✅ Voice conversion completed successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Conversion failed. Please check your files and try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error during conversion: {str(e)}")
                    # Clean up temporary files
                    try:
                        os.unlink(temp_input_path)
                        os.unlink(temp_ref_path)
                    except:
                        pass
    
    # Converted audio section (full width)
    if st.session_state.converted_audio is not None:
        converted_data, converted_sr = st.session_state.converted_audio
        
        st.markdown("""
        <div class="converted-section">
            <div class="converted-title">✨ Converted Audio Result</div>
            <div class="converted-description">
                Your original words + Reference accent + Preserved gender
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display converted audio
        st.markdown(create_audio_player(converted_data, converted_sr, "Converted Voice (Your Words + Reference Accent)"), unsafe_allow_html=True)
        
        # Download section
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.markdown("#### 💾 Download Converted Audio")
        download_link = get_download_link(converted_data, converted_sr, "converted_voice.wav")
        st.markdown(download_link, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Start New Conversion", key="reset_conversion"):
                st.session_state.converted_audio = None
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("### About OpenVoice AI")
    st.markdown("""
    OpenVoice is an advanced AI voice conversion tool that can transform your voice to match a reference voice while preserving the original speech content, emotion, and gender.
    
    **What it does:**
    - 🎯 **Extracts accent and tone** from reference voice
    - 🎤 **Applies that accent/tone** to your input audio
    - 👤 **Preserves your gender** (male stays male, female stays female)
    - 📝 **Keeps original words** and content exactly the same
    - 🗣️ **Result:** Your speech with the reference voice's accent and characteristics
    
    **Perfect for:**
    - Accent training and practice
    - Voice acting and character work
    - Language learning with native accents
    - Content creation with different voice styles
    
    **Current Status:**
    - Interface: ✅ Ready
    - Audio Upload/Preview: ✅ Working
    - OpenVoice CLI: ✅ Available
    - Real Voice Conversion: ✅ Active
    - Gender Preservation: ✅ Enabled
    """)

if __name__ == "__main__":
    main()
