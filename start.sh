#!/bin/bash

# Set environment variables if needed
export LOG_LEVEL=${LOG_LEVEL:-info}
export APP_HOST=${APP_HOST:-0.0.0.0}
export APP_PORT=${APP_PORT:-8000}

echo "Starting Trung Nguyen Legend Cafe Chatbot..."
echo "Host: $APP_HOST"
echo "Port: $APP_PORT"
echo "Log Level: $LOG_LEVEL"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Run uvicorn
uvicorn main:app \
    --host $APP_HOST \
    --port $APP_PORT \
    --reload \
    --log-level $LOG_LEVEL 