#!/bin/bash

echo "🚀 Editorial System - Quick Start Script"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend .env file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend .env file..."
    cp frontend/.env.example frontend/.env
    echo "⚠️  Please edit frontend/.env with your configuration"
fi

# Build and start containers
echo "🏗️  Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T backend python manage.py migrate

echo ""
echo "✅ Setup complete!"
echo ""
echo "📌 Services are running:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend:  http://localhost:8000"
echo "   - Admin:    http://localhost:8000/admin"
echo ""
echo "🔧 Next steps:"
echo "   1. Create superuser: docker-compose exec backend python manage.py createsuperuser"
echo "   2. Configure ORCID credentials in backend/.env"
echo "   3. Configure AWS S3 credentials in backend/.env"
echo ""
echo "📚 Documentation:"
echo "   - API: docs/API.md"
echo "   - Deployment: docs/DEPLOYMENT.md"
echo "   - Architecture: docs/ARCHITECTURE.md"
