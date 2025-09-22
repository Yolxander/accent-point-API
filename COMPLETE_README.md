# 🎵 OpenVoice AI Suite - Complete Guide

A comprehensive AI-powered voice processing toolkit that combines voice conversion with audio-to-text transcription capabilities.

## 🌟 Features

### 🎤 Voice Conversion
- **Accent Transformation**: Change voice accent while preserving gender
- **Real-time Preview**: Listen to audio before processing
- **Batch Processing**: Process multiple audio files
- **Advanced Settings**: Customize conversion parameters
- **Gender Preservation**: Maintains original voice gender

### 📝 Audio to Text
- **AI Transcription**: Powered by OpenAI Whisper
- **Multi-language Support**: 99+ languages with automatic detection
- **Detailed Segments**: Timestamped transcription
- **Export Options**: Download as text files
- **Audio Preview**: Listen while transcribing

## 🚀 Quick Start

### Prerequisites
- Anaconda or Miniconda installed
- Python 3.11+ (recommended)

### Installation

1. **Clone or download the project**
2. **Activate the openvoice environment**:
   ```bash
   conda activate openvoice
   ```

3. **Install additional dependencies** (if not already installed):
   ```bash
   pip install openai-whisper
   ```

### Running the Applications

#### Option 1: Complete Suite (Recommended)
```bash
./run_suite.sh
```
This launches the main navigation page where you can choose between:
- Voice Conversion
- Audio to Text

#### Option 2: Individual Apps

**Voice Conversion Only:**
```bash
conda activate openvoice
streamlit run app.py
```

**Audio to Text Only:**
```bash
./run_audio_to_text.sh
# or
conda activate openvoice
streamlit run app_audio_to_text.py
```

## 📖 Detailed Usage

### Voice Conversion Workflow

1. **Launch the Voice Conversion app**
2. **Upload your audio file** (WAV, MP3, M4A, etc.)
3. **Upload a reference audio** (the accent you want to copy)
4. **Preview both audio files**
5. **Click "Convert Voice"** to process
6. **Download the converted audio**

### Audio to Text Workflow

1. **Launch the Audio to Text app**
2. **Load a Whisper model** (choose size based on accuracy vs speed needs)
3. **Select language** (optional, for better accuracy)
4. **Choose an audio file** from your processed files
5. **Click "Start Transcription"**
6. **View, copy, or download the transcribed text**

## 🔧 Configuration

### Whisper Model Sizes

| Model | Speed | Accuracy | Memory | Use Case |
|-------|-------|----------|--------|----------|
| tiny  | Fastest | Good | ~1GB | Quick testing |
| base  | Fast | Better | ~1GB | **Recommended** |
| small | Medium | Good | ~2GB | Balanced |
| medium| Slow | Better | ~5GB | High accuracy |
| large | Slowest | Best | ~10GB | Maximum accuracy |

### Supported Audio Formats

**Voice Conversion:**
- WAV, MP3, M4A, FLAC, OGG

**Audio to Text:**
- WAV, MP3, M4A, FLAC, OGG, and more

## 🔄 Complete Workflow Example

Here's a typical workflow using both features:

1. **Record or upload an audio file** (e.g., "Hello, how are you today?")

2. **Convert the voice accent**:
   - Upload your audio
   - Upload a reference audio with the desired accent
   - Convert to get "Hello, how are you today?" in the new accent

3. **Transcribe the converted audio**:
   - Load Whisper model
   - Select the converted audio file
   - Get the transcribed text: "Hello, how are you today?"

4. **Use the results**:
   - Download the converted audio
   - Copy or download the transcribed text
   - Use for content creation, language learning, etc.

## 📁 File Structure

```
openvoice-project/
├── app.py                    # Voice conversion app
├── app_audio_to_text.py     # Audio to text app
├── app_main.py              # Main navigation
├── launcher.py              # App launcher
├── run_suite.sh             # Complete suite launcher
├── run_audio_to_text.sh     # Audio to text launcher
├── test_audio_to_text.py    # Test script
├── requirements.txt         # Dependencies
├── processed/               # Converted audio files
│   ├── folder1/
│   │   └── wavs/
│   │       ├── file1.wav
│   │       └── file2.wav
│   └── folder2/
│       └── wavs/
│           └── file3.wav
└── README files
```

## 🛠️ Troubleshooting

### Common Issues

1. **"OpenVoice CLI not found"**
   - Solution: Install with `pip install openvoice-cli`

2. **"No audio files found"**
   - Solution: Make sure you have processed audio files in the `processed/` directory

3. **"Whisper model loading fails"**
   - Solution: Check internet connection and available disk space

4. **"Streamlit not found"**
   - Solution: Install with `pip install streamlit`

5. **Python version issues**
   - Solution: Use the openvoice conda environment (Python 3.11)

### Performance Tips

- Use `base` or `small` Whisper models for good balance
- Specify the language for better transcription accuracy
- Ensure sufficient disk space for model downloads
- Close other applications to free up memory

## 🎯 Use Cases

### Content Creation
- Convert voice for different characters
- Transcribe content for subtitles
- Create multilingual content

### Language Learning
- Practice different accents
- Transcribe speech for analysis
- Compare pronunciation

### Accessibility
- Convert audio to text for hearing impaired
- Create transcripts for videos
- Generate captions

### Voice Acting
- Try different voice styles
- Transcribe scripts
- Practice character voices

## 📊 Technical Details

### Voice Conversion
- **Backend**: OpenVoice AI
- **Processing**: Real-time audio conversion
- **Output**: High-quality WAV files

### Audio to Text
- **Backend**: OpenAI Whisper
- **Processing**: AI-powered transcription
- **Output**: Plain text with timestamps

### Frontend
- **Framework**: Streamlit
- **Styling**: Custom CSS
- **Responsive**: Works on desktop and mobile

## 🔒 Security & Privacy

- All processing happens locally on your machine
- No audio data is sent to external servers
- Files are stored locally in the `processed/` directory
- You have full control over your data

## 📝 License

This project uses:
- OpenVoice AI (check their license)
- OpenAI Whisper (MIT License)
- Streamlit (Apache 2.0)

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section
2. Run the test script: `python test_audio_to_text.py`
3. Ensure you're using the openvoice environment
4. Check that all dependencies are installed

## 🎉 Getting Started

1. **Activate the environment**: `conda activate openvoice`
2. **Run the test**: `python test_audio_to_text.py`
3. **Launch the suite**: `./run_suite.sh`
4. **Start creating!** 🎵➡️📝

---

**Happy voice processing!** 🎤✨
