# SMAART AWS Infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-2"
}

# Use specific Ubuntu 22.04 AMI for us-east-2
locals {
  ami_id = "ami-0ea3c35c5c3284d82"  # Ubuntu 22.04 LTS in us-east-2
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = "smaart-vpc" }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "smaart-igw" }
}

# Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-2a"
  map_public_ip_on_launch = true
  tags                    = { Name = "smaart-subnet" }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  tags = { Name = "smaart-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "smaart" {
  name   = "smaart-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 30000
    to_port     = 30000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "smaart-sg" }
}

# EC2 Instance
resource "aws_instance" "smaart" {
  ami                    = local.ami_id
  instance_type          = "t3.large"  # 8GB RAM, 2 vCPUs
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.smaart.id]
  key_name               = "smaart-key"

  root_block_device {
    volume_size = 120
    volume_type = "gp3"
  }

  user_data = file("${path.module}/k3s-install.sh")

  tags = { Name = "smaart-server" }
}

# Elastic IP
resource "aws_eip" "smaart" {
  instance = aws_instance.smaart.id
  domain   = "vpc"
  tags     = { Name = "smaart-eip" }
}

# Outputs
output "instance_id" {
  value = aws_instance.smaart.id
}

output "public_ip" {
  value = aws_eip.smaart.public_ip
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/smaart-key.pem ubuntu@${aws_eip.smaart.public_ip}"
}

output "api_url" {
  value = "http://${aws_eip.smaart.public_ip}:8000"
}
