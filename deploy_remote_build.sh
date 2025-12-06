#!/bin/bash
set -e

KEY_PATH=~/.ssh/smaart-key.pem
# Read IP from file or argument
SERVER_IP=${1:-$(cat public_ip.txt)}
USER=ubuntu

echo "🚀 Starting DISK-SAFE Remote Deployment to $SERVER_IP..."

# 1. Cleanup Server (Ensure space)
echo "🧹 Cleaning Server..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "sudo docker system prune -a -f; sudo rm -f /swapfile; rm -rf ~/smaart-build"

# 2. Upload Source Code (Tiny)
echo "📂 Uploading Source Code..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "mkdir -p ~/smaart-build/backend"
scp -o StrictHostKeyChecking=no -i $KEY_PATH -r backend/* $USER@$SERVER_IP:~/smaart-build/backend/
scp -o StrictHostKeyChecking=no -i $KEY_PATH backend/infra/k8s/app-deployment.yaml $USER@$SERVER_IP:~/smaart-build/backend/infra/k8s/

# 3. Create Swap & Build on Server
echo "⚙️  Building on Server..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "bash -s" << 'EOF'
    set -e
    
    # Create 1GB Swap (Crucial for Build in Memory)
    if [ ! -f /swapfile ]; then
        echo "💾 Creating 1GB Swap..."
        sudo fallocate -l 1G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
    fi

    cd ~/smaart-build
    
    # Create Dockerfile in root (Simulate context)
    # We copied backend/* to ~/smaart-build/backend/
    # The Dockerfile is in backend/services/api/Dockerfile
    # We need to run build from root
    
    echo "🔨 Building Docker Image (Server-side)..."
    # We need to adjust context. 
    # The Dockerfile expects 'backend/requirements.txt'.
    # We are in ~/smaart-build.
    
    sudo docker build -t smaart-api:prod -f backend/services/api/Dockerfile .

    # Import to K3s (Directly from Docker Daemon? No, K3s uses containerd)
    # Option A: Save and Import (Double disk usage) -> Dangerous
    # Option B: Build directly into K3s? (Needs buildkit)
    # Option C: Use Docker Registry? (No registry)
    # Option D: Save/Import using minimal pipe:
    
    echo "📥 Piping Image to K3s..."
    sudo docker save smaart-api:prod | sudo k3s ctr images import -

    # Deploy
    echo "☸️  Updating Kubernetes..."
    export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
    
    # Patch yaml to use Never pull
    sed -i 's/imagePullPolicy: IfNotPresent/imagePullPolicy: Never/g' ~/smaart-build/backend/infra/k8s/app-deployment.yaml
    sed -i 's/image: smaart-api:latest/image: smaart-api:prod/g' ~/smaart-build/backend/infra/k8s/app-deployment.yaml
    
    sudo kubectl apply -f ~/smaart-build/backend/infra/k8s/app-deployment.yaml
    sudo kubectl rollout restart deployment smaart-api -n processing
    sudo kubectl rollout restart deployment smaart-worker -n processing
    
    echo "✅ Remote Build & Deploy Complete!"
    
    # Cleanup Build Artifacts
    sudo docker system prune -f
    rm -rf ~/smaart-build
EOF
echo "🎉 Done!"
