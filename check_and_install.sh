#!/bin/bash

# Check Python Version and Guide Installation

echo "======================================"
echo "FitTrack MCP - Python Version Check"
echo "======================================"
echo ""

echo "Checking your Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "Current Python version: $PYTHON_VERSION"
echo ""

# Extract major and minor version
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "❌ Your Python version is TOO OLD for FitTrack MCP"
    echo "   Required: Python 3.10 or higher"
    echo "   You have: Python $PYTHON_VERSION"
    echo ""
    echo "======================================"
    echo "How to Fix: Install Python 3.11+"
    echo "======================================"
    echo ""
    echo "OPTION 1: Install with Homebrew (Easiest)"
    echo "----------------------------------------"
    echo "1. Install Homebrew if you don't have it:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "2. Install Python 3.11:"
    echo "   brew install python@3.11"
    echo ""
    echo "3. Install FitTrack MCP packages:"
    echo "   python3.11 -m pip install fastmcp uvicorn[standard]"
    echo ""
    echo "4. Update your Claude config to use 'python3.11' instead of 'python3'"
    echo ""
    echo ""
    echo "OPTION 2: Download from python.org"
    echo "----------------------------------------"
    echo "1. Go to: https://www.python.org/downloads/"
    echo "2. Download Python 3.11 or 3.12 for macOS"
    echo "3. Install it"
    echo "4. Run: python3 -m pip install fastmcp uvicorn[standard]"
    echo ""
    echo "======================================"
    exit 1
else
    echo "✅ Your Python version is compatible!"
    echo ""
    echo "Installing FitTrack MCP packages..."
    python3 -m pip install --user fastmcp "uvicorn[standard]"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Installation successful!"
        echo ""
        echo "Next steps:"
        echo "1. Update your Claude Desktop config (if not done already)"
        echo "2. Restart Claude Desktop completely (Cmd+Q)"
        echo "3. Test by asking Claude: 'Use the ping tool'"
    else
        echo ""
        echo "❌ Installation failed. Check the error above."
    fi
fi
