#!/usr/bin/env python3
"""
Demo script showing the complete workflow:
1. Voice conversion (using existing processed files)
2. Audio to text transcription
"""

import os
import sys
import subprocess

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🎵 {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def check_environment():
    """Check if we're in the right environment"""
    print_header("Environment Check")
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found. Please run from openvoice-project directory.")
        return False
    
    # Check if processed files exist
    processed_dir = "processed"
    if not os.path.exists(processed_dir):
        print("❌ Error: No processed directory found.")
        print("   Please run the voice conversion app first to create some audio files.")
        return False
    
    # Count audio files
    audio_count = 0
    for folder in os.listdir(processed_dir):
        folder_path = os.path.join(processed_dir, folder)
        if os.path.isdir(folder_path):
            wavs_dir = os.path.join(folder_path, "wavs")
            if os.path.exists(wavs_dir):
                audio_count += len([f for f in os.listdir(wavs_dir) if f.endswith('.wav')])
    
    print(f"✅ Found {audio_count} processed audio files")
    
    if audio_count == 0:
        print("❌ No audio files found in processed directory.")
        print("   Please run the voice conversion app first.")
        return False
    
    return True

def show_workflow():
    """Show the complete workflow"""
    print_header("Complete Workflow Demo")
    
    print("""
🎯 This demo shows how to use both features of the OpenVoice AI Suite:

1️⃣ VOICE CONVERSION:
   • Upload your original audio file
   • Upload a reference audio with desired accent
   • Convert to get your voice in the new accent
   • Files are saved in the 'processed/' directory

2️⃣ AUDIO TO TEXT:
   • Select from your processed audio files
   • Choose a Whisper model (base recommended)
   • Transcribe the audio to text
   • Export as text file or copy to clipboard

🔄 COMPLETE PIPELINE:
   Original Audio → Voice Conversion → Audio to Text → Final Text
   """)

def show_launch_instructions():
    """Show how to launch the apps"""
    print_header("How to Launch")
    
    print("""
🚀 LAUNCH OPTIONS:

Option 1 - Complete Suite (Recommended):
   ./run_suite.sh
   Then choose between Voice Conversion or Audio to Text

Option 2 - Individual Apps:
   Voice Conversion:  conda activate openvoice && streamlit run app.py
   Audio to Text:     ./run_audio_to_text.sh

Option 3 - Direct URLs:
   Main Menu:         http://localhost:8501
   Voice Conversion:  http://localhost:8501/?page=voice_conversion
   Audio to Text:     http://localhost:8501/?page=audio_to_text
   """)

def show_file_structure():
    """Show the file structure"""
    print_header("File Structure")
    
    print("""
📁 PROJECT STRUCTURE:
openvoice-project/
├── app.py                    # Voice conversion app
├── app_audio_to_text.py     # Audio to text app
├── app_main.py              # Main navigation
├── launcher.py              # App launcher
├── run_suite.sh             # Complete suite launcher
├── run_audio_to_text.sh     # Audio to text launcher
├── test_audio_to_text.py    # Test script
├── processed/               # Your converted audio files
│   ├── folder1/
│   │   └── wavs/
│   │       ├── file1.wav
│   │       └── file2.wav
│   └── folder2/
│       └── wavs/
│           └── file3.wav
└── README files
   """)

def main():
    """Main demo function"""
    print_header("OpenVoice AI Suite - Workflow Demo")
    
    # Check environment
    if not check_environment():
        return
    
    # Show workflow
    show_workflow()
    
    # Show launch instructions
    show_launch_instructions()
    
    # Show file structure
    show_file_structure()
    
    print_header("Ready to Start!")
    print("""
🎉 Everything is set up and ready to go!

Next steps:
1. Run: ./run_suite.sh
2. Choose your tool
3. Start creating amazing voice content!

Happy voice processing! 🎤✨
   """)

if __name__ == "__main__":
    main()
