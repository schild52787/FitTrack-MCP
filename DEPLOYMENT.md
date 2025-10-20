# Deployment Guide

This guide covers deploying FitTrack MCP Server to various platforms for use with ChatGPT and Claude.

## Table of Contents

- [Local Development](#local-development)
- [Cloud Deployment Options](#cloud-deployment-options)
  - [Vercel](#vercel)
  - [Railway](#railway)
  - [Render](#render)
  - [Fly.io](#flyio)
  - [Docker](#docker)
- [Client Configuration](#client-configuration)
  - [Claude Desktop](#claude-desktop)
  - [ChatGPT](#chatgpt)

---

## Local Development

### Stdio Mode (Default)

Run the server locally for testing:

```bash
python fittrack_mcp.py
```

### HTTP/SSE Mode (Local Testing)

For testing HTTP/SSE transport locally:

```bash
uvicorn fittrack_mcp:app --reload --port 8000
```

Access the MCP endpoint at: `http://localhost:8000/mcp`

---

## Cloud Deployment Options

### Vercel

**Best for:** Quick serverless deployments

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel deploy
```

3. Your MCP endpoint will be available at:
```
https://your-project.vercel.app/mcp
```

**Configuration:** `vercel.json` is already included in the repo.

**Note:** Vercel has a 15MB limit for Python deployments. This project is well under that limit.

---

### Railway

**Best for:** Full-featured deployments with persistent hosting

#### Option 1: Railway CLI

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login:
```bash
railway login
```

3. Initialize and deploy:
```bash
railway init
railway up
```

#### Option 2: GitHub Integration (Recommended)

1. Push your code to GitHub
2. Go to [Railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect Python and use the `Procfile`

**Configuration:** `Procfile` is already included.

**Environment Variables:** None required by default.

**Custom Domain:** Railway provides a free subdomain and supports custom domains.

---

### Render

**Best for:** Free tier with persistent hosting

1. Push code to GitHub
2. Go to [Render.com](https://render.com)
3. Click "New Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn fittrack_mcp:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free (or upgrade for better performance)

**Environment Variables:** None required by default.

---

### Fly.io

**Best for:** Global edge deployment with Docker

1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login:
```bash
fly auth login
```

3. Create `fly.toml`:
```toml
app = "fittrack-mcp"

[build]
  dockerfile = "Dockerfile"

[env]
  PYTHONUNBUFFERED = "1"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

[[services.http_checks]]
  interval = "30s"
  timeout = "5s"
  grace_period = "10s"
  method = "GET"
  path = "/mcp"
```

4. Deploy:
```bash
fly launch
fly deploy
```

**Note:** Update Dockerfile CMD to HTTP mode:
```dockerfile
CMD ["uvicorn", "fittrack_mcp:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### Docker

**Best for:** Self-hosted deployments

#### Build and Run Locally

```bash
# Build
docker build -t fittrack-mcp .

# Run in HTTP/SSE mode
docker run -p 8000:8000 fittrack-mcp uvicorn fittrack_mcp:app --host 0.0.0.0 --port 8000

# Run in stdio mode
docker run -it fittrack-mcp
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  fittrack-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    command: uvicorn fittrack_mcp:app --host 0.0.0.0 --port 8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/mcp').raise_for_status()"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

Run:
```bash
docker-compose up -d
```

#### Deploy to Cloud Container Services

- **Google Cloud Run:** `gcloud run deploy`
- **AWS ECS/Fargate:** Use ECR + ECS
- **Azure Container Instances:** `az container create`

---

## Client Configuration

### Claude Desktop

1. Locate your Claude Desktop config file:
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the FitTrack MCP server:

#### For Local stdio Mode:

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

#### For Remote HTTP/SSE Mode:

```json
{
  "mcpServers": {
    "fittrack": {
      "url": "https://your-deployment-url.com/mcp",
      "transport": "sse"
    }
  }
}
```

3. Restart Claude Desktop

4. Verify: You should see "FitTrack MCP Server" in the available tools

---

### ChatGPT

#### Developer Mode (OpenAI API)

1. **For Local stdio:**
   - Not directly supported by ChatGPT web interface
   - Use MCP client library to bridge stdio to HTTP

2. **For Remote HTTP/SSE (Recommended):**

   Deploy your server to a cloud platform (see above), then:

   a. Get your deployment URL (e.g., `https://your-app.railway.app/mcp`)

   b. In ChatGPT settings or API configuration, add:
   ```json
   {
     "mcp_servers": [
       {
         "name": "FitTrack",
         "url": "https://your-app.railway.app/mcp",
         "transport": "sse"
       }
     ]
   }
   ```

   c. The exact configuration method depends on OpenAI's MCP implementation

#### Custom GPT Actions (Alternative)

If ChatGPT doesn't support MCP directly, you can expose the tools as custom GPT actions:

1. Deploy the server with HTTP/SSE
2. Create OpenAPI schema for the tools
3. Configure as Custom GPT actions

**Note:** As of 2025, OpenAI is implementing MCP support. Check OpenAI documentation for the latest integration method.

---

## Testing Your Deployment

### Health Check

```bash
curl https://your-deployment-url.com/mcp
```

### Test a Tool (via HTTP)

```bash
# Ping
curl -X POST https://your-deployment-url.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"tool": "ping"}'

# Log Workout
curl -X POST https://your-deployment-url.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "log_workout",
    "params": {
      "exercise_name": "Landmine Press",
      "sets": 3,
      "reps": 12,
      "weight_lbs": 95,
      "rpe": "8 - Moderate"
    }
  }'
```

---

## Monitoring & Logs

### Vercel
```bash
vercel logs
```

### Railway
```bash
railway logs
```

### Render
- View logs in the Render dashboard

### Docker
```bash
docker logs fittrack-mcp
```

---

## Troubleshooting

### Common Issues

1. **Import errors:**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version (3.10+ required)

2. **Port conflicts:**
   - Change the port in your run command
   - Update health checks accordingly

3. **CORS issues:**
   - Add CORS middleware if accessing from browser
   - Most MCP clients handle this automatically

4. **Timeout on cloud platforms:**
   - Increase timeout settings in platform config
   - Some platforms have 30s limits on free tiers

### Platform-Specific Issues

**Vercel:**
- Lambda timeout: Increase in `vercel.json`
- Max size: Optimize dependencies if >15MB

**Railway:**
- Memory limits: Upgrade plan if needed
- Build failures: Check build logs for dependency issues

**Render:**
- Free tier sleeps after inactivity
- First request may be slow (cold start)

---

## Security Considerations

1. **API Keys:** If you add authentication, use environment variables
2. **Rate Limiting:** Consider adding rate limiting for public deployments
3. **HTTPS:** All cloud platforms provide HTTPS by default
4. **Input Validation:** Already implemented via Pydantic models

---

## Scaling

For high-traffic deployments:

1. **Use Redis/Database:** For persistent storage (currently stateless)
2. **Add Caching:** Cache rehab protocols and exercise libraries
3. **Load Balancing:** Use platform's auto-scaling features
4. **CDN:** For static assets if you add a web UI

---

## Next Steps

After deployment:

1. Test all 6 tools via your MCP client
2. Monitor logs for errors
3. Set up alerts (platform-dependent)
4. Consider adding analytics
5. Update documentation with your deployment URL

---

## Support

For deployment issues:
- Check platform documentation
- Review server logs
- Open an issue on GitHub

For MCP protocol issues:
- Refer to [MCP Documentation](https://modelcontextprotocol.io)
- Check FastMCP examples
