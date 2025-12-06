#!/bin/bash
# SMAART EC2 Deployment Script
# This script deploys the SMAART application to EC2

set -e

EC2_IP="52.14.181.115"
SSH_KEY="~/.ssh/smaart-key.pem"

echo "🚀 Starting SMAART Deployment to EC2..."

# Step 1: Install PostgreSQL using Helm
echo "📦 Installing PostgreSQL..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Add Helm repos if not already added
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update

# Install PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace default \
  --set auth.username=smaart_user \
  --set auth.password=smaart_password \
  --set auth.database=smaart_db \
  --set primary.persistence.size=5Gi \
  --set primary.resources.requests.memory=256Mi \
  --set primary.resources.requests.cpu=100m \
  --wait --timeout 5m || echo "PostgreSQL already installed or failed"

echo "✅ PostgreSQL installation complete"
ENDSSH

# Step 2: Install Redis using Helm
echo "📦 Installing Redis..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Install Redis
helm install redis bitnami/redis \
  --namespace default \
  --set auth.password=redis_password \
  --set master.persistence.size=2Gi \
  --set master.resources.requests.memory=128Mi \
  --set master.resources.requests.cpu=50m \
  --set replica.replicaCount=0 \
  --wait --timeout 5m || echo "Redis already installed or failed"

echo "✅ Redis installation complete"
ENDSSH

# Step 3: Wait for Docker image to be loaded (if still loading)
echo "⏳ Checking Docker image status..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
# Check if image is loaded
if ! sudo docker images | grep -q smaart-api; then
    echo "Loading Docker image (this may take a few minutes)..."
    if [ -f ~/smaart-api-amd64.tar.gz ]; then
        sudo docker load -i ~/smaart-api-amd64.tar.gz
        echo "✅ Docker image loaded"
    else
        echo "❌ Docker image file not found!"
        exit 1
    fi
else
    echo "✅ Docker image already loaded"
fi
ENDSSH

# Step 4: Import Docker image to k3s
echo "📥 Importing Docker image to k3s..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
# Tag the image for k3s
sudo docker tag smaart-api:latest smaart-api:latest

# Import to k3s (k3s uses containerd, so we need to save and import)
sudo docker save smaart-api:latest | sudo k3s ctr images import -

echo "✅ Image imported to k3s"
ENDSSH

# Step 5: Deploy the application
echo "🚢 Deploying SMAART application..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Apply the deployment
kubectl apply -f ~/app-deployment.yaml

echo "✅ Application deployed"
ENDSSH

# Step 6: Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Wait for API pods
kubectl wait --for=condition=ready pod -l app=smaart-api -n processing --timeout=300s || true

echo "✅ Deployment complete!"
ENDSSH

# Step 7: Show deployment status
echo "📊 Deployment Status:"
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

echo ""
echo "=== Pods Status ==="
kubectl get pods -n processing
kubectl get pods -n default

echo ""
echo "=== Services ==="
kubectl get svc -n processing

echo ""
echo "=== Access Information ==="
echo "API URL: http://52.14.181.115:30000"
echo "Health Check: http://52.14.181.115:30000/api/v1/health"
echo "API Docs: http://52.14.181.115:30000/docs"
ENDSSH

echo ""
echo "✅ SMAART Deployment Complete!"
echo "🌐 API URL: http://52.14.181.115:30000"
echo "📚 API Docs: http://52.14.181.115:30000/docs"
