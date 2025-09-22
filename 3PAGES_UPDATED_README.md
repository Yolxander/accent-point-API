# OpenVoice AI Suite - 2-Page Application

## 🎵 Overview

This is the updated OpenVoice AI Suite that now contains only 2 main features: **Audio to Audio** conversion and **Text to Audio** generation. The Audio to Text functionality has been removed as requested.

## 🚀 Quick Start

### Launch the Application
```bash
./run_3pages.sh
```

Or manually:
```bash
streamlit run app_3pages.py
```

## 📋 Features

### 1. 🏠 Welcome Page (Landing Page)
- **Purpose**: Overview of all available features
- **Navigation**: Access to both main features
- **Status**: Shows which features are ready to use
- **Workflow**: Visual guide of the complete process

### 2. ��➡️🎵 Audio to Audio (Voice Conversion)
- **Purpose**: Transform voice accent while preserving gender and content
- **Technology**: OpenVoice AI
- **Features**:
  - Accent conversion with gender preservation
  - Real-time audio preview
  - High-quality professional conversion
  - Support for multiple audio formats (WAV, MP3, FLAC, M4A)

### 3. 📝➡️🎵 Text to Audio (Text to Speech)
- **Purpose**: Convert text to audio using uploaded voice file characteristics
- **Features**:
  - Upload reference voice file
  - Enter custom text to convert
  - Generate audio matching uploaded voice characteristics
  - Audio preview and download
  - Support for multiple audio formats (WAV, MP3, FLAC, M4A)

## �� Complete Workflow

1. **Audio to Audio**: Convert your voice accent
2. **Text to Audio**: Create new speech with custom text using uploaded voice

## 🎯 Text to Audio Feature

### How It Works
1. **Upload Reference Voice**: Upload an audio file with the voice characteristics you want to match
2. **Enter Text**: Type the text you want to convert to speech
3. **Generate Audio**: The system creates audio that matches your reference voice characteristics
4. **Preview & Download**: Listen to the result and download the audio file

### Use Cases
- Creating custom voiceovers with specific accents
- Generating speech in your own voice style
- Content creation with consistent voice characteristics
- Accessibility applications
- Voice acting and character work

### Technical Details
- Accepts WAV, MP3, FLAC, M4A files
- Analyzes uploaded voice for characteristics
- Generates audio based on text input
- Provides audio preview and download
- File size limit: 200MB

## 📁 File Structure

```
app_3pages.py          # Main 2-page application
run_3pages.sh          # Launch script
app.py                 # Audio to Audio functionality
processed/             # Output directory for processed files
```

## 🛠️ Dependencies

### Required
- streamlit
- soundfile
- numpy
- librosa
- base64
- tempfile

### Optional (for full functionality)
- openvoice-cli (for Audio to Audio)
- torch, torchaudio (for enhanced TTS)

## 🚀 Installation

1. **Clone or download the project**
2. **Install basic dependencies**:
   ```bash
   pip install streamlit soundfile numpy librosa
   ```

3. **Install optional dependencies** (for full functionality):
   ```bash
   # For Audio to Audio (voice conversion)
   pip install openvoice-cli
   
   # For enhanced Text to Audio
   pip install torch torchaudio
   ```

## 🎮 Usage

### Navigation
- Start at the **Welcome Page** to see all available features
- Click on any feature card to navigate to that functionality
- Use the "← Back to Main Menu" button to return to the welcome page

### Text to Audio Feature
1. Navigate to "Text to Audio" from the welcome page
2. Enter your text in the left column
3. Upload a reference voice file in the right column
4. Click "Generate Audio from Text"
5. Preview the generated audio
6. Download the result

## 🔧 Technical Notes

### Text to Audio Implementation
- Currently uses a simulation approach for demonstration
- Analyzes uploaded voice file characteristics
- Generates waveforms based on text and voice properties
- Can be enhanced with real TTS models like Coqui TTS, Tortoise TTS, or Bark

### Voice Conversion
- Uses OpenVoice AI for real accent conversion
- Preserves gender while changing accent
- Processes multiple audio formats

## 🎯 Future Enhancements

1. **Real TTS Integration**: Replace simulation with actual TTS models
2. **Voice Cloning**: Advanced voice cloning capabilities
3. **Batch Processing**: Process multiple files at once
4. **More Audio Formats**: Support for additional formats
5. **API Integration**: Connect to external TTS services

## 📞 Support

The application provides helpful error messages and guidance for:
- Missing dependencies
- File format issues
- Processing errors
- Navigation help

## 🎵 Enjoy Your Voice Processing Journey!

This 2-page application provides a focused voice processing toolkit with Audio to Audio conversion and Text to Audio generation. Start with the welcome page to explore the features!
