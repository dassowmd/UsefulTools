#!/bin/bash

# Gmail Cleanup Development Startup Script
set -e

echo "🚀 Starting Gmail Cleanup Development Environment"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the gmail-cleanup-saas directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Python backend
echo "🐍 Setting up Python backend..."
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -e .

# Setup Frontend
echo "🌐 Setting up Vue.js frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Go back to root
cd ..

echo "✅ Setup complete!"
echo ""
echo "🎯 Starting services..."
echo "  Backend API: http://localhost:8000"
echo "  Frontend:    http://localhost:3000"
echo ""
echo "📊 API Documentation: http://localhost:8000/api/docs"
echo ""

# Start services directly
trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo "Starting Backend API server..."
source venv/bin/activate
python -m uvicorn src.gmail_cleanup.api.main:app --reload --host 0.0.0.0 --port 8000 &

echo "Starting Frontend development server..."
cd frontend
npm run dev &

echo "Both services started! Press Ctrl+C to stop all services."

# Wait for user to stop
wait