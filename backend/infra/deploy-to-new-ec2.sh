#!/bin/bash
# Deploy SMAART to new EC2 instance with optimized model

set -e

EC2_IP="3.145.166.181"
SSH_KEY="~/.ssh/smaart-key.pem"

echo "🚀 Deploying SMAART to EC2 (8GB RAM, 120GB storage)..."

# Step 1: Copy application code
echo "📦 Copying application code..."
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude '__pycache__' --exclude '.terraform' \
  -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
  /Users/karepallimahesh/Desktop/py/SMAART/backend/ \
  ubuntu@$EC2_IP:~/smaart-backend/

echo "✅ Code copied"

# Step 2: Install dependencies and build Docker image
echo "🔨 Building Docker image on EC2..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
cd ~/smaart-backend

# Create optimized Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy application code
COPY . /app/backend

# Expose port
EXPOSE 8000

ENV PYTHONPATH=/app

# Run application
CMD ["uvicorn", "backend.services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build Docker image
sudo docker build -t smaart-api:latest .

echo "✅ Docker image built"
ENDSSH

# Step 3: Install and start Redis
echo "📦 Installing Redis..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
# Install Redis
sudo apt-get update
sudo apt-get install -y redis-server

# Configure Redis
sudo sed -i 's/supervised no/supervised systemd/' /etc/redis/redis.conf
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo "✅ Redis installed and running"
ENDSSH

# Step 4: Deploy application
echo "🚢 Deploying application..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
# Stop any existing containers
sudo docker stop smaart-api 2>/dev/null || true
sudo docker rm smaart-api 2>/dev/null || true

# Run the API container with Redis connection
sudo docker run -d \
  --name smaart-api \
  --restart unless-stopped \
  --network host \
  -e REDIS_URL="redis://localhost:6379/0" \
  smaart-api:latest

echo "✅ Application deployed"

# Wait for container to start
sleep 5

# Check status
sudo docker ps | grep smaart-api
echo ""
echo "Container logs:"
sudo docker logs --tail=30 smaart-api
ENDSSH

echo ""
echo "✅ SMAART Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 API URL: http://3.145.166.181:8000"
echo "📚 API Docs: http://3.145.166.181:8000/docs"
echo "🔍 Health Check: http://3.145.166.181:8000/api/v1/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Testing API..."
sleep 3
curl -s http://3.145.166.181:8000/api/v1/health | jq . || echo "API starting up, try again in 30 seconds"
