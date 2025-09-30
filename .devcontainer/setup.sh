#!/bin/bash

# Update system
sudo apt-get update

# Install required system packages
sudo apt-get install -y curl wget jq git

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service in background
sudo systemctl start ollama || true

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 10

# Pull Llama 3.2 model (3B version for faster performance in codespace)
ollama pull llama3.2:3b

# Install Node.js dependencies for MCP
npm install -g @modelcontextprotocol/inspector

echo "Setup complete! All tools and models are ready."