#!/bin/bash

# FitTrack MCP Server - Claude Desktop Setup Script

echo "=========================================="
echo "FitTrack MCP - Claude Desktop Setup"
echo "=========================================="
echo ""

# Get the absolute path to this script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MCP_FILE="${SCRIPT_DIR}/fittrack_mcp.py"

echo "✓ Found MCP server at: $MCP_FILE"
echo ""

# Detect OS and set config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CONFIG_FILE="${CONFIG_DIR}/claude_desktop_config.json"
    OS_NAME="macOS"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    CONFIG_DIR="$APPDATA/Claude"
    CONFIG_FILE="${CONFIG_DIR}/claude_desktop_config.json"
    OS_NAME="Windows"
else
    # Linux
    CONFIG_DIR="$HOME/.config/Claude"
    CONFIG_FILE="${CONFIG_DIR}/claude_desktop_config.json"
    OS_NAME="Linux"
fi

echo "Detected OS: $OS_NAME"
echo "Config file location: $CONFIG_FILE"
echo ""

# Create config directory if it doesn't exist
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Creating config directory..."
    mkdir -p "$CONFIG_DIR"
fi

# Check if config file exists
if [ -f "$CONFIG_FILE" ]; then
    echo "⚠️  Config file already exists!"
    echo ""
    echo "OPTION 1: Backup and replace"
    echo "OPTION 2: Manual merge (recommended if you have other MCP servers)"
    echo ""
    read -p "Do you want to backup and replace? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "Backing up to: $BACKUP_FILE"
        cp "$CONFIG_FILE" "$BACKUP_FILE"
    else
        echo ""
        echo "Please manually add this to your config file:"
        echo ""
        echo "{"
        echo "  \"mcpServers\": {"
        echo "    \"fittrack\": {"
        echo "      \"command\": \"python\","
        echo "      \"args\": ["
        echo "        \"$MCP_FILE\""
        echo "      ]"
        echo "    }"
        echo "  }"
        echo "}"
        echo ""
        exit 0
    fi
fi

# Create the config
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "fittrack": {
      "command": "python",
      "args": [
        "$MCP_FILE"
      ]
    }
  }
}
EOF

echo ""
echo "✅ Configuration created successfully!"
echo ""
echo "Next steps:"
echo "1. Make sure Python 3.10+ is installed: python --version"
echo "2. Install dependencies: pip install -r ${SCRIPT_DIR}/requirements.txt"
echo "3. Restart Claude Desktop"
echo "4. Look for 'FitTrack MCP Server' tools in Claude"
echo ""
echo "Available tools:"
echo "  - ping (test connection)"
echo "  - log_workout (track exercises)"
echo "  - calculate_hydration (hydration needs)"
echo "  - log_nutrition (meal tracking)"
echo "  - get_exercise_library (AC-joint safe exercises)"
echo "  - get_rehab_protocol (PT protocols)"
echo ""
echo "For troubleshooting, check Claude Desktop logs."
echo "=========================================="
