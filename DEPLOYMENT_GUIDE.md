# 🚀 DEPLOYMENT INSTRUCTIONS

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `SMAART`
3. Description: "AI-powered real-time social media analytics and trend summarization platform"
4. Visibility: Public
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## Step 2: Push Code to GitHub

```bash
# Navigate to project directory
cd /Users/karepallimahesh/Desktop/py/SMAART

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/SMAART.git

# Push code
git push -u origin main
```

## Step 3: Set Up GitHub Secrets

Go to: `https://github.com/YOUR_USERNAME/SMAART/settings/secrets/actions`

Add these secrets (click "New repository secret"):

### Required Secrets:
1. **AWS_ACCESS_KEY_ID**: Your NEW rotated AWS access key
2. **AWS_SECRET_ACCESS_KEY**: Your NEW rotated AWS secret key
3. **DOCKER_USERNAME**: `karepalli`
4. **DOCKER_PASSWORD**: Your Docker Hub password/token
5. **TWITTER_API_KEY**: `1909767787435958272-Nn0OfOwi39L163ymmWgxvGzp3synem`
6. **TWITTER_API_SECRET**: `c6JcKX2VCJjLyAtJRDHa1KCgbCvKA5B7oO23QV6VOYAZb`
7. **NEWS_API_KEY**: `4efd030adad64c01bad1c8392a70c0c5`

## Step 4: Deploy Frontend to Vercel

### Option A: Vercel Dashboard (Easiest)
1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository: `SMAART`
4. Framework Preset: Vite
5. Root Directory: `frontend`
6. Build Command: `npm run build`
7. Output Directory: `dist`
8. Add Environment Variable:
   - Name: `VITE_API_URL`
   - Value: `http://YOUR_EC2_IP` (will update after backend deployment)
9. Click "Deploy"

### Option B: Vercel CLI
```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Set environment variable
vercel env add VITE_API_URL production
# Enter: http://YOUR_EC2_IP (update after backend deployment)
```

### Your Vercel URL will be:
`https://smaart-XXXXX.vercel.app` (Vercel will provide the exact URL)

## Step 5: Update README with Live Links

After deployment, update README.md:

```bash
# Edit README.md
nano README.md

# Find this line:
[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://smaart-intelligence.vercel.app)

# Replace with your actual Vercel URL:
[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://YOUR_ACTUAL_VERCEL_URL)

# Also update the "Live Demo" section with your URLs

# Commit and push
git add README.md
git commit -m "Update README with live deployment URLs"
git push
```

## Step 6: Deploy Backend to AWS (Optional - for full deployment)

### Prerequisites:
- AWS CLI configured with NEW rotated credentials
- Terraform installed
- kubectl installed

### Steps:
```bash
cd backend/infra/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply (creates EC2 instance with k3s)
terraform apply

# Note the EC2 public IP from output
# Example: 3.145.123.45

# Update Vercel environment variable
vercel env add VITE_API_URL production
# Enter: http://3.145.123.45
```

## Step 7: Verify Deployment

### Frontend (Vercel)
- Visit: `https://YOUR_VERCEL_URL`
- Should see SMAART landing page
- Search functionality will work once backend is deployed

### Backend (AWS - if deployed)
- API Docs: `http://YOUR_EC2_IP/docs`
- Health Check: `http://YOUR_EC2_IP/api/v1/health`
- Grafana: `http://YOUR_EC2_IP:3000`

## 📝 Important Notes

### Security Reminders:
1. ✅ **NEVER** commit `.env` file
2. ✅ Use GitHub Secrets for all credentials
3. ✅ Rotate AWS keys immediately if exposed
4. ✅ Keep Docker Hub password secure

### Cost Monitoring:
- Check AWS billing dashboard regularly
- Set up billing alerts
- Monitor free tier usage

### Next Steps After Deployment:
1. Test the live application
2. Share the Vercel URL on your resume
3. Add screenshots to README
4. Create a demo video (optional)
5. Write a blog post about the project (optional)

## 🎯 Resume-Ready Links

Once deployed, you'll have:

1. **Live Demo**: `https://YOUR_VERCEL_URL`
2. **GitHub Repo**: `https://github.com/YOUR_USERNAME/SMAART`
3. **API Documentation**: `http://YOUR_EC2_IP/docs` (if backend deployed)
4. **Monitoring Dashboard**: `http://YOUR_EC2_IP:3000` (if backend deployed)

Add these to your resume under projects section!

## 🆘 Troubleshooting

### Vercel Deployment Fails
```bash
# Check build logs in Vercel dashboard
# Common issues:
# - Missing dependencies: Run `npm install` locally first
# - Build errors: Run `npm run build` locally to test
```

### GitHub Push Fails
```bash
# If authentication fails, use Personal Access Token:
# 1. Go to GitHub Settings → Developer settings → Personal access tokens
# 2. Generate new token with 'repo' scope
# 3. Use token as password when pushing
```

### AWS Deployment Issues
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Terraform state
cd backend/infra/terraform
terraform show
```

## 📧 Need Help?

- GitHub Issues: `https://github.com/YOUR_USERNAME/SMAART/issues`
- Check QUICKSTART.md for local development
- Review ARCHITECTURE.md for system design

---

**Ready to deploy?** Follow the steps above in order! 🚀
