#!/bin/bash

# Development Environment Setup Script
echo "🚀 Setting up Trung Nguyen Chatbot - Development Environment"

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed (support both old and new versions)
DOCKER_COMPOSE_CMD=""
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Using Docker Compose command: $DOCKER_COMPOSE_CMD"

# Step 1: Check environment file
if [ ! -f ".env" ]; then
    print_error ".env file not found! Please create and configure your .env file before running this setup script."
    print_status "You can copy from env.dev.example: cp env.dev.example .env"
    exit 1
else
    print_status ".env file found."
fi

# Step 2: Start PostgreSQL with Docker
print_status "Starting PostgreSQL database..."
sudo $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml up -d postgres

# Wait for PostgreSQL to be ready
print_status "Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if sudo docker exec trung-nguyen-postgres-dev pg_isready -U postgres &>/dev/null; then
        print_status "PostgreSQL is ready!"
        sudo docker exec trung-nguyen-postgres-dev psql -U postgres -d trung_nguyen_chatbot -c '\dt'
        break
    else
        print_status "Waiting for PostgreSQL... ($((attempt+1))/$max_attempts)"
        sleep 2
        ((attempt++))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    print_error "PostgreSQL failed to start within expected time"
    exit 1
fi

# Step 3: Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3.13 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Step 4: Activate virtual environment and install dependencies
print_status "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 5: Check if data file exists
if [ ! -f "data/trung-nguyen-legend.xlsx" ]; then
    print_error "Data file not found at data/trung-nguyen-legend.xlsx"
    print_warning "Please ensure your Excel file is placed in the data directory"
    exit 1
fi

# Step 6: Index knowledge base
print_status "Indexing knowledge base..."
python scripts/import_qa_data.py

print_status "✅ Development environment setup complete!"
print_status ""
print_status "Next steps:"
print_status "1. Run the backend: ./start.sh"
print_status "2. Run the frontend: source venv/bin/activate && streamlit run frontend/streamlit_app.py"
print_status ""
print_status "To stop the database: sudo $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml down"