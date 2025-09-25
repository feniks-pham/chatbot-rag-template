#!/bin/bash

# Setup script for VNG Chatbot

echo "Setting up VNG Chatbot..."

# Check if Python is installed
if ! command -v python3.13 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3.13 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
else
    echo ".env file already exists"
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Initialize database: psql -d your_database -f scripts/init_db.sql"
echo "3. Import Q&A data: python scripts/import_qa_data.py"
echo "4. Start the server: python main.py"
echo "5. (Optional) Start frontend: streamlit run frontend/streamlit_app.py"
