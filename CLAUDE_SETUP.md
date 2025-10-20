# Claude Desktop Setup Guide

Simple guide to connect FitTrack MCP Server to Claude Desktop.

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
cd /home/user/FitTrack-MCP
pip install -r requirements.txt
```

### Step 2: Run Setup Script (Easiest)

```bash
./setup_claude.sh
```

The script will automatically:
- Detect your operating system
- Find the correct Claude config location
- Create the configuration file
- Backup existing config if needed

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. You should see FitTrack tools available!

---

## Manual Setup (If Script Doesn't Work)

### Find Your Config File Location

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
(Usually: `C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json`)

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Edit the Config File

1. Open the file in a text editor (create it if it doesn't exist)
2. Add this configuration:

```json
{
  "mcpServers": {
    "fittrack": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/FitTrack-MCP/fittrack_mcp.py"
      ]
    }
  }
}
```

3. **Replace** `/ABSOLUTE/PATH/TO/FitTrack-MCP/fittrack_mcp.py` with your actual path:
   - **Current path on this system:** `/home/user/FitTrack-MCP/fittrack_mcp.py`
   - Find your path: `pwd` (in the FitTrack-MCP directory)

### If You Have Other MCP Servers Already

Don't replace the whole file! Just add the "fittrack" section:

```json
{
  "mcpServers": {
    "your-existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "fittrack": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/FitTrack-MCP/fittrack_mcp.py"
      ]
    }
  }
}
```

---

## Verify Installation

### Step 1: Check Python Version

```bash
python --version
```

Should be Python 3.10 or higher.

### Step 2: Test the MCP Server

```bash
cd /home/user/FitTrack-MCP
python fittrack_mcp.py
```

You should see the server start. Press Ctrl+C to stop.

### Step 3: Open Claude Desktop

1. Restart Claude Desktop completely
2. Start a new conversation
3. Look for a tools icon or mention of "MCP servers"
4. You should see **6 FitTrack tools** available:
   - ✅ ping
   - ✅ log_workout
   - ✅ calculate_hydration
   - ✅ log_nutrition
   - ✅ get_exercise_library
   - ✅ get_rehab_protocol

### Step 4: Test It

Try asking Claude:
```
"Use the ping tool to test the FitTrack MCP server"
```

If it responds with "pong", it's working! 🎉

---

## Troubleshooting

### "Command not found: python"

Try `python3` instead:

```json
{
  "mcpServers": {
    "fittrack": {
      "command": "python3",
      "args": [
        "/ABSOLUTE/PATH/TO/FitTrack-MCP/fittrack_mcp.py"
      ]
    }
  }
}
```

### "Module not found" errors

Install dependencies:
```bash
pip install -r requirements.txt
```

Or with pip3:
```bash
pip3 install -r requirements.txt
```

### Tools not showing up in Claude

1. **Check config file location** - Make sure you edited the right file
2. **Check file path** - Must be absolute path, not relative
3. **Restart Claude Desktop** - Completely quit and reopen
4. **Check Claude Desktop logs**:
   - **macOS:** `~/Library/Logs/Claude/`
   - **Windows:** `%APPDATA%\Claude\logs\`
   - **Linux:** `~/.config/Claude/logs/`

### Permission errors

Make sure the script is executable:
```bash
chmod +x /home/user/FitTrack-MCP/fittrack_mcp.py
```

---

## What You Can Do With FitTrack

Once connected, you can ask Claude things like:

**Workout Logging:**
- "Log a workout: 3 sets of 12 Landmine Press at 95 lbs, RPE 8"

**Hydration:**
- "Calculate hydration needs for a 60-minute workout at RPE 9"

**Exercise Library:**
- "Show me AC-joint safe pressing exercises"

**Nutrition:**
- "Log dinner at 8:30 PM: chicken and rice, 40g protein, 60g carbs"

**Rehab Protocols:**
- "Get the AC joint arthritis rehab protocol, phase 2"

---

## Need Help?

- Check the main [README.md](README.md) for more details
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment options
- Open an issue on GitHub if you're stuck

---

## Next Steps

Once it's working:
1. Try all 6 tools to see what they do
2. Check out the rehab protocols for detailed PT exercises
3. Use the exercise library to find AC-joint safe movements
4. Consider deploying to the cloud for access anywhere (see DEPLOYMENT.md)
