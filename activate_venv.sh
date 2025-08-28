#!/bin/bash
# Activate the WebScraperPortable virtual environment
# Usage: source activate_venv.sh

if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ WebScraperPortable virtual environment activated"
    echo "📋 To install requirements: pip install -r requirements.txt"
    echo "🧪 To test features: python -c 'from dependencies import print_feature_status; print_feature_status()'"
else
    echo "❌ Virtual environment not found. Create with: python -m venv .venv"
fi