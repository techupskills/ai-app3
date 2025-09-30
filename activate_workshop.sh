#!/bin/bash
# Activate the TechCorp AI Workshop Python environment
# Usage: source activate_workshop.sh

if [ -d "venv" ]; then
    echo "⚡ Activating TechCorp AI Workshop environment..."
    source venv/bin/activate
    echo "✅ Environment activated!"
    echo "🎯 You can now run lab commands and scripts"
else
    echo "❌ Virtual environment not found!"
    echo "🔧 Run: ./setup_python_env.sh first"
fi