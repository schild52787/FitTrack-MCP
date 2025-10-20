# Installation Fix for macOS

## The Problem

The original `requirements.txt` had package names that don't exist on PyPI. The correct package is just `fastmcp`, which automatically includes all dependencies.

## Quick Fix

Run this in Terminal:

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"

# Install with the simplified requirements
pip3 install fastmcp uvicorn[standard]
```

## If You Get "Python Version Too Old" Error

Check your Python version:

```bash
python3 --version
```

You need Python **3.10 or higher**. If yours is older:

### Option 1: Install Python 3.11 (Recommended)

**Using Homebrew:**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Use Python 3.11 specifically
python3.11 -m pip install fastmcp uvicorn[standard]
```

Then update your Claude config to use `python3.11`:

```json
{
  "mcpServers": {
    "fittrack": {
      "command": "python3.11",
      "args": [
        "/Users/kyleschildkraut/Documents/FitTrack MCP/fittrack_mcp.py"
      ]
    }
  }
}
```

### Option 2: Download from python.org

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or 3.12
3. Install it
4. Then run:
```bash
python3 -m pip install fastmcp uvicorn[standard]
```

## Test Installation

After installing, test it:

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
python3 fittrack_mcp.py
```

You should see the server start (press Ctrl+C to stop).

## Then Configure Claude Desktop

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Contents:**
```json
{
  "mcpServers": {
    "fittrack": {
      "command": "python3",
      "args": [
        "/Users/kyleschildkraut/Documents/FitTrack MCP/fittrack_mcp.py"
      ]
    }
  }
}
```

**Completely restart Claude Desktop** (Cmd+Q, then reopen).

## Verify

Ask Claude: "Use the ping tool"

Should respond: "pong" ✅

---

## Still Having Issues?

Share the output of:

```bash
python3 --version
pip3 list | grep -i mcp
```

And I'll help debug further!
