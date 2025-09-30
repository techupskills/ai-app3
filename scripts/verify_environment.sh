#!/bin/bash

# TechCorp Enterprise AI Workshop - Environment Verification Script
# Verifies all required tools and dependencies are properly installed

set -e

echo "🏢 TechCorp Enterprise AI Workshop - Environment Verification"
echo "============================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Success/failure tracking
ALL_CHECKS_PASSED=true

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "✅ ${GREEN}$2${NC}"
    else
        echo -e "❌ ${RED}$2${NC}"
        ALL_CHECKS_PASSED=false
        if [ ! -z "$3" ]; then
            echo -e "   ${YELLOW}Fix: $3${NC}"
        fi
    fi
}

# Check Python version
echo "🐍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
        print_status 0 "Python $PYTHON_VERSION (✓ >= 3.9)"
    else
        print_status 1 "Python $PYTHON_VERSION (✗ < 3.9)" "Please upgrade to Python 3.9 or higher"
    fi
else
    print_status 1 "Python not found" "Please install Python 3.9 or higher"
fi

# Check pip
echo ""
echo "📦 Checking pip installation..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1 | cut -d' ' -f2)
    print_status 0 "pip $PIP_VERSION"
else
    print_status 1 "pip not found" "Please install pip"
fi

# Check critical Python packages
echo ""
echo "📚 Checking Python dependencies..."

REQUIRED_PACKAGES=(
    "requests"
    "fastapi"
    "uvicorn"
    "streamlit"
    "pandas"
    "numpy"
    "plotly"
    "pydantic"
    "httpx"
    "pyjwt"
    "sentence-transformers"
    "chromadb"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        VERSION=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
        print_status 0 "$package ($VERSION)"
    else
        print_status 1 "$package not installed" "Run: pip install $package"
    fi
done

# Check Docker
echo ""
echo "🐳 Checking Docker installation..."
if command -v docker &> /dev/null; then
    if docker --version &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_status 0 "Docker $DOCKER_VERSION"
        
        # Check if Docker daemon is running
        if docker ps &> /dev/null; then
            print_status 0 "Docker daemon is running"
        else
            print_status 1 "Docker daemon not running" "Start Docker Desktop or Docker service"
        fi
    else
        print_status 1 "Docker command failed" "Check Docker installation"
    fi
else
    print_status 1 "Docker not found" "Install Docker Desktop from docker.com"
fi

# Check Ollama
echo ""
echo "🦙 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n1 || echo "unknown")
    print_status 0 "Ollama ($OLLAMA_VERSION)"
    
    # Check if Ollama service is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_status 0 "Ollama service is running"
        
        # Check if Llama 3.2 model is available
        if ollama list | grep -q "llama3.2"; then
            print_status 0 "Llama 3.2 model is available"
        else
            print_status 1 "Llama 3.2 model not found" "Run: ollama pull llama3.2"
        fi
    else
        print_status 1 "Ollama service not running" "Run: ollama serve"
    fi
else
    print_status 1 "Ollama not found" "Install from ollama.ai"
fi

# Check Node.js (for development tools)
echo ""
echo "📦 Checking Node.js (optional)..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status 0 "Node.js $NODE_VERSION"
else
    print_status 1 "Node.js not found" "Install Node.js for additional development tools (optional)"
fi

# Check Git
echo ""
echo "📂 Checking Git installation..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    print_status 0 "Git $GIT_VERSION"
else
    print_status 1 "Git not found" "Install Git for version control"
fi

# Check VS Code
echo ""
echo "📝 Checking VS Code..."
if command -v code &> /dev/null; then
    print_status 0 "VS Code command line tools available"
else
    print_status 1 "VS Code CLI not found" "Install VS Code and enable shell command"
fi

# Check required directories
echo ""
echo "📁 Checking directory structure..."
REQUIRED_DIRS=(
    "scripts"
    "config" 
    "extra"
    "lab1"
    "lab2"
    "lab3"
    "lab4"
    "lab5"
    "lab6"
    "lab7"
    "lab8"
    "slides"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_status 0 "Directory: $dir"
    else
        print_status 1 "Directory missing: $dir" "Create directory: mkdir -p $dir"
    fi
done

# Check configuration files
echo ""
echo "⚙️  Checking configuration files..."
if [ -f "config/app_config.yaml" ]; then
    print_status 0 "Application configuration found"
else
    print_status 1 "app_config.yaml missing" "Configuration will be created during labs"
fi

if [ -f "requirements.txt" ]; then
    print_status 0 "Requirements file found"
else
    print_status 1 "requirements.txt missing" "Dependencies file will be created"
fi

# Final summary
echo ""
echo "============================================================="
if [ "$ALL_CHECKS_PASSED" = true ]; then
    echo -e "🎉 ${GREEN}Environment verification completed successfully!${NC}"
    echo -e "✅ ${GREEN}Ready to start the TechCorp Enterprise AI Workshop${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Navigate to lab1: cd lab1"
    echo "2. Follow the lab instructions in enterprise-ai-labs.md"
    echo "3. Use 'code -d' for diff merging with complete implementations"
else
    echo -e "⚠️  ${YELLOW}Environment verification completed with issues${NC}"
    echo -e "❌ ${RED}Please fix the issues above before starting the workshop${NC}"
    echo ""
    echo "Quick fixes:"
    echo "1. Install missing dependencies: pip install -r requirements.txt"
    echo "2. Start Ollama service: ollama serve"
    echo "3. Pull Llama model: ollama pull llama3.2"
    echo "4. Start Docker if needed"
fi

echo ""
echo "🏢 TechCorp Enterprise AI Workshop Environment Check Complete"
echo "============================================================="