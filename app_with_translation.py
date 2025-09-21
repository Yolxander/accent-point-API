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
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 3px solid #ffc107;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2);
    }
    .warning-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #856404;
        margin-bottom: 1rem;
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 3px solid #17a2b8;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(23, 162, 184, 0.2);
    }
    .info-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #0c5460;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎵 OpenVoice AI Audio Converter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform your voice using AI-powered voice conversion</p>', unsafe_allow_html=True)
    
    # Important notice about language conversion
    st.markdown("""
    <div class="warning-box">
        <div class="warning-title">⚠️ Important: OpenVoice Limitations</div>
        <p><strong>OpenVoice does NOT change language!</strong></p>
        <ul>
            <li>✅ <strong>Voice Conversion</strong>: Changes tone/timbre (male→female, etc.)</li>
            <li>✅ <strong>Same Language</strong>: Works best with same language input/reference</li>
            <li>❌ <strong>Language Translation</strong>: Spanish input + English reference = Still Spanish output</li>
            <li>❌ <strong>Accent Change</strong>: Limited accent modification</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-title">💡 How to Get Better Results</div>
        <p><strong>For Voice Conversion (Same Language):</strong></p>
        <ul>
            <li>Use English input + English reference voice</li>
            <li>Use Spanish input + Spanish reference voice</li>
            <li>Choose reference voice with different gender/age characteristics</li>
        </ul>
        
        <p><strong>For Language + Voice Conversion:</strong></p>
        <ul>
            <li>You need a different approach: Speech→Text→Translation→Text→Speech</li>
            <li>Consider using tools like ElevenLabs, Azure Speech, or Google Cloud Speech</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Test with same language
    st.markdown("### 🧪 Test OpenVoice with Same Language")
    st.markdown("Try uploading audio files in the same language to see the voice conversion effect:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📁 Upload Input Audio")
        input_file = st.file_uploader(
            "Choose your input audio file", 
            type=['wav', 'mp3', 'flac', 'm4a'],
            key="input_file_test",
            help="Upload audio in the same language as your reference"
        )
    
    with col2:
        st.markdown("#### 🎯 Upload Reference Voice")
        ref_file = st.file_uploader(
            "Choose reference voice file", 
            type=['wav', 'mp3', 'flac', 'm4a'],
            key="ref_file_test",
            help="Upload reference voice in the same language"
        )
    
    if input_file and ref_file:
        st.info("🎯 **Tip**: For best results, use audio files in the same language (both English or both Spanish)")
        
        if st.button("🔄 Test Voice Conversion"):
            with st.spinner("Converting voice..."):
                try:
                    # Load audio files
                    def load_audio_file(uploaded_file):
                        file_extension = uploaded_file.name.split('.')[-1].lower()
                        with tempfile.NamedTemporaryFile(suffix=f'.{file_extension}', delete=False) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        try:
                            if file_extension in ['mp3', 'm4a', 'aac', 'ogg']:
                                audio_data, sample_rate = librosa.load(tmp_file_path, sr=None)
                            else:
                                audio_data, sample_rate = sf.read(tmp_file_path)
                            os.unlink(tmp_file_path)
                            return audio_data, sample_rate
                        except Exception as e:
                            os.unlink(tmp_file_path)
                            raise e
                    
                    input_data, input_sr = load_audio_file(input_file)
                    ref_data, ref_sr = load_audio_file(ref_file)
                    
                    # Import and run OpenVoice
                    import openvoice_cli.__main__ as openvoice_main
                    tune_one = openvoice_main.tune_one
                    
                    # Create temporary files
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_input:
                        sf.write(temp_input.name, input_data, input_sr)
                        temp_input_path = temp_input.name
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_ref:
                        sf.write(temp_ref.name, ref_data, ref_sr)
                        temp_ref_path = temp_ref.name
                    
                    output_path = "test_converted.wav"
                    
                    # Run conversion
                    tune_one(
                        input_file=temp_input_path,
                        ref_file=temp_ref_path,
                        output_file=output_path,
                        device="cpu"
                    )
                    
                    if os.path.exists(output_path):
                        converted_data, converted_sr = sf.read(output_path)
                        
                        st.success("✅ Conversion completed!")
                        st.markdown("#### 🎧 Results")
                        
                        # Create audio players
                        def create_audio_player(audio_data, sample_rate, label):
                            buffer = BytesIO()
                            sf.write(buffer, audio_data, sample_rate, format='WAV')
                            buffer.seek(0)
                            audio_base64 = base64.b64encode(buffer.getvalue()).decode()
                            
                            return f"""
                            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                                <h4 style="color: #1f77b4;">{label}</h4>
                                <audio controls style="width: 100%;">
                                    <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                                </audio>
                            </div>
                            """
                        
                        st.markdown(create_audio_player(input_data, input_sr, "Original Input"), unsafe_allow_html=True)
                        st.markdown(create_audio_player(ref_data, ref_sr, "Reference Voice"), unsafe_allow_html=True)
                        st.markdown(create_audio_player(converted_data, converted_sr, "Converted Voice"), unsafe_allow_html=True)
                        
                        # Clean up
                        os.unlink(temp_input_path)
                        os.unlink(temp_ref_path)
                        os.unlink(output_path)
                        
                    else:
                        st.error("❌ Conversion failed")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("### About OpenVoice AI")
    st.markdown("""
    **OpenVoice is designed for voice conversion, not language translation.**
    
    - **Voice Conversion**: Changes tone, timbre, gender characteristics
    - **Language Preservation**: Keeps original language and content
    - **Best Results**: Use same language for input and reference
    
    **For language conversion, consider:**
    - ElevenLabs (with translation features)
    - Azure Speech Services
    - Google Cloud Speech-to-Text + Translation + Text-to-Speech
    """)

if __name__ == "__main__":
    main()
