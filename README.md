# OpenVoice API

A production-ready FastAPI backend for voice conversion and text-to-speech using OpenVoice AI. This API is designed to be integrated with Next.js frontends and can be deployed on live servers.

## 🚀 Features

### Core Functionality
- **Audio-to-Audio Conversion**: Convert voice accents while preserving gender and content
- **Text-to-Speech**: Generate speech from text using reference voice characteristics
- **Batch Processing**: Process multiple files or texts simultaneously
- **Real-time Status Updates**: WebSocket support for conversion progress

### Advanced Features
- **CORS Configuration**: Ready for Next.js frontend integration
- **File Validation**: Comprehensive audio file validation
- **Error Handling**: Robust error handling and logging
- **Rate Limiting**: Built-in rate limiting for API protection
- **Health Checks**: Comprehensive health monitoring
- **Docker Support**: Production-ready Docker configuration

## 📋 API Endpoints

### Health & Status
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system metrics

### Voice Conversion
- `POST /api/v1/convert-voice` - Convert voice using reference audio
- `GET /api/v1/download/{filename}` - Download converted audio files
- `GET /api/v1/conversion-status/{conversion_id}` - Check conversion status

### Text-to-Speech
- `POST /api/v1/convert-text-to-speech` - Convert text to speech with voice characteristics
- `POST /api/v1/preview-tts` - Generate TTS preview without voice conversion

### Batch Processing
- `POST /api/v1/batch/convert-voices` - Batch voice conversion
- `POST /api/v1/batch/convert-texts` - Batch text-to-speech conversion
- `GET /api/v1/batch/status/{batch_id}` - Check batch processing status

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- FFmpeg
- OpenVoice CLI dependencies

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd openvoice-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp env.example .env
# Edit .env with your configuration
```

4. **Run the application**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose**:
```bash
docker-compose up -d
```

2. **Or build and run manually**:
```bash
docker build -t openvoice-api .
docker run -p 8000:8000 openvoice-api
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (development/production) | development |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `ALLOWED_ORIGINS` | CORS allowed origins | http://localhost:3000 |
| `OPENVOICE_DEVICE` | Processing device (cpu/cuda) | cpu |
| `MAX_FILE_SIZE` | Maximum file size in bytes | 52428800 (50MB) |
| `TARGET_SAMPLE_RATE` | Target audio sample rate | 22050 |

### CORS Configuration

The API is pre-configured for Next.js frontend integration:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:3001",
    "https://yourdomain.com"  # Production domain
]
```

## 📱 Frontend Integration

### Next.js API Client Example

```typescript
// services/voiceApi.ts
export class VoiceApiService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async convertVoice(inputAudio: File, referenceAudio: File, device: 'cpu' | 'cuda' = 'cpu') {
    const formData = new FormData();
    formData.append('input_audio', inputAudio);
    formData.append('reference_audio', referenceAudio);
    formData.append('device', device);

    const response = await fetch(`${this.baseUrl}/api/v1/convert-voice`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Voice conversion failed');
    }

    return response.blob();
  }
}
```

### React Component Example

```tsx
// components/VoiceConverter.tsx
import React, { useState } from 'react';
import { VoiceApiService } from '../services/voiceApi';

export const VoiceConverter: React.FC = () => {
  const [inputAudio, setInputAudio] = useState<File | null>(null);
  const [referenceAudio, setReferenceAudio] = useState<File | null>(null);
  const [convertedAudio, setConvertedAudio] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const voiceApi = new VoiceApiService();

  const handleConvert = async () => {
    if (!inputAudio || !referenceAudio) return;

    setIsLoading(true);
    try {
      const audioBlob = await voiceApi.convertVoice(inputAudio, referenceAudio);
      const audioUrl = URL.createObjectURL(audioBlob);
      setConvertedAudio(audioUrl);
    } catch (error) {
      console.error('Conversion failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <input type="file" accept="audio/*" onChange={(e) => setInputAudio(e.target.files?.[0] || null)} />
      <input type="file" accept="audio/*" onChange={(e) => setReferenceAudio(e.target.files?.[0] || null)} />
      <button onClick={handleConvert} disabled={!inputAudio || !referenceAudio || isLoading}>
        {isLoading ? 'Converting...' : 'Convert Voice'}
      </button>
      {convertedAudio && <audio controls src={convertedAudio} />}
    </div>
  );
};
```

## 🚀 Production Deployment

### Using Docker Compose

1. **Configure production environment**:
```bash
# Edit docker-compose.yml
environment:
  - ENVIRONMENT=production
  - ALLOWED_ORIGINS=https://yourdomain.com
```

2. **Deploy**:
```bash
docker-compose up -d
```

### Using Cloud Providers

The API is ready for deployment on:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**
- **Heroku** (with Docker)

### Environment Variables for Production

```bash
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com
OPENVOICE_DEVICE=cpu
MAX_FILE_SIZE=52428800
LOG_LEVEL=INFO
```

## 📊 Monitoring & Health Checks

### Health Endpoints

- **Basic Health**: `GET /api/v1/health`
- **Detailed Health**: `GET /api/v1/health/detailed`

### Metrics Included

- System resources (CPU, memory, disk)
- Directory status
- OpenVoice availability
- Service status

## 🔒 Security Features

- **CORS Protection**: Configurable allowed origins
- **File Validation**: Audio file type and size validation
- **Rate Limiting**: Built-in request rate limiting
- **Error Handling**: Secure error responses
- **Input Sanitization**: Comprehensive input validation

## 📝 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the health status at `/api/v1/health/detailed`
