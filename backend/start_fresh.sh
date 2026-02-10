#!/bin/bash
# Kill any existing processes on port 8001
lsof -ti:8001 | xargs kill -9 2>/dev/null

# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Start the server
./venv_py312/bin/python -m uvicorn main:app --port 8001
