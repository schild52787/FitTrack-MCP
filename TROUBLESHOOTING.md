# FitTrack MCP - Troubleshooting Guide

## Issue: Claude Desktop Not Detecting FitTrack MCP

Based on your configuration, here are the common issues and fixes:

---

## ⚠️ Issue Found: Dependencies Not Installed

The main issue is that the required Python packages are **not installed** on your system.

### Quick Fix (Run These Commands)

Open Terminal on your Mac and run:

```bash
# Navigate to your FitTrack MCP directory
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"

# Install the dependencies
pip3 install -r requirements.txt
```

**OR** use the automated fix script I created:

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
./install_and_configure.sh
```

---

## Your Current Configuration

I can see your config has:

```json
{
  "mcpServers": {
    "fittrack": {
      "command": "python",
      "args": [
        "/Users/kyleschildkraut/Documents/FitTrack MCP/fittrack_mcp.py"
      ]
    }
  }
}
```

### Potential Issues:

1. **Missing Dependencies** ✗ (Most likely)
2. **Space in path** (might cause issues)
3. **Should use `python3` instead of `python`** (better on macOS)

---

## Step-by-Step Fix

### Step 1: Install Dependencies

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
pip3 install -r requirements.txt
```

You should see it install:
- mcp
- fastmcp
- pydantic
- httpx
- uvicorn

### Step 2: Test the Server Manually

```bash
python3 "/Users/kyleschildkraut/Documents/FitTrack MCP/fittrack_mcp.py"
```

**Expected output:** The server should start. You'll see logs. Press Ctrl+C to stop.

**If you get an error:** Copy and paste the error message - I can help fix it.

### Step 3: Update Your Config (Recommended)

Change your Claude Desktop config to use `python3` explicitly:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

### Step 4: Completely Restart Claude Desktop

1. **Quit Claude Desktop** (Cmd+Q, don't just close the window)
2. **Wait 5 seconds**
3. **Open Claude Desktop again**
4. **Start a new conversation**

### Step 5: Test It

Ask Claude:

```
Use the ping tool
```

If it responds with "pong", it's working! 🎉

---

## Alternative: Rename Your Directory (Removes Space Issue)

If you keep having issues, the space in "FitTrack MCP" might be the problem. Rename it:

```bash
# Rename the folder to remove the space
mv "/Users/kyleschildkraut/Documents/FitTrack MCP" "/Users/kyleschildkraut/Documents/FitTrack-MCP"
```

Then update your config to:

```json
{
  "mcpServers": {
    "fittrack": {
      "command": "python3",
      "args": [
        "/Users/kyleschildkraut/Documents/FitTrack-MCP/fittrack_mcp.py"
      ]
    }
  }
}
```

---

## How to Check Claude Desktop Logs

If it's still not working, check the logs:

```bash
# View recent logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

Or open the logs folder:

```bash
open ~/Library/Logs/Claude/
```

Look for errors related to "fittrack" or "mcp".

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'mcp'"

**Fix:** Install dependencies
```bash
pip3 install -r requirements.txt
```

### "command not found: python"

**Fix:** Use `python3` in your config instead of `python`

### "Permission denied"

**Fix:** Make sure the file is readable
```bash
chmod +x "/Users/kyleschildkraut/Documents/FitTrack MCP/fittrack_mcp.py"
```

### No errors in logs, but tools don't show up

**Fix:**
1. Make sure you completely quit Claude Desktop (Cmd+Q)
2. Wait 5-10 seconds before reopening
3. Try creating a brand new conversation

---

## Still Not Working?

If none of this works, please share:

1. The output of:
   ```bash
   cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
   python3 fittrack_mcp.py
   ```

2. The contents of your Claude Desktop logs:
   ```bash
   cat ~/Library/Logs/Claude/mcp*.log
   ```

3. The output of:
   ```bash
   pip3 list | grep -E "mcp|fastmcp|pydantic"
   ```

I can then help debug further!

---

## Quick Reference Commands

```bash
# Install dependencies
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
pip3 install -r requirements.txt

# Test server
python3 fittrack_mcp.py

# Edit config
open -e ~/Library/Application\ Support/Claude/claude_desktop_config.json

# View logs
tail -f ~/Library/Logs/Claude/mcp*.log

# Restart Claude Desktop (use Cmd+Q to quit fully)
```

---

## Expected Behavior When Working

When it's working correctly:

1. **Claude Desktop starts** - no error messages
2. **You can see tools** - either in a tools panel or Claude will mention them
3. **You can use tools** - Ask "Use the ping tool" and get "pong" response
4. **All 6 tools available**:
   - ping
   - log_workout
   - calculate_hydration
   - log_nutrition
   - get_exercise_library
   - get_rehab_protocol

Good luck! Let me know what errors you get and I'll help fix them.
