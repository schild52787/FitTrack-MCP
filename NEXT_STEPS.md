# Next Steps - Verify and Test

Great! You've installed Python 3.11 and the required packages. Now let's verify everything works.

---

## Quick Verification (Run This First)

Open Terminal and run:

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
./verify_installation.sh
```

This will test:
- ✅ Python 3.11 installation
- ✅ FastMCP package
- ✅ MCP server file
- ✅ Server can start
- ✅ Claude Desktop config

---

## Manual Testing Steps

### Step 1: Test the MCP Server Directly

```bash
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
python3.11 fittrack_mcp.py
```

**Expected result:** You should see log messages. Press **Ctrl+C** to stop.

**If you see errors:** Copy the error and I'll help fix it.

---

### Step 2: Verify Your Claude Desktop Config

**File location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Open it:**
```bash
open -e ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Should look like this:**
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

**Key points:**
- ✅ Uses `"python3.11"` (not `"python3"`)
- ✅ Full path to your `fittrack_mcp.py` file
- ✅ Valid JSON (no trailing commas, proper brackets)

---

### Step 3: Restart Claude Desktop (IMPORTANT!)

**You MUST completely quit and restart:**

1. Click **Claude** in the menu bar
2. Click **Quit Claude** (or press Cmd+Q)
3. **Wait 5-10 seconds**
4. Open Claude Desktop again

Just closing the window is NOT enough!

---

### Step 4: Test in Claude Desktop

Open Claude Desktop and start a **new conversation**.

**Try these tests:**

#### Test 1: Ping (Basic Connection)
Ask Claude:
```
Use the ping tool to test the FitTrack MCP server
```

**Expected:** Claude should respond with "pong"

#### Test 2: List Tools
Ask Claude:
```
What MCP tools do you have available?
```

**Expected:** Claude should mention FitTrack tools

#### Test 3: Log a Workout
Ask Claude:
```
Log a workout: 3 sets of 10 Landmine Press at 85 lbs, RPE 7
```

**Expected:** Claude should log it and show AC-joint safety assessment

---

## Troubleshooting

### "Tools not showing up in Claude"

1. **Check logs:**
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```
   Look for errors related to "fittrack"

2. **Verify config location:**
   ```bash
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```
   Make sure it exists

3. **Try absolute paths:**
   Make sure your config uses the FULL path, not `~` or relative paths

### "Module not found" errors in logs

Run:
```bash
python3.11 -m pip list | grep -i mcp
```

Should show:
- fastmcp
- mcp (as a dependency)
- pydantic
- httpx

If missing, reinstall:
```bash
python3.11 -m pip install fastmcp "uvicorn[standard]"
```

### "Permission denied"

Make the script executable:
```bash
chmod +x "/Users/kyleschildkraut/Documents/FitTrack MCP/fittrack_mcp.py"
```

### Server starts but Claude doesn't see it

1. Check you're using `python3.11` in the config
2. Completely quit Claude Desktop (Cmd+Q, not just close window)
3. Wait 10 seconds before reopening
4. Try in a brand NEW conversation (not an existing one)

---

## What Success Looks Like

When everything is working:

✅ **Verification script passes all tests**
✅ **Server starts without errors** when you run it manually
✅ **Claude Desktop logs show no errors** for "fittrack"
✅ **Claude can use the ping tool** and responds with "pong"
✅ **All 6 tools are available:**
   - ping
   - log_workout
   - calculate_hydration
   - log_nutrition
   - get_exercise_library
   - get_rehab_protocol

---

## Example Usage (Once Working)

Here are some things to try:

**Workout tracking:**
```
Log a workout: 4 sets of 8 Face Pulls at 40 lbs, RPE 8, felt great today
```

**Hydration calculation:**
```
Calculate hydration for a 75-minute workout at RPE 9 in 85°F weather
```

**Exercise library:**
```
Show me AC-joint safe pressing exercises
```

**Rehab protocol:**
```
Get the AC joint arthritis rehab protocol, phase 2
```

**Nutrition logging:**
```
Log dinner at 9:30 PM: steak and potatoes, 50g protein, 60g carbs, 800 calories
```

---

## Still Having Issues?

Share the output of:

```bash
# Run verification
cd "/Users/kyleschildkraut/Documents/FitTrack MCP"
./verify_installation.sh

# Check package installation
python3.11 -m pip list | grep -E "fastmcp|mcp|pydantic"

# Check Claude logs
cat ~/Library/Logs/Claude/mcp*.log
```

I'll help debug! 🚀
