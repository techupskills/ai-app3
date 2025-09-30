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

# Critical packages for workshop core functionality
CRITICAL_PACKAGES=(
    "requests"
    "fastapi" 
    "uvicorn"
    "streamlit"
    "pandas"
    "numpy"
    "plotly"
    "pydantic"
    "httpx"
    "jwt"
    "chromadb"
)

# Optional packages that may have version conflicts
OPTIONAL_PACKAGES=(
    "sentence_transformers"
)

echo "Critical packages:"
for package in "${CRITICAL_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        VERSION=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
        print_status 0 "$package ($VERSION)"
    else
        print_status 1 "$package not installed" "Run: pip install $package"
    fi
done

echo ""
echo "Optional packages:"
for package in "${OPTIONAL_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        VERSION=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
        print_status 0 "$package ($VERSION)"
    else
        # Don't fail for optional packages
        echo -e "⚠️  ${YELLOW}$package not available (optional for advanced features)${NC}"
    fi
done

# Check Docker
echo ""
echo "🐳 Checking Docker installation..."
if command -v docker &> /dev/null; then
    if docker --version &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_status 0 "Docker $DOCKER_VERSION"
        
        # Check if Docker daemon is running (optional in Codespaces)
        if docker ps &> /dev/null; then
            print_status 0 "Docker daemon is running"
        else
            # In Codespaces, Docker might not be running by default - that's OK
            if [ -n "$CODESPACES" ]; then
                print_status 0 "Docker available (Codespaces environment)"
            else
                print_status 1 "Docker daemon not running" "Start Docker Desktop or Docker service"
            fi
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
        # Ollama might not be running yet - provide helpful guidance
        print_status 1 "Ollama service not running" "Run: ollama serve (or will be started by devcontainer setup)"
    fi
else
    # In devcontainer, Ollama will be installed by setup script
    if [ -n "$CODESPACES" ]; then
        print_status 1 "Ollama not found" "Will be installed by devcontainer setup"
    else
        print_status 1 "Ollama not found" "Install from ollama.ai"
    fi
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

# Count critical issues (ignore Docker/Ollama service status for devcontainer)
CRITICAL_ISSUES_COUNT=0
# Check if any critical packages failed (we set ALL_CHECKS_PASSED=false for critical package failures)
for package in "${CRITICAL_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        CRITICAL_ISSUES_COUNT=$((CRITICAL_ISSUES_COUNT + 1))
    fi
done

if [ "$CRITICAL_ISSUES_COUNT" -eq 0 ]; then
    echo -e "🎉 ${GREEN}Environment verification completed successfully!${NC}"
    echo -e "✅ ${GREEN}Ready to start the TechCorp Enterprise AI Workshop${NC}"
    
    # Show minor issues that don't block the workshop
    if [ "$ALL_CHECKS_PASSED" != true ]; then
        echo ""
        echo -e "📝 ${YELLOW}Minor issues detected (workshop can still proceed):${NC}"
        echo "• Docker daemon not running (will be available in devcontainer)"
        echo "• Ollama service not running (will be started by devcontainer setup)"
        echo "• Some optional packages may have version conflicts"
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Navigate to lab1: cd lab1"
    echo "2. Follow the lab instructions in enterprise-ai-labs.md"
    echo "3. Use 'code -d' for diff merging with complete implementations"
else
    echo -e "⚠️  ${YELLOW}Environment verification completed with critical issues${NC}"
    echo -e "❌ ${RED}Please fix the critical issues before starting the workshop${NC}"
    echo ""
    echo "Critical fixes needed:"
    echo "1. Install missing dependencies: pip install -r requirements.txt"
    echo ""
    echo "Optional fixes:"
    echo "2. Start Ollama service: ollama serve (or will be handled by devcontainer)"
    echo "3. Pull Llama model: ollama pull llama3.2 (or will be handled by devcontainer)"
    echo "4. Start Docker if needed (available in devcontainer)"
fi

echo ""
echo "🏢 TechCorp Enterprise AI Workshop Environment Check Complete"
echo "============================================================="