#!/bin/bash
# Search Analytics with OTel — One-command setup
set -e

echo "=== Search Analytics with OTel — Setup ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required. Install it from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check .env
if [ ! -f ".env" ]; then
    echo ""
    echo "No .env file found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "⚠  Edit .env with your Elastic Cloud credentials before continuing."
    echo "   See README.md for where to find each value."
    echo ""
    echo "   Then run:"
    echo "     source venv/bin/activate"
    echo "     python load_data.py"
    echo "     python app.py"
    exit 0
fi

# Load data
echo ""
echo "Loading product data into Elasticsearch..."
python load_data.py

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Start the server:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Then open http://localhost:8000 in your browser."
echo ""
echo "Generate demo traffic:"
echo "  python generate_traffic.py --blog 2 --sessions 20"
