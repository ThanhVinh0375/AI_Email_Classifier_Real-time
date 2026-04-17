#!/bin/bash

# Deployment script for AI Email Classifier

set -e  # Exit on error

echo "🚀 Deploying AI Email Classifier..."
echo "===================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Check environment
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example and configure:"
    echo "   cp .env.example .env"
    exit 1
fi

# Load environment
set -a
source .env
set +a

# Create credentials directory
if [ ! -d credentials ]; then
    mkdir -p credentials
    echo "⚠️  Created credentials directory. Add service-account-key.json"
fi

echo "📦 Building Docker images..."
docker-compose build

echo "🔧 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check MongoDB
if docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✓ MongoDB is healthy"
else
    echo "⚠️  MongoDB not ready yet"
fi

# Check API
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ API is healthy"
else
    echo "⚠️  API not ready yet"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Services:"
echo "  • API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • MongoDB: localhost:27017"
echo "  • Redis: localhost:6379"
echo "  • Adminer: http://localhost:8080"
echo ""
echo "View logs: docker-compose logs -f api"
echo "Stop services: docker-compose down"
