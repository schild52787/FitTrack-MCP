# For Railway, Heroku, and other PaaS platforms
web: uvicorn fittrack_mcp:app --host 0.0.0.0 --port $PORT

# Alternative: using gunicorn with uvicorn workers
# web: gunicorn fittrack_mcp:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
