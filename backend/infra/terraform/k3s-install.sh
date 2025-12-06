#!/bin/bash
# k3s Installation and SMAART Deployment Script
# This script runs on EC2 instance boot

set -e

echo "=== SMAART k3s Installation ==="

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y curl wget git docker.io

# Install k3s
curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --node-name smaart-node

# Wait for k3s to be ready
sleep 30

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Add Helm repos
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Create namespaces
kubectl create namespace ingestion || true
kubectl create namespace processing || true
kubectl create namespace ml-service || true
kubectl create namespace monitoring || true

# Install PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace processing \
  --set auth.username=smaart_user \
  --set auth.password=smaart_password \
  --set auth.database=smaart_db \
  --set primary.persistence.size=10Gi

# Install Redis
helm install redis bitnami/redis \
  --namespace processing \
  --set auth.password=redis_password \
  --set master.persistence.size=5Gi

# Install Prometheus + Grafana (DISABLED to save RAM)
# helm install loki-stack grafana/loki-stack \
#   --namespace monitoring \
#   --set grafana.enabled=true \
#   --set prometheus.enabled=true \
#   --set promtail.enabled=true

# Install Nginx Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

echo "=== k3s Installation Complete ==="
echo "Kubeconfig: /etc/rancher/k3s/k3s.yaml"
echo "kubectl get nodes"
echo "kubectl get pods --all-namespaces"
