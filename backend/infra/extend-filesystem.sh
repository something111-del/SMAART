#!/bin/bash
# Extend filesystem after EBS volume expansion

set -e

EC2_IP="52.14.181.115"
SSH_KEY="~/.ssh/smaart-key.pem"

echo "🔧 Extending filesystem to use new disk space..."

# Wait for SSH to be available
echo "Waiting for EC2 instance to be accessible..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if ssh -i $SSH_KEY -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$EC2_IP "echo 'Connected'" 2>/dev/null; then
        echo "✅ EC2 instance is accessible"
        break
    fi
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts - waiting..."
    sleep 10
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Failed to connect to EC2 instance"
    exit 1
fi

# Extend the filesystem
ssh -i $SSH_KEY -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'ENDSSH'
echo "Current disk usage:"
df -h /

echo ""
echo "Growing partition..."
sudo growpart /dev/nvme0n1 1 || echo "Partition already at maximum size"

echo ""
echo "Resizing filesystem..."
sudo resize2fs /dev/nvme0n1p1 || sudo xfs_growfs / || echo "Filesystem resize attempted"

echo ""
echo "New disk usage:"
df -h /

echo ""
echo "✅ Filesystem extended successfully!"
ENDSSH

echo ""
echo "✅ Disk expansion complete!"
