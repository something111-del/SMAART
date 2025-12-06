#!/bin/bash
# Create new EC2 instance with AWS CLI
# Specs: t3.large (8GB RAM), 120GB storage

set -e

echo "🚀 Creating new SMAART EC2 instance..."

# Get VPC and subnet IDs from existing resources
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=smaart-vpc" --query 'Vpcs[0].VpcId' --output text)
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=smaart-subnet" --query 'Subnets[0].SubnetId' --output text)
SG_ID=$(aws ec2 describe-security-groups --filters "Name=tag:Name,Values=smaart-sg" --query 'SecurityGroups[0].GroupId' --output text)

echo "VPC ID: $VPC_ID"
echo "Subnet ID: $SUBNET_ID"
echo "Security Group ID: $SG_ID"

# AMI ID for Ubuntu 22.04 in us-east-2
AMI_ID="ami-0ea3c35c5c3284d82"

# Create instance
echo "Creating t3.large instance with 120GB storage..."
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.large \
  --key-name smaart-key \
  --subnet-id $SUBNET_ID \
  --security-group-ids $SG_ID \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":120,"VolumeType":"gp3","DeleteOnTermination":true}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=smaart-server}]' \
  --user-data file://k3s-install.sh \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "✅ Instance created: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get instance IP
INSTANCE_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "Instance IP: $INSTANCE_IP"

# Allocate and associate Elastic IP
echo "Allocating Elastic IP..."
ALLOCATION_ID=$(aws ec2 allocate-address --domain vpc --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=smaart-eip}]' --query 'AllocationId' --output text)
aws ec2 associate-address --instance-id $INSTANCE_ID --allocation-id $ALLOCATION_ID

# Get new Elastic IP
EIP=$(aws ec2 describe-addresses --allocation-ids $ALLOCATION_ID --query 'Addresses[0].PublicIp' --output text)

echo ""
echo "✅ New EC2 Instance Created Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Instance ID: $INSTANCE_ID"
echo "Instance Type: t3.large (8GB RAM, 2 vCPUs)"
echo "Storage: 120GB gp3"
echo "Public IP: $EIP"
echo "SSH Command: ssh -i ~/.ssh/smaart-key.pem ubuntu@$EIP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Waiting for instance to initialize (k3s installation)..."
echo "This may take 5-10 minutes. You can SSH in to monitor progress:"
echo "ssh -i ~/.ssh/smaart-key.pem ubuntu@$EIP 'tail -f /var/log/cloud-init-output.log'"
