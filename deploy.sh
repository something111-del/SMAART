#!/bin/bash

# SMAART Deployment Script
# This script deploys the entire SMAART platform

set -e

echo "🚀 SMAART Deployment Script"
echo "=============================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}❌ Please edit .env with your API keys before continuing!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment file found${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker Compose is installed${NC}"

# Build and start services
echo ""
echo "📦 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."

if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Services are running${NC}"
else
    echo -e "${RED}❌ Some services failed to start${NC}"
    docker-compose logs
    exit 1
fi

# Show service URLs
echo ""
echo "=============================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=============================="
echo ""
echo "📍 Service URLs:"
echo "   API:          http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Nginx:        http://localhost"
echo "   PostgreSQL:   localhost:5432"
echo "   Redis:        localhost:6379"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "🔄 Restart services:"
echo "   docker-compose restart"
echo ""
