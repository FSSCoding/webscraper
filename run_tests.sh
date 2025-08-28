#!/bin/bash
# Test runner for WebScraperPortable with proper environment setup

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH to include src directory
export PYTHONPATH=src:$PYTHONPATH

# Run tests with verbose output
python -m pytest tests/ -v --tb=short

echo "Tests completed!"