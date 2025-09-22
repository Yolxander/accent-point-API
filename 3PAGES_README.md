# 🎵 OpenVoice AI Suite - 3 Pages System

A comprehensive 3-page AI-powered voice processing toolkit that provides a complete workflow from voice conversion to text-to-speech generation.

## 🌟 Overview

This system consists of three interconnected pages:

1. **🏠 Landing Page** - Main navigation and workflow overview
2. **🎤 Voice Conversion** - Convert voice accents while preserving gender
3. **📝 Text to Speech** - Generate new audio using converted voices and custom text

## 🚀 Quick Start

### Prerequisites
- Anaconda or Miniconda installed
- Python 3.11+ (recommended)

### Installation

1. **Activate the openvoice environment**:
   ```bash
   conda activate openvoice
   ```

2. **Install additional dependencies** (if not already installed):
   ```bash
   pip install openai-whisper torch torchaudio
   ```

### Running the 3-Page System

```bash
./run_3pages.sh
```

This launches the complete 3-page system where you can navigate between all features.

## 📖 Page Descriptions

### 🏠 Landing Page
- **Purpose**: Main navigation hub
- **Features**:
  - Overview of all three tools
  - Workflow explanation
  - Quick access to each page
  - Dependency status checks

### 🎤 Voice Conversion Page
- **Purpose**: Convert voice accents while preserving gender
- **Features**:
  - Upload your original audio
  - Upload reference voice (target accent)
  - Real-time audio preview
  - Gender preservation
  - Batch processing
  - Download converted audio

### 📝 Text to Speech Page
- **Purpose**: Create new audio using converted voices and custom text
- **Features**:
  - Select from converted voice files
  - Enter custom text
  - Generate speech in the selected voice
  - Audio preview and download
  - Voice file management

## 🔄 Complete Workflow

### Step 1: Voice Conversion
1. Go to **Voice Conversion** page
2. Upload your original audio file
3. Upload a reference voice with the desired accent
4. Preview both audio files
5. Click "Convert Voice" to process
6. Download the converted audio files

### Step 2: Text to Speech
1. Go to **Text to Speech** page
2. Select a converted voice file from Step 1
3. Enter the text you want to convert to speech
4. Click "Generate Speech from Text"
5. Preview and download the generated audio

### Step 3: Audio to Text (Optional)
1. Go to **Audio to Text** page
2. Select any audio file (original or converted)
3. Choose a Whisper model
4. Transcribe the audio to text
5. Download or copy the transcribed text

## 🎯 Use Cases

### Content Creation
- Convert your voice for different characters
- Generate new speech with custom text
- Create multilingual content

### Language Learning
- Practice different accents
- Generate speech in target language
- Compare pronunciation

### Voice Acting
- Try different voice styles
- Generate character dialogue
- Practice with custom scripts

### Accessibility
- Convert audio to text for hearing impaired
- Generate speech from text
- Create audio content from written material

## 📁 File Structure

```
openvoice-project/
├── app_3pages.py              # Main 3-page launcher
├── app_text_to_speech.py      # Text to speech page
├── app_audio_to_text.py       # Audio to text page
├── app.py                     # Voice conversion page (existing)
├── run_3pages.sh              # 3-page system launcher
├── processed/                 # Converted audio files
│   ├── folder1/
│   │   └── wavs/
│   │       ├── file1.wav
│   │       └── file2.wav
│   └── folder2/
│       └── wavs/
│           └── file3.wav
└── README files
```

## 🛠️ Technical Details

### Voice Conversion
- **Backend**: OpenVoice AI
- **Processing**: Real-time audio conversion
- **Output**: High-quality WAV files
- **Gender Preservation**: Maintains original gender

### Text to Speech
- **Backend**: PyTorch + TorchAudio
- **Processing**: Voice cloning simulation
- **Input**: Custom text + converted voice files
- **Output**: Generated audio files

### Audio to Text
- **Backend**: OpenAI Whisper
- **Processing**: AI-powered transcription
- **Output**: Plain text with timestamps

## 🔧 Configuration

### Voice Conversion Settings
- Device selection (CPU/GPU)
- Audio format support (WAV, MP3, M4A, FLAC)
- File size limits (200MB per file)

### Text to Speech Settings
- Voice file selection
- Text length limits
- Audio quality settings

### Audio to Text Settings
- Whisper model selection
- Language specification
- Output format options

## 🚨 Troubleshooting

### Common Issues

1. **"No converted audio files found"**
   - Solution: Use Voice Conversion page first to create audio files

2. **"TTS libraries not found"**
   - Solution: Install with `pip install torch torchaudio`

3. **"OpenVoice CLI not found"**
   - Solution: Install with `pip install openvoice-cli`

4. **"Whisper model loading fails"**
   - Solution: Check internet connection and disk space

### Performance Tips

- Use CPU for stable processing
- Keep audio files under 200MB
- Use shorter text for faster TTS generation
- Close other applications to free up memory

## 🎉 Getting Started

1. **Activate environment**: `conda activate openvoice`
2. **Launch system**: `./run_3pages.sh`
3. **Start with Voice Conversion**: Convert your voice
4. **Use Text to Speech**: Create new audio with custom text
5. **Optional Audio to Text**: Transcribe audio files

## 🔒 Security & Privacy

- All processing happens locally
- No data sent to external servers
- Files stored locally in `processed/` directory
- Full control over your data

## 📝 License

This project uses:
- OpenVoice AI (check their license)
- OpenAI Whisper (MIT License)
- PyTorch (BSD License)
- Streamlit (Apache 2.0)

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section
2. Ensure you're using the openvoice environment
3. Verify all dependencies are installed
4. Check file permissions and disk space

---

**Happy voice processing!** 🎤✨

The 3-page system provides a complete voice processing pipeline from conversion to synthesis!
