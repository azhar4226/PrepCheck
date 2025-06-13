#!/bin/bash

# PrepCheck Development Setup Script
echo "🚀 PrepCheck Development Setup"
echo "================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the PrepCheck root directory"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start backend services
echo ""
echo "🐳 Starting backend services with Docker..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo "✅ Backend services are running"
else
    echo "❌ Failed to start backend services"
    exit 1
fi

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# Start frontend development server
echo ""
echo "🎨 Starting frontend development server..."
echo "Frontend will be available at: http://localhost:3001"
echo "Backend API is available at: http://localhost:8000"
echo "Production frontend at: http://localhost"
echo ""
echo "📝 Test credentials:"
echo "Admin: admin@prepcheck.com / admin123"
echo "User: test@example.com / testpass123"
echo ""
echo "🛑 Press Ctrl+C to stop the frontend server"
echo "🛑 Use 'docker compose down' to stop backend services"
echo ""

# Start the frontend server (this will block)
npm run serve
