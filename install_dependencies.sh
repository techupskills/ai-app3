#!/bin/bash
# Manual dependency installation script for TechCorp AI Workshop
# Run this if the devcontainer setup doesn't work properly

set -e

echo "🏢 TechCorp Enterprise AI Workshop - Manual Dependency Installation"
echo "================================================================="

# Update pip
echo "📦 Updating pip..."
python3 -m pip install --upgrade pip

# Install critical packages one by one for better error handling
echo "📚 Installing critical Python packages..."

CRITICAL_PACKAGES=(
    "requests>=2.31.0"
    "fastapi>=0.100.0" 
    "uvicorn>=0.20.0"
    "streamlit>=1.25.0"
    "pandas>=2.0.0"
    "numpy>=1.24.0"
    "plotly>=5.15.0"
    "pydantic>=2.0.0"
    "httpx>=0.25.0"
    "pyjwt>=2.8.0"
    "chromadb>=0.4.0"
)

for package in "${CRITICAL_PACKAGES[@]}"; do
    echo "Installing $package..."
    python3 -m pip install "$package" || echo "⚠️ Failed to install $package (continuing...)"
done

# Install optional packages
echo "📚 Installing optional packages..."
OPTIONAL_PACKAGES=(
    "transformers>=4.30.0"
    "huggingface-hub>=0.16.0"
    "pypdf>=3.15.0"
    "pyyaml>=6.0.0"
    "black>=23.0.0"
    "pylint>=2.17.0"
    "pytest>=7.4.0"
)

for package in "${OPTIONAL_PACKAGES[@]}"; do
    echo "Installing $package..."
    python3 -m pip install "$package" || echo "⚠️ Failed to install $package (optional)"
done

# Verify installation
echo "🔍 Verifying installation..."
python3 -c "
import sys
failed = []
critical_packages = ['requests', 'fastapi', 'uvicorn', 'streamlit', 'pandas', 'numpy', 'plotly', 'pydantic', 'httpx', 'jwt', 'chromadb']

for pkg in critical_packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg} - FAILED')
        failed.append(pkg)

if failed:
    print(f'\\n❌ Installation incomplete. Failed packages: {failed}')
    print('Try running: pip install -r requirements.txt')
    sys.exit(1)
else:
    print('\\n🎉 All critical packages installed successfully!')
    print('✅ Ready to start the TechCorp Enterprise AI Workshop')
"

echo ""
echo "🎯 Next steps:"
echo "1. Run: ./scripts/verify_environment.sh"
echo "2. Navigate to lab1: cd lab1"
echo "3. Follow the lab instructions in enterprise-ai-labs.md"