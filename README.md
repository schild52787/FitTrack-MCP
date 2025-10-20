# FitTrack MCP Server

A comprehensive Model Context Protocol (MCP) server for fitness tracking, workout logging, hydration management, nutrition tracking, and evidence-based physical therapy protocols.

## Features

- **AC-Joint Safe Exercise Validation**: Automatically validates exercises for AC joint arthritis safety
- **Hyperhidrosis-Aware Hydration**: Personalized hydration calculations for heavy sweaters
- **Late-Meal Guardrails**: Warnings for meals after 9pm to maintain healthy eating patterns
- **RPE-Based Progression**: Rate of Perceived Exertion tracking (6-10 scale)
- **Evidence-Based PT Protocols**: Comprehensive rehab protocols for 6 conditions
- **Multi-Format Support**: Returns data in Markdown or JSON format

## Available Tools

1. **ping** - Health check endpoint
2. **log_workout** - Log workout sessions with AC-joint safety validation
3. **calculate_hydration** - Calculate hydration needs based on workout intensity and duration
4. **log_nutrition** - Log meals with late-meal warnings
5. **get_exercise_library** - Browse AC-joint safe exercises by category
6. **get_rehab_protocol** - Access evidence-based rehab protocols

## Rehab Conditions Supported

- AC Joint Arthritis
- Bicep Tendonitis
- Cervical Spine Arthritis
- Scapular Winging
- Post-Ankle Surgery
- Post-Meniscus Surgery

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Local Development (stdio)

Run the server locally in stdio mode:

```bash
python fittrack_mcp.py
```

### Method 2: HTTP/SSE Mode (for ChatGPT & Claude)

The server exposes an ASGI app that can be deployed to any cloud platform supporting ASGI applications.

## Configuration

### For Claude Desktop

Add this to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fittrack": {
      "command": "python",
      "args": ["/absolute/path/to/FitTrack-MCP/fittrack_mcp.py"]
    }
  }
}
```

### For ChatGPT Developer Mode

1. **Option A: Local stdio connection**
   - Use the MCP client in ChatGPT to connect to the server
   - Configure with the command: `python /path/to/fittrack_mcp.py`

2. **Option B: HTTP/SSE connection (recommended for cloud deployment)**
   - Deploy the server to a cloud platform (see Deployment section)
   - Configure ChatGPT with the deployed URL: `https://your-domain.com/mcp`

### MCP Client Configuration File

Create a file named `mcp_config.json` in your project directory:

```json
{
  "name": "FitTrack MCP Server",
  "version": "1.0.0",
  "description": "Comprehensive fitness and rehab tracker",
  "server": {
    "command": "python",
    "args": ["fittrack_mcp.py"],
    "env": {}
  },
  "tools": [
    {
      "name": "ping",
      "description": "Health check endpoint"
    },
    {
      "name": "log_workout",
      "description": "Log workout sessions with AC-joint safety validation"
    },
    {
      "name": "calculate_hydration",
      "description": "Calculate hydration needs for hyperhidrosis"
    },
    {
      "name": "log_nutrition",
      "description": "Log meals with late-meal warnings"
    },
    {
      "name": "get_exercise_library",
      "description": "Browse AC-joint safe exercises"
    },
    {
      "name": "get_rehab_protocol",
      "description": "Access evidence-based rehab protocols"
    }
  ]
}
```

## Deployment

### Vercel

1. Create a `vercel.json`:
```json
{
  "builds": [
    {
      "src": "fittrack_mcp.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/mcp/(.*)",
      "dest": "fittrack_mcp.py"
    }
  ]
}
```

2. Deploy:
```bash
vercel deploy
```

### Railway

1. Create a `Procfile`:
```
web: uvicorn fittrack_mcp:app --host 0.0.0.0 --port $PORT
```

2. Add `uvicorn` to requirements.txt

3. Deploy via Railway CLI or GitHub integration

### Docker

1. Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fittrack_mcp.py .

# For stdio mode
CMD ["python", "fittrack_mcp.py"]

# For HTTP/SSE mode, use:
# CMD ["uvicorn", "fittrack_mcp:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:
```bash
docker build -t fittrack-mcp .
docker run -p 8000:8000 fittrack-mcp
```

## Example Usage

### Log a Workout

```python
# Via MCP protocol
{
  "tool": "log_workout",
  "params": {
    "exercise_name": "Landmine Press",
    "sets": 3,
    "reps": 12,
    "weight_lbs": 95,
    "rpe": "8 - Moderate",
    "notes": "Felt strong, good form"
  }
}
```

### Calculate Hydration

```python
{
  "tool": "calculate_hydration",
  "params": {
    "workout_duration_minutes": 60,
    "intensity": "9 - Hard",
    "ambient_temp_f": 75,
    "sweat_rate_lbs_per_hour": 2.5
  }
}
```

### Get Rehab Protocol

```python
{
  "tool": "get_rehab_protocol",
  "params": {
    "condition": "ac_joint_arthritis",
    "phase": 2
  }
}
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Quality

```bash
# Format code
black fittrack_mcp.py

# Type checking
mypy fittrack_mcp.py

# Linting
ruff check fittrack_mcp.py
```

## Architecture

- **Framework**: FastMCP (Model Context Protocol framework)
- **Validation**: Pydantic v2 for input validation
- **Transport**: Supports both stdio and HTTP/SSE
- **Deployment**: ASGI-compatible (Uvicorn, Hypercorn, etc.)

## API Documentation

### Tool Annotations

All tools include MCP annotations:
- `readOnlyHint`: Indicates if the tool modifies state
- `destructiveHint`: Warns about destructive operations
- `idempotentHint`: Indicates if repeated calls have the same effect
- `openWorldHint`: Suggests the tool may interact with external systems

### Response Formats

Tools support two output formats:
- **Markdown**: Human-readable, formatted output (default)
- **JSON**: Structured data for programmatic access

## Troubleshooting

### Common Issues

1. **Module not found error**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Use Python 3.10 or higher

2. **Connection refused**
   - For HTTP mode, ensure the server is running and accessible
   - Check firewall settings for cloud deployments

3. **Invalid exercise warnings**
   - The server validates against a curated list of AC-joint safe exercises
   - Unknown exercises will trigger a warning with guidelines

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Acknowledgments

Built with [FastMCP](https://github.com/jlowin/fastmcp) framework for the Model Context Protocol.
