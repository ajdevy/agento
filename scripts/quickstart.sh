#!/bin/bash
# Quick start script for agento

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << 'BANNER'
    __       ____  ____  __________
   / /______ / / / / / /_  __/ __ \
  / //_/ __// / / / / / / / / /_/ /
 / ,< / /__/ /_/ / /_/ / / / /\ \ /
/_/|_|\___/\____/\____/ /_/ /_/ \_\

BANNER
echo -e "${NC}"
echo -e "${GREEN}Welcome to Agento!${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 is required but not found.${NC}"
    echo "Please install Python 3.11 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Using Python $PYTHON_VERSION"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

# Upgrade pip
echo "Setting up..."
pip install --upgrade pip -q

# Install
echo "Installing agento..."
pip install -e ".[all]" -q

# Check for API key
if [ -z "$OPENROUTER_API_KEY" ] && [ ! -f ".env" ]; then
    echo ""
    echo -e "${YELLOW}No API key found!${NC}"
    echo ""
    echo "Get a free API key from: https://openrouter.ai/keys"
    echo ""
    read -p "Paste your OpenRouter API key (or press Enter to skip): " API_KEY

    if [ -n "$API_KEY" ]; then
        echo "OPENROUTER_API_KEY=$API_KEY" > .env
        echo "Saved to .env"
    fi
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the agent:"
echo "  agento run"
echo ""
echo "Or use Make:"
echo "  make run"
echo ""
