#!/bin/bash

# FitTrack MCP - Quick Fix Script for macOS
# Run this in your FitTrack MCP directory

echo "======================================"
echo "FitTrack MCP - Installation Fix"
echo "======================================"
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Step 2: Install dependencies
echo "Step 2: Installing dependencies..."
echo "Running: pip3 install -r requirements.txt"
echo ""
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✓ Dependencies installed successfully"
echo ""

# Step 3: Test the MCP server
echo "Step 3: Testing MCP server..."
echo "Running a quick test (will timeout after 3 seconds)..."
echo ""

timeout 3s python3 fittrack_mcp.py &> /dev/null
TEST_EXIT=$?

if [ $TEST_EXIT -eq 124 ]; then
    # Timeout means it started successfully (124 is timeout exit code)
    echo "✓ MCP server started successfully"
elif [ $TEST_EXIT -eq 0 ]; then
    echo "✓ MCP server ran successfully"
else
    echo "⚠️  MCP server test had issues (exit code: $TEST_EXIT)"
    echo "   This might be normal. Let's continue..."
fi
echo ""

# Step 4: Get the correct path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MCP_FILE="${SCRIPT_DIR}/fittrack_mcp.py"

echo "Step 4: Configuration Information"
echo "======================================"
echo ""
echo "Your MCP server is located at:"
echo "$MCP_FILE"
echo ""
echo "Your Claude Desktop config should be:"
echo "~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "======================================"
echo "Copy this configuration:"
echo "======================================"
echo ""
cat << EOF
{
  "mcpServers": {
    "fittrack": {
      "command": "python3",
      "args": [
        "$MCP_FILE"
      ]
    }
  }
}
EOF
echo ""
echo "======================================"
echo ""
echo "Next Steps:"
echo "1. Copy the configuration above"
echo "2. Open: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "3. Paste the configuration (replace contents or merge if you have other servers)"
echo "4. Save the file"
echo "5. Completely quit and restart Claude Desktop"
echo ""
echo "To test after restarting Claude:"
echo "Ask Claude: 'Use the ping tool to test FitTrack'"
echo ""
echo "======================================"
