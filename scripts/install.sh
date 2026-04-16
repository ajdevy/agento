#!/bin/bash
# Agento install script

set -e

echo "Installing Agento..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3.11+ is required"
    exit 1
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install --upgrade pip
pip install -e ".[dev,memory,mcp,docker]"

echo "Agento installed successfully!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run agento:"
echo "  agento"
echo ""
echo "Or set up your API key:"
echo "  export OPENROUTER_API_KEY=your-key-here"
