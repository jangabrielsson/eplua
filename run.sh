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

# Create a new session and process group to ensure proper cleanup
# This ensures that when VSCode kills the process, all child processes are also killed
exec python -u -m eplua.cli "$@"
