#!/bin/bash
# EPLua runner script

echo "🚀 EPLua - Native UI System"
echo "============================"

# Set PYTHONPATH to include src directory
export PYTHONPATH="/Users/jangabrielsson/Documents/dev/eplua/src:$PYTHONPATH"

# Activate virtual environment if available
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "ℹ️ Activated .venv virtual environment"
else
    echo "ℹ️ .venv not found, using system Python"
fi

# Run with Python module syntax
python -m eplua.cli "$@"
