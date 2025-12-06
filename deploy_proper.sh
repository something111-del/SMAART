#!/bin/bash
set -e

KEY_PATH=~/.ssh/smaart-key.pem
SERVER_IP=$(cat public_ip.txt)
USER=ubuntu

echo "🚀 Starting PROPER Deployment Pipeline..."

# 1. Build for Linux/AMD64 (EC2 Architecture)
echo "🔨 Building Docker Image locally (linux/amd64)..."
docker buildx build --platform linux/amd64 -t smaart-api:prod -f backend/services/api/Dockerfile . --load

# 2. Save Image to File
echo "📦 Compressing Image..."
docker save smaart-api:prod | gzip > smaart-api-prod.tar.gz

# 3. Transfer to Server
echo "🚀 Uploading Image to EC2 (This may take a moment)..."
scp -o StrictHostKeyChecking=no -i $KEY_PATH smaart-api-prod.tar.gz $USER@$SERVER_IP:~/

# 4. Upload Infrastructure
echo "📂 Uploading Configs..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "mkdir -p ~/smaart/infra"
scp -o StrictHostKeyChecking=no -i $KEY_PATH backend/infra/k8s/app-deployment.yaml $USER@$SERVER_IP:~/smaart/infra/

# 5. Execute Remote Deployment
echo "⚙️  Deploying on Server..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "bash -s" << 'EOF'
    set -e
    
    # Enable Swap if missing (Critical for ML)
    if [ ! -f /swapfile ]; then
        echo "💾 Adding Swap..."
        sudo fallocate -l 4G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi

    # Import Image
    echo "📥 Loading Docker Image..."
    sudo k3s ctr images import smaart-api-prod.tar.gz

    # Deploy
    echo "☸️  Updating Kubernetes..."
    export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
    sudo kubectl create namespace processing || true
    
    # Patch Deployment to use the new image pull policy (Never pull, use local)
    # We update the yaml on the fly to ensure it uses the local image we just imported
    sed -i 's/imagePullPolicy: IfNotPresent/imagePullPolicy: Never/g' ~/smaart/infra/app-deployment.yaml
    sed -i 's/image: smaart-api:latest/image: smaart-api:prod/g' ~/smaart/infra/app-deployment.yaml
    
    sudo kubectl apply -f ~/smaart/infra/app-deployment.yaml
    
    # Restart pods to pick up new image
    sudo kubectl rollout restart deployment smaart-api -n processing
    sudo kubectl rollout restart deployment smaart-worker -n processing
    
    echo "✅ Backend Deployed Successfully!"
EOF

# Cleanup local
rm smaart-api-prod.tar.gz
echo "🎉 Deployment Pipeline Complete!"
