#!/bin/bash

# Startup Trends Dashboard - Quick Start Script

echo "=========================================="
echo "  Startup Trends Dashboard Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "📝 IMPORTANT: Edit .env and add your Anthropic API key:"
    echo "   ANTHROPIC_API_KEY=your_api_key_here"
    echo ""
    echo "Get your API key at: https://console.anthropic.com"
    echo ""
    read -p "Press Enter after you've added your API key..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run the application
echo "=========================================="
echo "  Starting Dashboard"
echo "=========================================="
echo ""

python main.py

# Deactivate when done
deactivate
