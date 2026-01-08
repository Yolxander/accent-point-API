# Railway Deployment Guide for accent-point-API

## 🚂 Railway Deployment Options

Railway supports **two main deployment methods**:

1. **GitHub Integration** (Recommended) - Automatic deployments from your GitHub repository
2. **Docker Image** - Manual deployment using Docker images

---

## 📦 Option 1: GitHub Integration (Recommended)

This is the **easiest and most common** method. Railway will automatically:
- Detect your Dockerfile
- Build and deploy on every push to your repository
- Set up automatic deployments

### Prerequisites
1. Push your code to GitHub (if not already)
2. Create a Railway account at [railway.app](https://railway.app)

### Step-by-Step Deployment

#### 1. Create Railway Project
1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select your repository: `accent-point-API` (or the repo containing this project)
6. Railway will automatically detect the Dockerfile

#### 2. Configure Environment Variables
In Railway Dashboard → Your Service → Variables tab, add:

**Required Variables:**
```
ENVIRONMENT=production
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-role-key>
```

**Optional Variables (with defaults):**
```
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=<your-frontend-domain>
ALLOWED_HOSTS=<your-domain>
OPENVOICE_DEVICE=cpu
MAX_FILE_SIZE=52428800
TARGET_SAMPLE_RATE=22050
NORMALIZE_AUDIO=true
LOG_LEVEL=INFO
```

**Note:** Railway automatically sets `PORT` - don't override it unless needed.

#### 3. Deploy
- Railway will automatically start building and deploying
- Watch the build logs in the Railway dashboard
- Once deployed, Railway will provide a URL like: `https://your-project.up.railway.app`

#### 4. Configure Custom Domain (Optional)
1. Go to Settings → Networking
2. Click "Generate Domain" or add your custom domain
3. Update `ALLOWED_ORIGINS` and `ALLOWED_HOSTS` with your domain

---

## 🐳 Option 2: Docker Image Deployment

Use this method if you want to:
- Deploy without GitHub
- Use a private registry
- Have more control over the build process

### Step 1: Build Docker Image Locally

```bash
cd accent-point-API

# Build the image
docker build -t accent-point-api:latest .

# Tag for Railway (optional, if using Railway registry)
docker tag accent-point-api:latest railway.app/your-project:latest
```

### Step 2: Push to Railway

#### Using Railway CLI:

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize project:**
   ```bash
   railway init
   ```

4. **Link to existing project (or create new):**
   ```bash
   railway link
   ```

5. **Deploy:**
   ```bash
   railway up
   ```

#### Using Railway Dashboard:

1. Create a new project in Railway
2. Select "Empty Project"
3. Go to Settings → Source
4. Choose "Docker Image"
5. Push your image to a registry (Docker Hub, GitHub Container Registry, etc.)
6. Enter the image URL in Railway

---

## 🔧 Configuration Files

### `railway.json`
Railway configuration file (already created):
- Specifies Dockerfile path
- Sets start command
- Configures restart policy

### `Dockerfile`
Updated for Railway:
- Uses Python 3.11
- Handles Railway's `PORT` environment variable
- Includes health check
- Optimized for production

### `.dockerignore`
Excludes unnecessary files from Docker build:
- Virtual environments
- Test files
- Temporary files
- Development files

---

## 🌐 Environment Variables Setup

### In Railway Dashboard:

1. Go to your service
2. Click on **"Variables"** tab
3. Add each variable:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ENVIRONMENT` | Yes | Environment mode | `production` |
| `SUPABASE_URL` | Yes | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Yes | Supabase anonymous key | `eyJhbGc...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Supabase service role key | `eyJhbGc...` |
| `ALLOWED_ORIGINS` | Recommended | CORS allowed origins | `https://yourdomain.com` |
| `ALLOWED_HOSTS` | Recommended | Allowed hosts | `yourdomain.com` |
| `OPENVOICE_DEVICE` | No | Device for processing | `cpu` |
| `MAX_FILE_SIZE` | No | Max upload size (bytes) | `52428800` |
| `LOG_LEVEL` | No | Logging level | `INFO` |

**Note:** Railway automatically provides:
- `PORT` - Don't set this manually
- `RAILWAY_ENVIRONMENT` - Railway environment name
- `RAILWAY_PROJECT_ID` - Your project ID

---

## 🚀 Post-Deployment

### 1. Test Your API

```bash
# Health check
curl https://your-project.up.railway.app/api/v1/health

# Root endpoint
curl https://your-project.up.railway.app/
```

### 2. Update Frontend

Update your Next.js frontend to use the Railway URL:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-project.up.railway.app';
```

### 3. Monitor Logs

View logs in Railway Dashboard:
- Go to your service
- Click "Deployments" → Select a deployment → "View Logs"

Or use Railway CLI:
```bash
railway logs
```

### 4. Set Up Custom Domain

1. Railway Dashboard → Settings → Networking
2. Add your domain
3. Update DNS records as instructed
4. Update `ALLOWED_ORIGINS` and `ALLOWED_HOSTS`

---

## 📊 Railway Features

### Automatic Deployments
- Deploys on every push to main/master branch
- Can configure branch-specific deployments
- Rollback to previous deployments easily

### Environment Management
- Separate environments (production, staging, etc.)
- Environment-specific variables
- Preview deployments for PRs

### Scaling
- Railway automatically scales based on traffic
- Can configure resource limits
- Pay-as-you-go pricing

### Monitoring
- Built-in logs viewer
- Metrics dashboard
- Health check monitoring

---

## 🔍 Troubleshooting

### Build Fails

**Issue:** Docker build fails
**Solutions:**
- Check build logs in Railway dashboard
- Verify Dockerfile syntax
- Ensure all dependencies are in requirements.txt
- Check for missing system packages

### Application Won't Start

**Issue:** Service crashes on startup
**Solutions:**
- Check application logs: `railway logs`
- Verify environment variables are set
- Ensure PORT is not manually set (Railway provides it)
- Check if all required services (Supabase) are accessible

### Health Check Fails

**Issue:** Health check endpoint returns error
**Solutions:**
- Verify `/api/v1/health` endpoint works locally
- Check if application is binding to `0.0.0.0` and correct port
- Review health check implementation

### Large Dependencies

**Issue:** Build takes too long or fails due to size
**Solutions:**
- Railway has generous limits, but if issues occur:
  - Use multi-stage Docker builds
  - Cache dependencies properly
  - Consider using Railway's build cache

---

## 💰 Pricing

Railway offers:
- **Free tier**: $5 credit/month
- **Pay-as-you-go**: Only pay for what you use
- **Hobby plan**: $5/month for more resources
- **Pro plan**: $20/month for teams

For ML/AI applications with large dependencies, Railway is cost-effective compared to Vercel.

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway CLI Reference](https://docs.railway.app/develop/cli)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub (for GitHub integration)
- [ ] Railway account created
- [ ] Project created in Railway
- [ ] Environment variables configured
- [ ] Build successful
- [ ] Health check passing
- [ ] API endpoints tested
- [ ] Frontend updated with new API URL
- [ ] Custom domain configured (if needed)
- [ ] Monitoring set up

---

## 🎯 Quick Start Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize (if using CLI deployment)
railway init

# Link to project
railway link

# View logs
railway logs

# Open dashboard
railway open
```

---

## 🆚 GitHub vs Docker Image

| Feature | GitHub Integration | Docker Image |
|---------|-------------------|--------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Auto Deploy** | ✅ Yes | ❌ Manual |
| **Setup Time** | 5 minutes | 15+ minutes |
| **Best For** | Most users | Advanced users |
| **CI/CD** | Built-in | Manual |

**Recommendation:** Use GitHub Integration unless you have specific requirements for Docker image deployment.

