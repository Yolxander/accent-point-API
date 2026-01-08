# Railway Quick Start Guide

## 🚀 Fastest Way to Deploy (GitHub Integration)

### Step 1: Push to GitHub
```bash
cd accent-point-API
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Select your repository
5. Railway will automatically:
   - Detect your Dockerfile
   - Build your application
   - Deploy it

### Step 3: Set Environment Variables
In Railway Dashboard → Your Service → Variables:

```
ENVIRONMENT=production
SUPABASE_URL=<your-url>
SUPABASE_ANON_KEY=<your-key>
SUPABASE_SERVICE_ROLE_KEY=<your-key>
ALLOWED_ORIGINS=<your-frontend-url>
```

### Step 4: Get Your URL
Railway will provide: `https://your-project.up.railway.app`

**That's it!** Your API is deployed. 🎉

---

## 📦 Deployment Methods Comparison

### GitHub Integration (Recommended) ✅
- **How it works:** Railway connects to your GitHub repo
- **Deployment:** Automatic on every push
- **Setup time:** 5 minutes
- **Best for:** Most users

### Docker Image
- **How it works:** Build and push Docker image manually
- **Deployment:** Manual via CLI or dashboard
- **Setup time:** 15+ minutes
- **Best for:** Advanced users, private registries

---

## 🔑 Key Points

1. **Railway automatically:**
   - Detects your Dockerfile
   - Sets the `PORT` environment variable
   - Builds and deploys on git push

2. **You need to set:**
   - Supabase credentials
   - CORS origins
   - Other environment variables

3. **No code changes needed:**
   - Your existing code works as-is
   - Dockerfile is already configured
   - Just push and deploy!

---

## 📚 Full Documentation

See `RAILWAY_DEPLOYMENT.md` for complete guide.

