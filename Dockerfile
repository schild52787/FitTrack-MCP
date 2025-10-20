# Multi-stage Dockerfile for FitTrack MCP Server
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY fittrack_mcp.py .

# Expose port for HTTP/SSE mode
EXPOSE 8000

# Default to stdio mode
CMD ["python", "fittrack_mcp.py"]

# For HTTP/SSE mode, override with:
# CMD ["uvicorn", "fittrack_mcp:app", "--host", "0.0.0.0", "--port", "8000"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/mcp').raise_for_status()" || exit 1
