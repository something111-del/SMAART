#!/bin/bash
set -e

# Configuration
KEY_PATH=~/.ssh/smaart-key.pem
# Read IP from file or use argument
SERVER_IP=$(cat public_ip.txt)
USER=ubuntu

echo "🚀 Deploying SMAART to EC2 ($SERVER_IP)..."

# 1. Create remote directory
echo "📂 Creating remote directory..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "mkdir -p ~/smaart/backend ~/smaart/infra"

# 2. Upload backend code
echo "uploading code..."
# Exclude venv, __pycache__, etc.
tar -czf backend.tar.gz backend/
scp -o StrictHostKeyChecking=no -i $KEY_PATH backend.tar.gz $USER@$SERVER_IP:~/smaart/
rm backend.tar.gz

# 3. Upload infrastructure files
echo "uploading infra..."
scp -o StrictHostKeyChecking=no -i $KEY_PATH backend/infra/k8s/app-deployment.yaml $USER@$SERVER_IP:~/smaart/infra/

# 4. Remote execution: Build and Deploy
echo "🔨 Building and Deploying on remote server..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "bash -s" << 'EOF'
    set -e
    cd ~/smaart
    
    echo "📦 Extracting code..."
    tar -xzf backend.tar.gz -C .
    
    echo "🐳 Building Docker image..."
    # Using k3s's built-in containerd directory if possible, or build with docker and import
    # For simplicity with k3s, we often build with docker and save/import or use k3s ctr
    # Assuming docker was installed by our user_data script
    
    docker build -t smaart-api:latest -f backend/services/api/Dockerfile .
    
    echo "📥 Importing image to k3s..."
    docker save smaart-api:latest | sudo k3s ctr images import -
    
    echo "☸️ Applying Kubernetes manifests..."
    # Wait for namespace if it doesn't exist yet (created by user_data script usually)
    kubectl create namespace processing || true
    
    # Apply
    kubectl apply -f infra/app-deployment.yaml
    
    echo "✅ Deployment successful!"
    kubectl get pods -n processing
EOF
