#!/bin/bash

# Intrabot-AI Startup Script
echo "🤖 Starting Intrabot-AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Setting up virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "⬇️  Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your actual API keys before running the server."
    echo "   Especially set your GEMINI_API_KEY"
fi

# Initialize database if needed
if [ ! -d "offline-org-chatbot/.chromadb" ]; then
    echo "🗄️  Initializing database..."
    python init_db.py
else
    echo "✅ Database already exists"
fi

# Start the FastAPI server
echo "🚀 Starting FastAPI server..."
echo "   Server will be available at: http://127.0.0.1:8000"
echo "   API documentation at: http://127.0.0.1:8000/docs"
echo "   Frontend interface at: http://127.0.0.1:8000/static/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn api:app --host 127.0.0.1 --port 8000 --reload
