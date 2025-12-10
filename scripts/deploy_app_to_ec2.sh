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
tar --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='.DS_Store' --exclude='venv' -czf backend.tar.gz backend/
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
    
    # Add Swap for ML models (t3.micro has only 1GB RAM)
    if [ ! -f /swapfile ]; then
        echo "💾 Adding 4GB Swap file..."
        sudo fallocate -l 4G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi
    
    echo "🐳 Building Docker image..."
    # Check if docker is ready
    if ! command -v docker &> /dev/null; then
        echo "Docker not found, waiting/checking..."
        sudo apt-get update && sudo apt-get install -y docker.io
    fi
    
    sudo docker build -t smaart-api:latest -f backend/services/api/Dockerfile .
    
    echo "📥 Importing image to k3s..."
    sudo docker save smaart-api:latest | sudo k3s ctr images import -
    
    echo "☸️ Applying Kubernetes manifests..."
    export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
    
    # Wait for k3s
    until sudo kubectl get nodes; do echo "Waiting for k3s..."; sleep 5; done
    
    sudo kubectl create namespace processing || true
    
    # Apply
    sudo kubectl apply -f infra/app-deployment.yaml
    
    echo "✅ Deployment successful!"
    sudo kubectl get pods -n processing
EOF
