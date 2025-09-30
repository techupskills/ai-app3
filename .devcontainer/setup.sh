#!/bin/bash
set -e

echo "🏢 Setting up TechCorp Enterprise AI Workshop Environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd /workspaces/ai-app3 || cd /workspace || cd $(pwd)
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

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