import streamlit as st
import os
import tempfile
import soundfile as sf
import numpy as np
import base64
from io import BytesIO
import librosa
import torch
import torchaudio
import subprocess
import sys

# Page configuration
st.set_page_config(
    page_title="Text to Speech Generator",
    page_icon="📝",
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
    .text-section {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #c3e6cb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .generated-audio {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 2rem;
        border: 2px solid #ffeaa7;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .voice-info {
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

def simple_tts_simulation(text, voice_file):
    """Simulate TTS generation (placeholder for actual TTS implementation)"""
    try:
        # For now, we'll create a simple simulation
        # In a real implementation, this would use TTS models like:
        # - Coqui TTS
        # - Tortoise TTS
        # - Bark
        # - or other voice cloning models
        
        # Read the voice file to get characteristics
        voice_data, sample_rate = sf.read(voice_file)
        
        # Create a simple tone that represents the "generated" speech
        # This is just a placeholder - real TTS would generate actual speech
        duration = len(text.split()) * 0.5  # Rough estimate: 0.5 seconds per word
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a simple waveform (this is just for demonstration)
        frequency = 200 + (hash(text) % 100)  # Vary frequency based on text
        waveform = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Add some variation to make it more interesting
        waveform += np.sin(2 * np.pi * frequency * 2 * t) * 0.1
        
        # Normalize
        waveform = waveform / np.max(np.abs(waveform)) * 0.8
        
        return waveform, sample_rate
    except Exception as e:
        st.error(f"Error in TTS simulation: {str(e)}")
        return None, None

def main():
    # Header
    st.markdown('<h1 class="main-header">📝➡️🎵 Text to Speech Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Create new audio using your converted voice files and custom text</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'selected_voice' not in st.session_state:
        st.session_state.selected_voice = None
    if 'generated_audio' not in st.session_state:
        st.session_state.generated_audio = None
    if 'generated_text' not in st.session_state:
        st.session_state.generated_text = None
    
    # Get available converted audio files
    audio_files = get_audio_files()
    
    if not audio_files:
        st.error("❌ No converted audio files found.")
        st.info("💡 Please use the Voice Conversion page first to create some converted audio files.")
        
        st.markdown("### 🚀 Quick Start Guide")
        st.markdown("""
        1. **Go to Voice Conversion page** - Convert your voice with different accents
        2. **Upload your audio** - Your original voice recording
        3. **Upload reference voice** - The accent you want to adopt
        4. **Convert your voice** - Generate converted audio files
        5. **Return here** - Use the converted files to create new speech
        """)
        
        st.markdown("### 🎯 What This Feature Does")
        st.markdown("""
        Once you have converted voice files, you can:
        - **Type any text** you want to convert to speech
        - **Select a converted voice** to use as the voice style
        - **Generate new audio** that speaks your text in the converted voice
        - **Download the result** as an audio file
        
        Perfect for creating custom content with your converted voice!
        """)
        return
    
    # Text input section
    st.markdown("### 📝 Enter Your Text")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        text_input = st.text_area(
            "Type the text you want to convert to speech:",
            placeholder="Enter your text here... For example: 'Hello, this is my converted voice speaking your custom text!'",
            height=100,
            value=st.session_state.get('generated_text', '')
        )
    
    with col2:
        st.markdown("**💡 Tips:**")
        st.markdown("• Keep text under 500 characters for best results")
        st.markdown("• Use punctuation for natural pauses")
        st.markdown("• Avoid special characters")
    
    if not text_input.strip():
        st.warning("⚠️ Please enter some text to convert.")
        return
    
    # Voice selection section
    st.markdown("### 🎤 Select Converted Voice")
    
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
                        st.session_state.selected_voice = file
                        st.session_state.generated_audio = None
                        st.rerun()
    else:
        # Single folder - display as list
        for file in audio_files:
            if st.button(f"🎵 {file['name']}", key=f"select_{file['name']}", use_container_width=True):
                st.session_state.selected_voice = file
                st.session_state.generated_audio = None
                st.rerun()
    
    # Display selected voice
    if st.session_state.selected_voice:
        voice = st.session_state.selected_voice
        
        st.markdown("### 🎧 Selected Voice")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**File:** {voice['name']}")
            st.markdown(f"**Folder:** {voice['folder']}")
            
            # Audio player
            audio_html = create_audio_player(voice['path'])
            st.markdown(audio_html, unsafe_allow_html=True)
        
        with col2:
            # File info
            try:
                audio_data, sample_rate = sf.read(voice['path'])
                duration = len(audio_data) / sample_rate
                st.markdown(f"**Duration:** {duration:.2f} seconds")
                st.markdown(f"**Sample Rate:** {sample_rate} Hz")
                st.markdown(f"**Channels:** {audio_data.shape[1] if len(audio_data.shape) > 1 else 1}")
            except Exception as e:
                st.error(f"Error reading audio info: {str(e)}")
        
        # Generate speech section
        st.markdown("### 🎯 Generate Speech")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🎵 Generate Speech from Text", type="primary", use_container_width=True):
                with st.spinner("Generating speech... This may take a moment."):
                    # Generate the speech
                    waveform, sample_rate = simple_tts_simulation(text_input, voice['path'])
                    
                    if waveform is not None:
                        st.session_state.generated_audio = {
                            'waveform': waveform,
                            'sample_rate': sample_rate,
                            'text': text_input,
                            'voice_file': voice['name']
                        }
                        st.session_state.generated_text = text_input
                        st.success("✅ Speech generated successfully!")
                    else:
                        st.error("❌ Failed to generate speech.")
        
        with col2:
            st.markdown("**⚙️ Settings:**")
            st.markdown("• Voice: Selected voice file")
            st.markdown("• Text length: " + str(len(text_input.split())) + " words")
            st.markdown("• Estimated duration: ~" + str(len(text_input.split()) * 0.5) + " seconds")
        
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
                
                st.markdown(audio_html, unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    label="💾 Download Generated Audio",
                    data=audio_bytes,
                    file_name=f"generated_speech_{voice['name']}.wav",
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
                st.markdown(f"**Voice:** {audio_data['voice_file']}")
                
            except Exception as e:
                st.error(f"Error creating audio player: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>📝➡️🎵 Text to Speech Generator | Powered by OpenVoice AI</p>
        <p>Create custom audio using your converted voice files</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
