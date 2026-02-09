#!/bin/bash

# VidyaMitra Backend Startup Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         VidyaMitra Backend - Starting...                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "❗ IMPORTANT: Edit .env and add your API keys before continuing!"
    echo "   Required: OPENAI_API_KEY"
    echo ""
    read -p "Press Enter after you've added your API keys..."
fi

# Install/update dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if OpenAI key is set
if grep -q "your-openai-api-key" .env; then
    echo ""
    echo "⚠️  WARNING: OPENAI_API_KEY not configured in .env"
    echo "   The API will not work without a valid OpenAI API key"
    echo ""
fi

# Start server
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Starting VidyaMitra API Server                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "API Server: http://localhost:8000"
echo "API Docs:   http://localhost:8000/docs"
echo "Health:     http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
