#!/bin/bash
# Python environment setup for TechCorp AI Workshop in GitHub Codespaces

set -e

echo "🐍 Setting up Python environment for TechCorp AI Workshop..."

# Check if we're in Codespaces
if [ -n "$CODESPACES" ]; then
    echo "📍 Detected GitHub Codespaces environment"
    WORKSHOP_DIR="/workspaces/ai-app3"
else
    echo "📍 Local development environment"
    WORKSHOP_DIR=$(pwd)
fi

cd "$WORKSHOP_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔨 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Verify installation
echo "🔍 Verifying critical packages..."
python -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python executable: {sys.executable}')

critical_packages = ['requests', 'fastapi', 'uvicorn', 'streamlit', 'pandas', 'numpy', 'plotly', 'pydantic', 'httpx', 'jwt', 'chromadb']
failed = []

for pkg in critical_packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg}')
        failed.append(pkg)

if failed:
    print(f'\\n❌ Failed to import: {failed}')
    sys.exit(1)
else:
    print('\\n🎉 All critical packages installed successfully!')
"

echo ""
echo "✅ Python environment setup complete!"
echo ""
echo "🎯 To use this environment:"
echo "   source venv/bin/activate"
echo ""
echo "🎯 To verify installation:"
echo "   source venv/bin/activate && ./scripts/verify_environment.sh"
echo ""
echo "🎯 To start Lab 1:"
echo "   source venv/bin/activate && cd lab1"