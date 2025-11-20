#!/bin/bash
# Test script for CLI

echo "🧪 Testing Code Assistant CLI"
echo ""

# Activate venv
source .venv/bin/activate

# Check Ollama
echo "1. Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "   ✅ Ollama found"
else
    echo "   ❌ Ollama not found"
    exit 1
fi

# List models
echo ""
echo "2. Checking available models..."
python main.py models

# Test simple query (when model is ready)
echo ""
echo "3. Testing single query..."
python main.py ask "What is a Python list comprehension?" --model deepseek-coder:6.7b

echo ""
echo "✅ Tests complete!"
echo ""
echo "To start interactive chat:"
echo "  python main.py chat"
