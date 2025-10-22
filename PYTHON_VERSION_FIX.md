# Python Version Issue - Quick Fix

## Your Problem

Your Mac has Python **older than 3.10**, which is required for the MCP server.

## Check Your Version

Run this to see your current version:

```bash
python3 --version
```

If it shows Python 3.9 or older, you need to upgrade.

---

## 🚀 EASIEST FIX: Use Homebrew

### Step 1: Install Homebrew (if you don't have it)

Open Terminal and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the prompts. This takes 2-3 minutes.

### Step 2: Install Python 3.11

```bash
brew install python@3.11
```

### Step 3: Install FitTrack MCP Packages

```bash
python3.11 -m pip install fastmcp "uvicorn[standard]"
```

### Step 4: Update Your Claude Config

**File:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Important:** Change `"python3"` to `"python3.11"`:

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

### Step 5: Test It

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
python3.11 fittrack_mcp.py
```

Press Ctrl+C to stop. If it started without errors, you're good!

### Step 6: Restart Claude Desktop

1. Completely quit Claude Desktop (Cmd+Q)
2. Wait 5 seconds
3. Reopen Claude Desktop
4. Ask: "Use the ping tool"
5. Should respond: "pong" ✅

---

## Alternative: Download Python from python.org

If you don't want to use Homebrew:

1. Go to: https://www.python.org/downloads/
2. Download **Python 3.11** or **3.12** (macOS installer)
3. Install it (double-click the .pkg file)
4. Run in Terminal:
   ```bash
   python3 -m pip install fastmcp "uvicorn[standard]"
   ```
5. Your Claude config can stay with `"python3"` (the new version will be default)

---

## Why This Happens

- MCP (Model Context Protocol) requires Python 3.10+
- macOS ships with an older Python version
- Installing a newer version doesn't break anything - they coexist

---

## Quick Test Script

I created a script that checks your version and guides you:

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
./check_and_install.sh
```

This will:
- ✅ Check your Python version
- ✅ Tell you exactly what to do
- ✅ Install packages if your version is OK
- ❌ Guide you to upgrade if your version is too old

---

## After Installing Python 3.11

Your system will have both versions:
- `python3` → old version (3.9 or whatever came with macOS)
- `python3.11` → new version (what you installed)

**Use `python3.11` for FitTrack MCP.**

---

## Summary

1. Install Python 3.11: `brew install python@3.11`
2. Install packages: `python3.11 -m pip install fastmcp "uvicorn[standard]"`
3. Update Claude config to use `"python3.11"`
4. Restart Claude Desktop
5. Test: "Use the ping tool"

That's it! Let me know if you hit any errors during installation.
