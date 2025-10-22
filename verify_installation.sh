#!/bin/bash

# FitTrack MCP - Verification Script
# This tests that everything is set up correctly

echo "======================================"
echo "FitTrack MCP - Installation Verification"
echo "======================================"
echo ""

# Test 1: Python version
echo "Test 1: Python Version"
echo "----------------------"
PYTHON_CMD="python3.11"

if command -v $PYTHON_CMD &> /dev/null; then
    VERSION=$($PYTHON_CMD --version)
    echo "✅ $VERSION found"
else
    echo "❌ python3.11 not found. Try 'python3' instead?"
    PYTHON_CMD="python3"
    VERSION=$($PYTHON_CMD --version)
    echo "   Using: $VERSION"
fi
echo ""

# Test 2: FastMCP package
echo "Test 2: FastMCP Package"
echo "----------------------"
if $PYTHON_CMD -c "import fastmcp" 2>/dev/null; then
    FASTMCP_VERSION=$($PYTHON_CMD -c "import fastmcp; print(fastmcp.__version__)" 2>/dev/null)
    echo "✅ FastMCP installed (version: $FASTMCP_VERSION)"
else
    echo "❌ FastMCP not installed"
    echo "   Run: $PYTHON_CMD -m pip install fastmcp"
    exit 1
fi
echo ""

# Test 3: MCP Server File
echo "Test 3: MCP Server File"
echo "----------------------"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MCP_FILE="${SCRIPT_DIR}/fittrack_mcp.py"

if [ -f "$MCP_FILE" ]; then
    echo "✅ Found: $MCP_FILE"
else
    echo "❌ MCP server file not found"
    exit 1
fi
echo ""

# Test 4: Server Syntax Check
echo "Test 4: Server Syntax Check"
echo "----------------------"
if $PYTHON_CMD -m py_compile "$MCP_FILE" 2>/dev/null; then
    echo "✅ No syntax errors"
else
    echo "❌ Syntax errors found in MCP server"
    exit 1
fi
echo ""

# Test 5: Quick Server Start Test
echo "Test 5: Server Start Test (3 second timeout)"
echo "----------------------"
timeout 3s $PYTHON_CMD "$MCP_FILE" &>/dev/null
EXIT_CODE=$?

if [ $EXIT_CODE -eq 124 ]; then
    echo "✅ Server started successfully (timeout is expected)"
elif [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Server started and exited cleanly"
else
    echo "⚠️  Server exited with code $EXIT_CODE"
    echo "   This might be normal for stdio mode"
fi
echo ""

# Test 6: Claude Desktop Config
echo "Test 6: Claude Desktop Config"
echo "----------------------"
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✅ Config file exists"

    if grep -q "fittrack" "$CLAUDE_CONFIG"; then
        echo "✅ FitTrack configuration found"

        if grep -q "$MCP_FILE" "$CLAUDE_CONFIG"; then
            echo "✅ Correct file path in config"
        else
            echo "⚠️  File path might be different in config"
        fi
    else
        echo "❌ FitTrack not configured in Claude Desktop"
        echo "   Add this to $CLAUDE_CONFIG:"
        echo ""
        cat << EOF
{
  "mcpServers": {
    "fittrack": {
      "command": "$PYTHON_CMD",
      "args": [
        "$MCP_FILE"
      ]
    }
  }
}
EOF
    fi
else
    echo "⚠️  Claude Desktop config not found at:"
    echo "   $CLAUDE_CONFIG"
    echo "   You may need to create it"
fi
echo ""

# Summary
echo "======================================"
echo "Summary"
echo "======================================"
echo ""
echo "Python Command: $PYTHON_CMD"
echo "MCP Server: $MCP_FILE"
echo ""
echo "If all tests passed, you should:"
echo "1. Make sure your Claude Desktop config uses:"
echo "   command: \"$PYTHON_CMD\""
echo "   args: [\"$MCP_FILE\"]"
echo ""
echo "2. Completely restart Claude Desktop (Cmd+Q)"
echo ""
echo "3. Test by asking Claude: 'Use the ping tool'"
echo ""
echo "======================================"
