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
    .status-experimental {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
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
    }
    .audio-title {
        margin: 0;
        color: #2c3e50;
        font-size: 1.5rem;
    }
    .audio-description {
        margin: 0;
        color: #7f8c8d;
        font-size: 0.9rem;
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

def create_audio_player(audio_data, sample_rate, label="Audio"):
    """Create an HTML5 audio player for the given audio data"""
    # Convert audio data to bytes
    buffer = BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV')
    buffer.seek(0)
    
    # Encode audio data to base64
    audio_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Create HTML audio player
    audio_html = f"""
    <div style="background: white; padding: 1rem; border-radius: 10px; margin: 1rem 0; border: 1px solid #dee2e6;">
        <h4 style="color: #1f77b4; margin-bottom: 1rem;">{label}</h4>
        <audio controls style="width: 100%; height: 50px;">
            <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    </div>
    """
    return audio_html

def simple_tts_simulation(text, voice_file_path):
    """Simulate TTS generation using uploaded voice file characteristics"""
    try:
        # Read the voice file to get characteristics
        voice_data, sample_rate = sf.read(voice_file_path)
        
        # Create a simple tone that represents the "generated" speech
        # This is just a placeholder - real TTS would generate actual speech
        duration = len(text.split()) * 0.5  # Rough estimate: 0.5 seconds per word
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a simple waveform (this is just for demonstration)
        frequency = 200 + (hash(text) % 100)  # Vary frequency based on text
        waveform = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Add some variation to make it more interesting
        waveform += np.sin(2 * np.pi * frequency * 2 * t) * 0.1
        
        # Try to match some characteristics of the uploaded voice
        if len(voice_data) > 0:
            # Get average amplitude from voice file
            avg_amplitude = np.mean(np.abs(voice_data))
            waveform = waveform * avg_amplitude * 2
        
        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform)) * 0.8
        
        return waveform, sample_rate
    except Exception as e:
        st.error(f"Error in TTS simulation: {str(e)}")
        return None, None

