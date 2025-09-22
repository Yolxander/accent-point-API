import streamlit as st
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="OpenVoice AI Suite",
    page_icon="🎵",
    layout="wide"
)

def main():
    # Get the page parameter from URL
    query_params = st.query_params
    page = query_params.get("page", "main")
    
    if page == "voice_conversion":
        # Import and run the voice conversion app
        try:
            from app import main as voice_main
            voice_main()
        except ImportError as e:
            st.error(f"Error loading voice conversion app: {e}")
            st.info("Make sure app.py exists in the current directory.")
    elif page == "audio_to_text":
        # Import and run the audio to text app
        try:
            from app_audio_to_text import main as text_main
            text_main()
        except ImportError as e:
            st.error(f"Error loading audio to text app: {e}")
            st.info("Make sure app_audio_to_text.py exists in the current directory.")
    else:
        # Show the main navigation
        try:
            from app_main import main as main_nav
            main_nav()
        except ImportError as e:
            st.error(f"Error loading main navigation: {e}")
            st.info("Make sure app_main.py exists in the current directory.")

if __name__ == "__main__":
    main()
