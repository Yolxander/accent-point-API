import streamlit as st
import os
import tempfile
import soundfile as sf
import numpy as np
import base64
from io import BytesIO
import librosa
import whisper
import torch

# Page configuration
st.set_page_config(
    page_title="Audio to Text Converter",
    page_icon="🎤",
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
    .transcription-section {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
        border: 2px solid #c3e6cb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .transcription-text {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-top: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .model-info {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ffeaa7;
        margin-bottom: 1rem;
    }
    .file-list {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .file-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    .file-item:hover {
        background: #e9ecef;
    }
    .file-item.selected {
        background: #d1ecf1;
        border-color: #bee5eb;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-info {
        color: #17a2b8;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_whisper_model(model_size="base"):
    """Load Whisper model with caching"""
    try:
        model = whisper.load_model(model_size)
        return model
    except Exception as e:
        st.error(f"Error loading Whisper model: {str(e)}")
        return None

def get_audio_files():
    """Get list of available audio files from processed directory"""
    processed_dir = "processed"
    audio_files = []
    
    if os.path.exists(processed_dir):
        for folder in os.listdir(processed_dir):
            folder_path = os.path.join(processed_dir, folder)
            if os.path.isdir(folder_path):
                wavs_dir = os.path.join(folder_path, "wavs")
                if os.path.exists(wavs_dir):
                    for file in os.listdir(wavs_dir):
                        if file.endswith('.wav'):
                            audio_files.append({
                                'name': file,
                                'path': os.path.join(wavs_dir, file),
                                'folder': folder,
                                'full_name': f"{folder}/{file}"
                            })
    
    return audio_files

def transcribe_audio(model, audio_path, language=None):
    """Transcribe audio file using Whisper"""
    try:
        # Load audio
        audio = whisper.load_audio(audio_path)
        
        # Transcribe
        if language:
            result = model.transcribe(audio, language=language)
        else:
            result = model.transcribe(audio)
        
        return {
            'text': result['text'].strip(),
            'language': result.get('language', 'unknown'),
            'segments': result.get('segments', [])
        }
    except Exception as e:
        return {'error': str(e)}

def create_audio_player(audio_path):
    """Create HTML audio player for the audio file"""
    try:
        # Read audio file
        audio_data, sample_rate = sf.read(audio_path)
        
        # Convert to bytes
        buffer = BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        buffer.seek(0)
        
        # Encode to base64
        audio_bytes = buffer.read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        
        # Create HTML player
        audio_html = f"""
        <audio controls style="width: 100%; margin-top: 1rem;">
            <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
        """
        
        return audio_html
    except Exception as e:
        return f"<p>Error loading audio: {str(e)}</p>"

def main():
    # Header
    st.markdown('<h1 class="main-header">🎤 Audio to Text Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Convert your converted audio files to text using AI transcription</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_audio' not in st.session_state:
        st.session_state.selected_audio = None
    if 'transcription_result' not in st.session_state:
        st.session_state.transcription_result = None
    if 'whisper_model' not in st.session_state:
        st.session_state.whisper_model = None
    
    # Model selection
    st.markdown("### 🤖 AI Model Configuration")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        model_size = st.selectbox(
            "Select Whisper Model Size",
            ["tiny", "base", "small", "medium", "large"],
            index=1,
            help="Larger models are more accurate but slower"
        )
    
    with col2:
        language = st.selectbox(
            "Language (Optional)",
            ["Auto-detect", "English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Chinese", "Japanese"],
            help="Specify language for better accuracy"
        )
    
    # Load model
    if st.button("🔄 Load Model", type="primary"):
        with st.spinner(f"Loading Whisper {model_size} model..."):
            st.session_state.whisper_model = load_whisper_model(model_size)
            if st.session_state.whisper_model:
                st.success(f"✅ Whisper {model_size} model loaded successfully!")
            else:
                st.error("❌ Failed to load model")
    
    # Check if model is loaded
    if st.session_state.whisper_model is None:
        st.warning("⚠️ Please load a Whisper model first to start transcription.")
        st.stop()
    
    # Get available audio files
    audio_files = get_audio_files()
    
    if not audio_files:
        st.error("❌ No audio files found in the processed directory.")
        st.info("💡 Make sure you have converted some audio files using the main OpenVoice app first.")
        st.stop()
    
    # Audio file selection
    st.markdown("### 📁 Select Audio File")
    
    # Group files by folder
    folders = {}
    for file in audio_files:
        folder = file['folder']
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(file)
    
    # Display files in tabs
    if len(folders) > 1:
        tab_names = list(folders.keys())
        tabs = st.tabs(tab_names)
        
        for i, (folder, files) in enumerate(folders.items()):
            with tabs[i]:
                st.markdown(f"**Files in {folder}:**")
                for file in files:
                    if st.button(f"🎵 {file['name']}", key=f"select_{file['name']}", use_container_width=True):
                        st.session_state.selected_audio = file
                        st.session_state.transcription_result = None
                        st.rerun()
    else:
        # Single folder - display as list
        for file in audio_files:
            if st.button(f"🎵 {file['name']}", key=f"select_{file['name']}", use_container_width=True):
                st.session_state.selected_audio = file
                st.session_state.transcription_result = None
                st.rerun()
    
    # Display selected audio
    if st.session_state.selected_audio:
        st.markdown("### 🎧 Selected Audio")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**File:** {st.session_state.selected_audio['name']}")
            st.markdown(f"**Folder:** {st.session_state.selected_audio['folder']}")
            
            # Audio player
            audio_html = create_audio_player(st.session_state.selected_audio['path'])
            st.markdown(audio_html, unsafe_allow_html=True)
        
        with col2:
            # File info
            try:
                audio_data, sample_rate = sf.read(st.session_state.selected_audio['path'])
                duration = len(audio_data) / sample_rate
                st.markdown(f"**Duration:** {duration:.2f} seconds")
                st.markdown(f"**Sample Rate:** {sample_rate} Hz")
                st.markdown(f"**Channels:** {audio_data.shape[1] if len(audio_data.shape) > 1 else 1}")
            except Exception as e:
                st.error(f"Error reading audio info: {str(e)}")
        
        # Transcription button
        st.markdown("### 📝 Transcription")
        
        if st.button("🎯 Start Transcription", type="primary", use_container_width=True):
            with st.spinner("Transcribing audio... This may take a moment."):
                lang_code = None
                if language != "Auto-detect":
                    lang_map = {
                        "English": "en", "Spanish": "es", "French": "fr", "German": "de",
                        "Italian": "it", "Portuguese": "pt", "Russian": "ru",
                        "Chinese": "zh", "Japanese": "ja"
                    }
                    lang_code = lang_map.get(language)
                
                result = transcribe_audio(
                    st.session_state.whisper_model,
                    st.session_state.selected_audio['path'],
                    lang_code
                )
                
                st.session_state.transcription_result = result
        
        # Display transcription result
        if st.session_state.transcription_result:
            result = st.session_state.transcription_result
            
            if 'error' in result:
                st.error(f"❌ Transcription failed: {result['error']}")
            else:
                st.markdown("### ✅ Transcription Result")
                
                # Model info
                st.markdown(f"""
                <div class="model-info">
                    <strong>Model:</strong> Whisper {model_size} | 
                    <strong>Detected Language:</strong> {result['language']} | 
                    <strong>Segments:</strong> {len(result['segments'])}
                </div>
                """, unsafe_allow_html=True)
                
                # Transcription text
                st.markdown("**Transcribed Text:**")
                st.markdown(f"""
                <div class="transcription-text">
                    {result['text']}
                </div>
                """, unsafe_allow_html=True)
                
                # Copy to clipboard button
                if st.button("📋 Copy to Clipboard"):
                    st.code(result['text'], language="text")
                    st.success("✅ Text copied! You can now paste it anywhere.")
                
                # Download as text file
                text_file = BytesIO(result['text'].encode('utf-8'))
                st.download_button(
                    label="💾 Download as Text File",
                    data=text_file,
                    file_name=f"transcription_{st.session_state.selected_audio['name']}.txt",
                    mime="text/plain"
                )
                
                # Show segments if available
                if result['segments']:
                    with st.expander("📊 View Detailed Segments"):
                        for i, segment in enumerate(result['segments']):
                            st.markdown(f"**Segment {i+1}:** {segment['start']:.2f}s - {segment['end']:.2f}s")
                            st.markdown(f"*{segment['text']}*")
                            st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎤 Audio to Text Converter | Powered by OpenAI Whisper</p>
        <p>Convert your OpenVoice processed audio files to text with high accuracy</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
