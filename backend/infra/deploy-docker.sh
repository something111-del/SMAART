#!/bin/bash
# Simple Docker Deployment (without k3s)
# Run SMAART API directly with Docker

set -e

EC2_IP="52.14.181.115"
SSH_KEY="~/.ssh/smaart-key.pem"

echo "🚀 Deploying SMAART with Docker..."

# Deploy using Docker directly
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
# Stop any existing containers
sudo docker stop smaart-api 2>/dev/null || true
sudo docker rm smaart-api 2>/dev/null || true

# Run the API container
sudo docker run -d \
  --name smaart-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -p 30000:8000 \
  -e DATABASE_URL="postgresql://smaart_user:smaart_password@postgres-postgresql.default.svc.cluster.local:5432/smaart_db" \
  -e REDIS_URL="redis://:redis_password@redis-master.default.svc.cluster.local:6379/0" \
  smaart-api:latest

echo "✅ Container started"

# Wait a few seconds for the container to start
sleep 5

# Check container status
sudo docker ps | grep smaart-api

# Check logs
echo ""
echo "=== Container Logs (last 20 lines) ==="
sudo docker logs --tail=20 smaart-api

echo ""
echo "✅ Deployment Complete!"
echo "🌐 API URL: http://52.14.181.115:8000"
echo "🌐 NodePort URL: http://52.14.181.115:30000"
echo "📚 API Docs: http://52.14.181.115:8000/docs"
ENDSSH

echo ""
echo "Testing API..."
curl -s http://52.14.181.115:8000/api/v1/health | jq . || echo "API not responding yet, please wait a moment"
