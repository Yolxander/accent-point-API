# Vercel Deployment Guide for accent-point-API

## 🚀 Deployment Steps

### Prerequisites
1. Install Vercel CLI (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

### Initial Setup
Navigate to the `accent-point-API` directory and run:
```bash
cd accent-point-API
vc init fastapi
```

This will:
- Detect your FastAPI application
- Set up the necessary configuration
- Link your project to Vercel

### Deploy
```bash
vercel
```

For production deployment:
```bash
vercel --prod
```

## ⚠️ Important Considerations

### 1. **Function Size Limitations**
Your project includes heavy dependencies:
- **PyTorch** (~500MB+)
- **torchaudio** (~100MB+)
- **librosa**, **scipy**, **numpy** (large scientific libraries)
- **openvoice-cli** (ML model dependencies)

**Vercel Limitations:**
- **Function size limit**: 50MB (Hobby plan) / 250MB (Pro plan)
- Your dependencies will likely **exceed these limits**

### 2. **Solutions**

#### Option A: Use Vercel Pro Plan
- Upgrade to Vercel Pro for 250MB function size limit
- Still may not be enough for PyTorch + models

#### Option B: Externalize ML Processing
- Deploy ML models to a separate service (AWS Lambda, Google Cloud Functions, or dedicated server)
- Keep only the API layer on Vercel
- Use the external service for heavy processing

#### Option C: Use Docker/Container Deployment
- Consider deploying to:
  - **Railway** (supports Docker, larger size limits)
  - **Render** (supports Docker, good for ML apps)
  - **Fly.io** (supports Docker, good performance)
  - **AWS ECS/Fargate** (enterprise solution)

#### Option D: Optimize Dependencies
- Use CPU-only PyTorch builds (smaller)
- Remove unused dependencies
- Use lighter alternatives where possible

### 3. **Environment Variables**
Set these in Vercel Dashboard → Settings → Environment Variables:

**Required:**
- `ENVIRONMENT=production`
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_ROLE_KEY` - Your Supabase service role key

**Optional (with defaults):**
- `HOST=0.0.0.0` (Vercel handles this)
- `PORT` (Vercel handles this)
- `ALLOWED_ORIGINS` - Your frontend domain(s)
- `ALLOWED_HOSTS` - Your domain(s)
- `OPENVOICE_DEVICE=cpu`
- `MAX_FILE_SIZE=52428800`
- `LOG_LEVEL=INFO`

### 4. **Function Timeout**
- **Hobby plan**: 10 seconds
- **Pro plan**: 60 seconds
- Audio processing may exceed these limits

**Solution**: Use async processing with job queues (Redis, Supabase, etc.)

### 5. **File Storage**
Vercel serverless functions are stateless. For file uploads:
- Use **Supabase Storage** (already configured)
- Or use **AWS S3** / **Cloudflare R2**
- Don't rely on local filesystem

## 📋 Pre-Deployment Checklist

- [ ] Review and optimize `requirements.txt` (remove unused deps)
- [ ] Set all environment variables in Vercel dashboard
- [ ] Test API locally with production-like settings
- [ ] Verify Supabase connection works
- [ ] Check file upload/download functionality
- [ ] Test CORS configuration with your frontend domain
- [ ] Review `.vercelignore` to ensure unnecessary files aren't deployed

## 🔧 Configuration Files Created

1. **`vercel.json`** - Vercel deployment configuration
2. **`api/index.py`** - Serverless function entry point
3. **`.vercelignore`** - Files to exclude from deployment
4. **`runtime.txt`** - Python version specification

## 🧪 Testing Deployment

After deployment, test your endpoints:
```bash
# Health check
curl https://your-project.vercel.app/api/v1/health

# Root endpoint
curl https://your-project.vercel.app/
```

## 📚 Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel Function Size Limits](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python#limitations)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)

## 🚨 Recommended Alternative

Given the size of your dependencies, consider:
1. **Railway** - Easy Docker deployment, larger limits
2. **Render** - Good for ML applications
3. **Fly.io** - Fast global deployment
4. **AWS Lambda** with container images (up to 10GB)

These platforms are better suited for ML/AI applications with large dependencies.

