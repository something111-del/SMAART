#!/bin/bash
set -e
KEY_PATH=~/.ssh/smaart-key.pem
SERVER_IP=$(cat public_ip.txt)
USER=ubuntu

echo "🚀 Patching Kubernetes Manifests on ($SERVER_IP)..."

# Upload updated deployment file
echo "uploading yaml..."
scp -o StrictHostKeyChecking=no -i $KEY_PATH backend/infra/k8s/app-deployment.yaml $USER@$SERVER_IP:~/smaart/infra/

# Apply
echo "☸️ Applying updated manifests..."
ssh -o StrictHostKeyChecking=no -i $KEY_PATH $USER@$SERVER_IP "sudo kubectl apply -f ~/smaart/infra/app-deployment.yaml"

echo "✅ Patch applied!"
