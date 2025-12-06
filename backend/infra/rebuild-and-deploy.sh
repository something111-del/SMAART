#!/bin/bash
# SMAART EC2 Direct Build and Deploy Script
# Builds Docker image directly on EC2 to avoid disk space issues

set -e

EC2_IP="52.14.181.115"
SSH_KEY="~/.ssh/smaart-key.pem"

echo "🚀 Building and Deploying SMAART on EC2..."

# Step 1: Copy application code to EC2
echo "📦 Copying application code to EC2..."
rsync -avz --exclude 'node_modules' --exclude '.git' --exclude '__pycache__' \
  -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
  /Users/karepallimahesh/Desktop/py/SMAART/backend/ \
  ubuntu@$EC2_IP:~/smaart-backend/

echo "✅ Code copied successfully"

# Step 2: Build Docker image on EC2
echo "🔨 Building Docker image on EC2..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
cd ~/smaart-backend

# Create Dockerfile in the backend directory
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

# Build the image
sudo docker build -t smaart-api:latest .

echo "✅ Docker image built successfully"
ENDSSH

# Step 3: Import image to k3s
echo "📥 Importing Docker image to k3s..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
# Import to k3s containerd
sudo docker save smaart-api:latest | sudo k3s ctr images import -

echo "✅ Image imported to k3s"
ENDSSH

# Step 4: Remove disk pressure taint
echo "🔧 Removing disk pressure taint..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Get node name
NODE_NAME=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')

# Remove disk pressure taint
kubectl taint nodes $NODE_NAME node.kubernetes.io/disk-pressure- || echo "Taint already removed"

echo "✅ Taint removed"
ENDSSH

# Step 5: Restart pods
echo "🔄 Restarting application pods..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Delete existing pods to force recreation
kubectl delete pods -n processing -l app=smaart-api --force --grace-period=0 || true
kubectl delete pods -n processing -l app=smaart-worker --force --grace-period=0 || true

echo "✅ Pods restarted"
ENDSSH

# Step 6: Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Wait for API pods
kubectl wait --for=condition=ready pod -l app=smaart-api -n processing --timeout=300s || echo "Timeout waiting for pods"

echo "✅ Deployment complete!"
ENDSSH

# Step 7: Show deployment status
echo "📊 Deployment Status:"
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

echo ""
echo "=== Disk Usage ==="
df -h /

echo ""
echo "=== Pods Status ==="
kubectl get pods -n processing
kubectl get pods -n default

echo ""
echo "=== Services ==="
kubectl get svc -n processing

echo ""
echo "=== Pod Logs (last 20 lines) ==="
POD_NAME=$(kubectl get pods -n processing -l app=smaart-api -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$POD_NAME" ]; then
    kubectl logs -n processing $POD_NAME --tail=20 || echo "No logs available yet"
else
    echo "No API pods running yet"
fi

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
