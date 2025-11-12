#!/bin/bash
# Script to start the multi-agent API server

echo "Starting LangChain Multi-Agent API Server..."
echo "API will be available at http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the server
python api_server.py

