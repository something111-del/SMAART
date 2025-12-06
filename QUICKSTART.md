# SMAART - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- AWS CLI configured
- Git

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/SMAART.git
cd SMAART
```

### 2. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required credentials:
- `TWITTER_API_KEY` and `TWITTER_API_SECRET`
- `NEWS_API_KEY`
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- `DOCKER_USERNAME` and `DOCKER_PASSWORD`

### 3. Local Development

#### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run API server
cd services/api
python main.py
```

API will be available at: http://localhost:8000  
Swagger docs at: http://localhost:8000/docs

#### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4. Deploy to Production

#### Deploy Backend to AWS
```bash
# 1. Initialize Terraform
cd backend/infra/terraform
terraform init
terraform apply

# 2. Note the EC2 public IP from output
# 3. Update frontend/.env with API URL
```

#### Deploy Frontend to Vercel
```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel deploy --prod

# Set environment variable
vercel env add VITE_API_URL
# Enter: http://YOUR_EC2_IP
```

### 5. Verify Deployment

- **Frontend**: https://YOUR_PROJECT.vercel.app
- **Backend API**: http://YOUR_EC2_IP/docs
- **Grafana**: http://YOUR_EC2_IP:3000

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Documentation](http://YOUR_EC2_IP/docs)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🔧 Troubleshooting

### Backend Issues
```bash
# Check API logs
docker logs smaart-api

# Check worker logs
docker logs smaart-workers
```

### Frontend Issues
```bash
# Clear cache and rebuild
rm -rf node_modules dist
npm install
npm run build
```

### Database Issues
```bash
# Connect to PostgreSQL
docker exec -it smaart-postgres psql -U smaart_user -d smaart_db

# Check tables
\dt
```

## 🎯 Next Steps

1. ✅ Set up GitHub Secrets for CI/CD
2. ✅ Configure custom domain (optional)
3. ✅ Set up monitoring alerts
4. ✅ Add more data sources

## 📧 Support

Open an issue on GitHub for questions or bug reports.