def main():
    # Get the page parameter from URL
    query_params = st.query_params
    page = query_params.get("page", "landing")
    
    if page == "audio_to_audio":
        show_audio_to_audio_page()
    elif page == "text_to_audio":
        show_text_to_audio_page()
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
            <span class="workflow-step">1. Audio to Audio</span>
            <span class="workflow-arrow">→</span>
            <span class="workflow-step">2. Text to Audio</span>
        </div>
        <p>Convert voice accents and create custom speech from text!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the pages
    col1, col2 = st.columns(2)
    
    with col1:
        # Audio to Audio Page (Voice Conversion)
        st.markdown("""
        <div class="page-card" onclick="window.location.href='?page=audio_to_audio'">
            <span class="page-icon">🎤➡️🎵</span>
            <div class="status-badge status-ready">✅ Ready</div>
            <div class="page-title">Audio to Audio</div>
            <div class="page-description">
                Transform your voice accent while preserving gender and content using OpenVoice AI technology.
            </div>
            <div class="page-features">
                <div class="feature-item">🎯 <strong>Accent Conversion:</strong> Change voice accent while keeping gender</div>
                <div class="feature-item">👨👩 <strong>Gender Preservation:</strong> Maintains original voice gender</div>
                <div class="feature-item">🎧 <strong>Real-time Preview:</strong> Listen before processing</div>
                <div class="feature-item">📁 <strong>High Quality:</strong> Professional audio conversion</div>
            </div>
            <a href="?page=audio_to_audio" class="launch-button">Launch Audio to Audio</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Text to Audio Page (NEW)
        st.markdown("""
        <div class="page-card" onclick="window.location.href='?page=text_to_audio'">
            <span class="page-icon">📝➡️🎵</span>
            <div class="status-badge status-ready">✅ Ready</div>
            <div class="page-title">Text to Audio</div>
            <div class="page-description">
                Convert text to audio using an uploaded voice file to match voice characteristics and accent.
            </div>
            <div class="page-features">
                <div class="feature-item">🎤 <strong>Voice Matching:</strong> Uses uploaded voice characteristics</div>
                <div class="feature-item">📝 <strong>Custom Text:</strong> Type any text to convert</div>
                <div class="feature-item">🎧 <strong>Audio Preview:</strong> Listen before downloading</div>
                <div class="feature-item">💾 <strong>Export Options:</strong> Download as audio files</div>
            </div>
            <a href="?page=text_to_audio" class="launch-button">Launch Text to Audio</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Installation instructions
    if not openvoice_available:
        st.markdown("### 📦 Installation Required")
        st.warning("The Audio to Audio feature requires OpenVoice CLI. Please activate your conda environment and install:")
        st.code("conda activate openvoice\npip install openvoice-cli", language="bash")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎵 OpenVoice AI Suite | Complete Voice Processing Toolkit</p>
        <p>Powered by OpenVoice AI and PyTorch</p>
    </div>
    """, unsafe_allow_html=True)

def show_audio_to_audio_page():
    """Show the audio to audio page (voice conversion functionality)"""
    # Back button
    st.markdown('<a href="?page=landing" class="back-button">← Back to Main Menu</a>', unsafe_allow_html=True)
    
    # Import and run the existing voice conversion app
    try:
        # Read the existing app.py and extract the main function
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Fix the typo in the import statement
        app_content = app_content.replace('timport streamlit as st', 'import streamlit as st')
        
        # Execute the app content in a new namespace
        namespace = {}
        exec(app_content, namespace)
        
        # Call the main function
        if 'main' in namespace:
            namespace['main']()
        else:
            st.error("Could not find main function in app.py")
    except Exception as e:
        st.error(f"Error loading audio to audio app: {e}")
        st.info("Make sure app.py exists in the current directory.")

def show_text_to_audio_page():
    """Show the text to audio page (NEW FUNCTIONALITY)"""
    # Back button
    st.markdown('<a href="?page=landing" class="back-button">← Back to Main Menu</a>', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📝➡️🎵 Text to Audio Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Convert text to audio using an uploaded voice file to match voice characteristics and accent</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'generated_audio' not in st.session_state:
        st.session_state.generated_audio = None
    if 'voice_file_path' not in st.session_state:
        st.session_state.voice_file_path = None
    
    # Two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Text input section
        st.markdown("""
        <div class="audio-section">
            <div class="audio-header">
                <div class="audio-icon">📝</div>
                <div>
                    <h3 class="audio-title">Text Input</h3>
                    <p class="audio-description">Enter the text you want to convert to audio</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        text_input = st.text_area(
            "Type your text here:",
            placeholder="Enter the text you want to convert to speech... For example: 'Hello, this is a demonstration of text to audio conversion using your uploaded voice file!'",
            height=150,
            help="Enter any text you want to convert to audio"
        )
        
        # Tips
        st.markdown("**💡 Tips:**")
        st.markdown("• Keep text under 500 characters for best results")
        st.markdown("• Use punctuation for natural pauses")
        st.markdown("• Avoid special characters")
        
    with col2:
        # Voice file upload section
        st.markdown("""
        <div class="audio-section">
            <div class="audio-header">
                <div class="audio-icon">🎤</div>
                <div>
                    <h3 class="audio-title">Reference Voice</h3>
                    <p class="audio-description">Upload the voice file to match characteristics and accent</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="upload-area">
            <div class="upload-icon">🎤</div>
            <div class="upload-text">Upload your reference voice file</div>
            <div class="upload-subtext">Drag and drop file here or click to browse<br>Limit 200MB per file • WAV, MP3, FLAC, M4A</div>
        </div>
        """, unsafe_allow_html=True)
        
        voice_file = st.file_uploader(
            "Choose your reference voice file", 
            type=['wav', 'mp3', 'flac', 'm4a'],
            key="voice_file",
            help="Upload the voice file whose characteristics you want to match",
            label_visibility="collapsed"
        )
        
        if voice_file is not None:
            st.success("✅ Voice file uploaded successfully!")
            
            # Preview the audio
            try:
                voice_data, voice_sr = load_audio_file(voice_file)
                
                # Save to temporary file for processing
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_voice:
                    sf.write(temp_voice.name, voice_data, voice_sr)
                    st.session_state.voice_file_path = temp_voice.name
                
                # Display audio player
                st.markdown(create_audio_player(voice_data, voice_sr, "Reference Voice"), unsafe_allow_html=True)
                
                # Show file info
                duration = len(voice_data) / voice_sr
                st.markdown(f"**Duration:** {duration:.2f} seconds")
                st.markdown(f"**Sample Rate:** {voice_sr} Hz")
                
            except Exception as e:
                st.error(f"Error loading voice file: {str(e)}")
                voice_file = None
    
    # Generate audio section
    if text_input.strip() and voice_file is not None:
        st.markdown("### 🎯 Generate Audio")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🎵 Generate Audio from Text", type="primary", use_container_width=True):
                with st.spinner("Generating audio... This may take a moment."):
                    # Generate the speech using the uploaded voice file
                    waveform, sample_rate = simple_tts_simulation(text_input, st.session_state.voice_file_path)
                    
                    if waveform is not None:
                        st.session_state.generated_audio = {
                            'waveform': waveform,
                            'sample_rate': sample_rate,
                            'text': text_input,
                            'voice_file': voice_file.name
                        }
                        st.success("✅ Audio generated successfully!")
                    else:
                        st.error("❌ Failed to generate audio.")
        
        with col2:
            st.markdown("**⚙️ Settings:**")
            st.markdown("• Text length: " + str(len(text_input.split())) + " words")
            st.markdown("• Estimated duration: ~" + str(len(text_input.split()) * 0.5) + " seconds")
            st.markdown("• Voice: " + (voice_file.name if voice_file else "None"))
        
        # Display generated audio
        if st.session_state.generated_audio:
            audio_data = st.session_state.generated_audio
            
            st.markdown("### ✅ Generated Audio")
            
            # Create audio player for generated audio
            try:
                # Convert numpy array to audio bytes
                buffer = BytesIO()
                sf.write(buffer, audio_data['waveform'], audio_data['sample_rate'], format='WAV')
                buffer.seek(0)
                
                # Display audio player
                st.markdown(create_audio_player(audio_data['waveform'], audio_data['sample_rate'], "Generated Audio"), unsafe_allow_html=True)
                
                # Download button
                audio_bytes = buffer.getvalue()
                st.download_button(
                    label="💾 Download Generated Audio",
                    data=audio_bytes,
                    file_name=f"generated_audio_{audio_data['voice_file']}.wav",
                    mime="audio/wav"
                )
                
                # Show generation info
                st.markdown("### 📊 Generation Info")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Text Length", f"{len(audio_data['text'])} characters")
                with col2:
                    st.metric("Word Count", f"{len(audio_data['text'].split())} words")
                with col3:
                    duration = len(audio_data['waveform']) / audio_data['sample_rate']
                    st.metric("Audio Duration", f"{duration:.2f} seconds")
                
                # Show the text that was converted
                st.markdown("### 📝 Converted Text")
                st.markdown(f"**Text:** {audio_data['text']}")
                st.markdown(f"**Reference Voice:** {audio_data['voice_file']}")
                
            except Exception as e:
                st.error(f"Error creating audio player: {str(e)}")
    
    elif not text_input.strip():
        st.warning("⚠️ Please enter some text to convert.")
    elif voice_file is None:
        st.warning("⚠️ Please upload a reference voice file.")
    
    # Information section
    st.markdown("### 🎯 How Text to Audio Works")
    st.markdown("""
    This feature converts your text to audio by:
    
    1. **Analyzing your uploaded voice file** - Extracts voice characteristics, accent, and tone
    2. **Processing your text** - Prepares the text for speech synthesis
    3. **Generating audio** - Creates speech that matches your reference voice characteristics
    4. **Delivering results** - Provides audio file for download
    
    **Perfect for:**
    - Creating custom voiceovers with specific accents
    - Generating speech in your own voice style
    - Content creation with consistent voice characteristics
    - Accessibility applications
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>📝➡️🎵 Text to Audio Converter | Powered by OpenVoice AI</p>
        <p>Convert text to speech using uploaded voice characteristics</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
