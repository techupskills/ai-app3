#!/bin/bash
set -e

echo "🏢 Setting up TechCorp Enterprise AI Workshop Environment..."

# Ensure we're in the right directory
WORKSHOP_DIR="/workspaces/ai-app3"
if [ ! -d "$WORKSHOP_DIR" ]; then
    WORKSHOP_DIR="/workspace"
fi
if [ ! -d "$WORKSHOP_DIR" ]; then
    WORKSHOP_DIR=$(pwd)
fi

echo "📁 Working in directory: $WORKSHOP_DIR"
cd "$WORKSHOP_DIR"

# Create and activate virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Verify critical packages
echo "🔍 Verifying critical packages..."
python -c "import requests, fastapi, uvicorn, streamlit, pandas, numpy, plotly, pydantic, httpx, jwt, chromadb" && echo "✅ All critical packages installed successfully"

# Make scripts executable
chmod +x scripts/verify_environment.sh
chmod +x setup_python_env.sh
chmod +x activate_workshop.sh
chmod +x install_dependencies.sh

# Install and setup Ollama
echo "🦙 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service in background
echo "🚀 Starting Ollama service..."
ollama serve &
sleep 10

# Pull required models
echo "📥 Downloading Llama 3.2 model..."
ollama pull llama3.2

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs data lab7 lab8

# Set permissions
chmod +x scripts/verify_environment.sh

echo "✅ TechCorp Enterprise AI Workshop setup complete!"
echo "🎯 Ready to start Lab 1"