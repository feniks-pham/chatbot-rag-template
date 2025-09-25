#!/bin/bash

# Production Environment Setup Script
echo "🚀 Setting up VNG Chatbot - Production Environment"

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

# Step 0: Check environment file
if [ ! -f ".env" ]; then
    print_error ".env file not found! Please create and configure your .env file before running this setup script."
    print_status "You can copy from env.prod.example: cp env.prod.example .env"
    exit 1
else
    print_status ".env file found."
fi

# Step 1: Setup environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f "env.prod.example" ]; then
        cp env.prod.example .env
        print_status "Created .env file from env.prod.example"
        print_warning "Please update .env file with your actual production configurations"
    else
        print_error "env.prod.example file not found!"
        exit 1
    fi
else
    print_status ".env file already exists"
fi

# Step 2: Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3.13 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Step 3: Activate virtual environment and install dependencies
print_status "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Verify S3 and Database configurations
print_status "Verifying configurations..."
python -c "
import sys
import os
# Add current directory to Python path
sys.path.insert(0, os.getcwd())
from app.config.settings import settings
print(f'Environment: {settings.app_env}')
print(f'Database URL: {settings.database_url[:50]}...')
print(f'S3 Bucket: {settings.s3_path}')
print(f'S3 Excel File: {settings.s3_excel_file_key}')
"

# Step 5: Setup database schema
print_status "Setting up database schema..."

# Check if psql is available and install if needed
if ! command -v psql &> /dev/null; then
    print_warning "psql command not found! Attempting to install PostgreSQL client..."
    
    # Detect OS and install accordingly
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        print_status "Installing postgresql-client on Ubuntu/Debian..."
        sudo apt-get update
        sudo apt-get install -y postgresql-client
    elif command -v brew &> /dev/null; then
        # macOS
        print_status "Installing postgresql on macOS..."
        brew install postgresql
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        print_status "Installing postgresql on CentOS/RHEL..."
        sudo yum install -y postgresql
    else
        print_error "Could not automatically install PostgreSQL client."
        print_warning "Please install it manually:"
        print_warning "  - Ubuntu/Debian: sudo apt-get install postgresql-client"
        print_warning "  - macOS: brew install postgresql"
        print_warning "  - CentOS/RHEL: sudo yum install postgresql"
        print_warning "  - Or use Docker: docker run --rm -v \$(pwd):/workspace postgres:15 psql \$DATABASE_URL -f /workspace/scripts/init_db.sql"
        exit 1
    fi
    
    # Verify installation
    if ! command -v psql &> /dev/null; then
        print_error "Failed to install PostgreSQL client. Please install manually."
        exit 1
    else
        print_status "PostgreSQL client installed successfully!"
    fi
fi

DATABASE_URL=$(python -c "import sys; sys.path.insert(0, '.'); from app.config.settings import settings; print(settings.database_url)")

if ! psql "$DATABASE_URL" -f scripts/init_db.sql; then
    print_error "Failed to initialize database schema! Please check your DATABASE_URL and scripts/init_db.sql."
    exit 1
fi

print_status "Verifying database schema..."

missing_tables=()
for tbl in sessions chat_history; do
    if ! psql "$DATABASE_URL" -c "\dt" | grep -qw "$tbl"; then
        missing_tables+=("$tbl")
    fi
done

if [ ${#missing_tables[@]} -ne 0 ]; then
    print_error "Database schema verification failed - missing tables: ${missing_tables[*]}"
    print_error "Please check if scripts/init_db.sql executed successfully."
    exit 1
fi

print_status "Database schema is clean and verified."


# Step 6: Index knowledge base from S3
print_status "Indexing knowledge base from S3..."
python scripts/import_qa_data.py

print_status "✅ Production environment setup complete!"
print_status ""
print_status "Next steps:"
print_status "1. Run the backend: ./start.sh"
print_status "2. Run the frontend: source venv/bin/activate && streamlit run frontend/streamlit_app.py"
print_status ""
print_status "For Kubernetes deployment:"
print_status "1. Create ConfigMap and Secret for environment variables"
print_status "2. Apply Kubernetes manifests"
print_status "3. Ensure proper ingress configuration" 