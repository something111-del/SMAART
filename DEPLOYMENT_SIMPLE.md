# SMAART Backend - Lightweight Deployment

## Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)
Railway provides free tier with 500 hours/month and handles everything automatically.

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy from backend directory
cd backend
railway init
railway up
```

**Pros:**
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Built-in Redis
- ✅ Zero configuration
- ✅ Auto-scaling

### Option 2: Render
```bash
# Just connect your GitHub repo to Render
# It auto-detects the Dockerfile and deploys
```

### Option 3: Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
cd backend
fly launch
fly deploy
```

## Current Model Features ✅

Your model is already optimized with:
- **Lazy loading** - Model loads only when needed
- **Redis caching** - Summaries cached, no reprocessing
- **Auto cleanup** - Memory freed after each request
- **Query-driven** - Only processes what's requested
- **Early stopping** - Processes minimal data needed

## Environment Variables Needed

```env
REDIS_URL=redis://localhost:6379/0
PORT=8000
```

## Cost Comparison

| Platform | Free Tier | Paid (if needed) |
|----------|-----------|------------------|
| Railway  | 500 hrs/month | $5/month |
| Render   | 750 hrs/month | $7/month |
| Fly.io   | 3 VMs free | $1.94/month |
| EC2      | 750 hrs/month | $15-30/month (manual) |

## Recommendation

**Use Railway** - It's the simplest and your optimized model will work perfectly with their free Redis and auto-scaling.

The model you have now is production-ready and memory-efficient!
