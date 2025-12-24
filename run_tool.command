#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Biochar Validation Studio..."

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install Python 3."
    exit
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Open Browser (Optional - wait a bit)
(sleep 2 && open http://localhost:8000) &

# Run App
echo "Server running at http://localhost:8000"
python3 -m app.main
