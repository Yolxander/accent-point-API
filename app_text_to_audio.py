import streamlit as st
import os
import tempfile
import soundfile as sf
import numpy as np
import base64
from io import BytesIO
import librosa
import torch
import subprocess
import json

# Page configuration
st.set_page_config(
    page_title="Text to Audio Converter",
    page_icon="📝➡️🎵",
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
    .text-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .text-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #dee2e6;
    }
    .text-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .text-title {
        margin: 0;
        color: #2c3e50;
        font-size: 1.5rem;
    }
    .text-description {
        margin: 0;
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    .reference-section {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #c3e6cb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .reference-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #c3e6cb;
    }
    .reference-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .reference-title {
        margin: 0;
        color: #2c3e50;
        font-size: 1.5rem;
    }
    .reference-description {
        margin: 0;
        color: #7f8c8d;
        font-size: 0.9rem;
    }
    .result-section {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
        border: 2px solid #ffeaa7;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .result-text {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-top: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .accent-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #bee5eb;
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
    .text-input {
        min-height: 200px;
        font-size: 1.1rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

def get_reference_audio_files():
    """Get list of available reference audio files from processed directory"""
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

def text_to_speech_with_accent(text, reference_audio_path, output_path):
    """Convert text to speech with accent from reference audio"""
    try:
        # This is a placeholder function - you would integrate with your TTS system here
        # For now, we'll create a simple implementation
        
        # Check if reference audio exists
        if not os.path.exists(reference_audio_path):
            return {"error": "Reference audio file not found"}
        
        # For demonstration, we'll copy the reference audio and add a note
        # In a real implementation, you would use a TTS system that can mimic accents
        
        # Read reference audio
        reference_audio, sample_rate = sf.read(reference_audio_path)
        
        # Create a simple tone as placeholder (in real implementation, this would be TTS)
        duration = len(reference_audio) / sample_rate
        t = np.linspace(0, duration, int(sample_rate * duration))
        tone = 0.1 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
        
        # Mix with reference audio characteristics
        if len(reference_audio.shape) > 1:
            reference_audio = reference_audio[:, 0]  # Take first channel
        
        # Normalize and mix
        reference_normalized = reference_audio / np.max(np.abs(reference_audio))
        tone_normalized = tone / np.max(np.abs(tone))
        
        # Create output audio (placeholder - real TTS would generate this)
        output_audio = 0.3 * tone_normalized + 0.7 * reference_normalized
        
        # Save output
        sf.write(output_path, output_audio, sample_rate)
        
        return {
            "success": True,
            "output_path": output_path,
            "duration": duration,
            "sample_rate": sample_rate
        }
        
    except Exception as e:
        return {"error": str(e)}

def main():
    # Header
    st.markdown('<h1 class="main-header">📝➡️🎵 Text to Audio Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Convert your text to speech with the accent of your reference audio</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_reference' not in st.session_state:
        st.session_state.selected_reference = None
    if 'generated_audio' not in st.session_state:
        st.session_state.generated_audio = None
    if 'input_text' not in st.session_state:
        st.session_state.input_text = ""
    
    # Text input section
    st.markdown("""
    <div class="text-section">
        <div class="text-header">
            <div class="text-icon">📝</div>
            <div>
                <h3 class="text-title">Input Text</h3>
                <p class="text-description">Enter the text you want to convert to speech</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💬 What text do you want to convert?")
    st.markdown("Enter the text you want to convert to speech. The resulting audio will have the accent and characteristics of your reference audio.")
    
    # Text input
    input_text = st.text_area(
        "Enter your text here:",
        value=st.session_state.input_text,
        height=200,
        placeholder="Type your text here... For example: 'Hello, how are you today? I hope you're having a wonderful day!'",
        help="The text will be converted to speech with the accent of your reference audio",
        key="text_input"
    )
    
    if input_text:
        st.session_state.input_text = input_text
        st.success(f"✅ Text ready: {len(input_text)} characters")
    
    # Reference audio section
    st.markdown("""
    <div class="reference-section">
        <div class="reference-header">
            <div class="reference-icon">🎭</div>
            <div>
                <h3 class="reference-title">Reference Audio</h3>
                <p class="reference-description">Choose audio with the accent you want to mimic</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 What is Reference Audio?")
    st.markdown("""
    This is the audio file that contains the accent and voice characteristics you want to apply to your text. 
    The AI will analyze this audio and generate speech that matches its accent, tone, and style.
    
    **Choose from your processed audio files or upload a new one:**
    """)
    
    # Get available reference audio files
    reference_files = get_reference_audio_files()
    
    if reference_files:
        st.markdown("### 📁 Available Reference Audio Files")
        
        # Group files by folder
        folders = {}
        for file in reference_files:
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
                        if st.button(f"🎵 {file['name']}", key=f"ref_{file['name']}", use_container_width=True):
                            st.session_state.selected_reference = file
                            st.session_state.generated_audio = None
                            st.rerun()
        else:
            # Single folder - display as list
            for file in reference_files:
                if st.button(f"🎵 {file['name']}", key=f"ref_{file['name']}", use_container_width=True):
                    st.session_state.selected_reference = file
                    st.session_state.generated_audio = None
                    st.rerun()
    
    # Upload new reference audio
    st.markdown("### 📤 Or Upload New Reference Audio")
    uploaded_reference = st.file_uploader(
        "Upload reference audio file",
        type=['wav', 'mp3', 'flac', 'm4a'],
        help="Upload an audio file with the accent you want to mimic",
        key="uploaded_reference"
    )
    
    if uploaded_reference:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_reference.read())
            tmp_path = tmp_file.name
        
        st.session_state.selected_reference = {
            'name': uploaded_reference.name,
            'path': tmp_path,
            'folder': 'uploaded',
            'full_name': f"uploaded/{uploaded_reference.name}"
        }
        st.success(f"✅ Reference audio uploaded: {uploaded_reference.name}")
    
    # Display selected reference audio
    if st.session_state.selected_reference:
        st.markdown("### 🎧 Selected Reference Audio")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**File:** {st.session_state.selected_reference['name']}")
            st.markdown(f"**Source:** {st.session_state.selected_reference['folder']}")
            
            # Audio player
            audio_html = create_audio_player(st.session_state.selected_reference['path'])
            st.markdown(audio_html, unsafe_allow_html=True)
        
        with col2:
            # File info
            try:
                audio_data, sample_rate = sf.read(st.session_state.selected_reference['path'])
                duration = len(audio_data) / sample_rate
                st.markdown(f"**Duration:** {duration:.2f} seconds")
                st.markdown(f"**Sample Rate:** {sample_rate} Hz")
                st.markdown(f"**Channels:** {audio_data.shape[1] if len(audio_data.shape) > 1 else 1}")
            except Exception as e:
                st.error(f"Error reading audio info: {str(e)}")
    
    # Generation section
    if input_text and st.session_state.selected_reference:
        st.markdown("### 🎵 Generate Audio")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="accent-info">
                <strong>🎯 Accent Transfer:</strong> Your text will be converted to speech with the accent and characteristics of the reference audio.
                <br><strong>📝 Text:</strong> "{text}"
                <br><strong>🎭 Reference:</strong> {reference}
            </div>
            """.format(
                text=input_text[:50] + "..." if len(input_text) > 50 else input_text,
                reference=st.session_state.selected_reference['name']
            ), unsafe_allow_html=True)
        
        with col2:
            if st.button("🚀 Generate Audio", type="primary", use_container_width=True):
                with st.spinner("Generating audio with accent... This may take a moment."):
                    # Create output file path
                    output_filename = f"generated_{len(input_text)}_{st.session_state.selected_reference['name']}.wav"
                    output_path = os.path.join("processed", "generated", output_filename)
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Generate audio
                    result = text_to_speech_with_accent(
                        input_text,
                        st.session_state.selected_reference['path'],
                        output_path
                    )
                    
                    if result.get("success"):
                        st.session_state.generated_audio = {
                            'path': output_path,
                            'filename': output_filename,
                            'duration': result['duration'],
                            'sample_rate': result['sample_rate']
                        }
                        st.success("✅ Audio generated successfully!")
                    else:
                        st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        
        # Display generated audio
        if st.session_state.generated_audio:
            st.markdown("### ✅ Generated Audio")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**File:** {st.session_state.generated_audio['filename']}")
                st.markdown(f"**Duration:** {st.session_state.generated_audio['duration']:.2f} seconds")
                
                # Audio player
                audio_html = create_audio_player(st.session_state.generated_audio['path'])
                st.markdown(audio_html, unsafe_allow_html=True)
            
            with col2:
                # Download button
                if os.path.exists(st.session_state.generated_audio['path']):
                    with open(st.session_state.generated_audio['path'], 'rb') as f:
                        audio_bytes = f.read()
                    
                    st.download_button(
                        label="💾 Download Audio",
                        data=audio_bytes,
                        file_name=st.session_state.generated_audio['filename'],
                        mime="audio/wav"
                    )
                
                # Regenerate button
                if st.button("🔄 Regenerate", use_container_width=True):
                    st.session_state.generated_audio = None
                    st.rerun()
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. **Enter your text** in the text area above
    2. **Choose reference audio** from your processed files or upload new audio
    3. **Click "Generate Audio"** to create speech with the reference accent
    4. **Download the result** or regenerate with different settings
    
    **Perfect for:**
    - Creating voice content with specific accents
    - Language learning with native pronunciation
    - Voice acting and character work
    - Content creation with consistent voice style
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>📝➡️🎵 Text to Audio Converter | Powered by AI</p>
        <p>Convert text to speech with any accent from your reference audio</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
