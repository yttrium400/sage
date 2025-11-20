#!/bin/bash
# Quick setup script for Code Assistant

echo "🚀 Setting up Code Assistant..."
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed!"
echo ""

# Check if Ollama is installed
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"

    # Check for models
    echo ""
    echo "Checking for available models..."
    ollama list

    echo ""
    echo "To pull the recommended model, run:"
    echo "  ollama pull deepseek-coder:6.7b"
else
    echo "❌ Ollama not found"
    echo ""
    echo "Please install Ollama:"
    echo "  macOS:   brew install ollama"
    echo "  Linux:   curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Windows: Download from https://ollama.com"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To get started:"
echo "  1. Activate venv: source .venv/bin/activate"
echo "  2. Run setup: python main.py setup"
echo "  3. Start chat: python main.py chat"
