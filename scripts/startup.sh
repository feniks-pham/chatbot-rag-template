#!/bin/bash

# Startup script for VNG Chatbot
echo "🚀 Starting VNG Chatbot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Wait for database to be ready
print_status "Waiting for database to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if python -c "
import sys
import os
sys.path.insert(0, '/app')
os.environ.setdefault('PYTHONPATH', '/app')
from app.config.settings import settings
from app.utils.create_db import create_db_if_not_exists
import psycopg2
try:
    if settings.is_postgres:
        create_db_if_not_exists(settings.database_url)
        conn = psycopg2.connect(settings.database_url)
        conn.close()
        print('Postgres is ready!')
        exit(0)
    elif settings.is_opensearch:
        from opensearchpy import OpenSearch
        client = OpenSearch(
            hosts=[settings.opensearch_url],
            http_auth=(settings.opensearch_username, settings.opensearch_password),
            use_ssl=True,
            verify_certs=False
        )
        client.info()   
        print('OpenSearch is ready!')
        exit(0)   
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
" 2>/dev/null; then
        print_status "Database is ready!"
        break
    else
        print_status "Waiting for database... ($((attempt+1))/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    print_error "Database failed to be ready within expected time"
    exit 1
fi

# Step 2: Initialize database schema
print_status "Initializing database schema..."

# Get DATABASE_URL from Python settings
# DATABASE_URL=$(python -c "
# import sys
# import os
# sys.path.insert(0, '/app')
# os.environ.setdefault('PYTHONPATH', '/app')
# from app.config.settings import settings
# print(settings.database_url)
# ")

# if [ -z "$DATABASE_URL" ]; then
#     print_error "DATABASE_URL is empty or not set"
#     exit 1
# fi

# print_status "Using DATABASE_URL: ${DATABASE_URL:0:50}..."

# if psql "$DATABASE_URL" -f /app/scripts/init_db.sql; then
#     print_status "Database schema initialized successfully"
# else
#     print_error "Failed to initialize database schema"
#     exit 1
# fi

# Step 3: Import Q&A data
print_status "Importing Q&A data..."

# Set PYTHONPATH for import_qa_data.py
export PYTHONPATH=/app

if python /app/scripts/import_qa_data.py; then
    print_status "Q&A data imported successfully"
else
    print_warning "Failed to import Q&A data (might already exist)"
    print_status "Continuing with application startup..."
fi

# Step 4: Start the application
print_status "Starting FastAPI application..."
print_status "🚀 VNG Chatbot is ready!"

# Use exec to replace the shell process with uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload 