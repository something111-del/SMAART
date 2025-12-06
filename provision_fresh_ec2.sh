#!/bin/bash
set -e
IP=${1:-$(cat public_ip.txt)}
KEY=~/.ssh/smaart-key.pem

echo "🚀 Provisioning New Server at $IP..."
echo "⏳ Waiting for SSH to be ready..."

# Loop until SSH is ready
until ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i $KEY ubuntu@$IP "echo ready"; do
    echo "Waiting for ssh..."
    sleep 5
done

ssh -o StrictHostKeyChecking=no -i $KEY ubuntu@$IP "bash -s" << 'EOF'
    set -e
    echo "🔄 Updating System..."
    # Prevent interactive upgrades
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update
    
    echo "🐳 Installing Docker..."
    sudo apt-get install -y docker.io unzip
    sudo usermod -aG docker ubuntu
    
    echo "☸️ Installing K3s (Lightweight Kubernetes)..."
    # Install without starting agent yet to avoid race conditions? No, standard install is fine.
    curl -sfL https://get.k3s.io | sh -
    
    echo "🔧 Configuring Permissions..."
    mkdir -p ~/.kube
    sudo chmod 644 /etc/rancher/k3s/k3s.yaml
    sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
    sudo chown ubuntu:ubuntu ~/.kube/config
    
    echo "💾 Setting up 4GB Swap (Essential for Stability)..."
    if [ ! -f /swapfile ]; then
        sudo fallocate -l 4G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi
    
    echo "✅ Server Infrastructure Ready!"
EOF
