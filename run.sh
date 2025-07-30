#!/bin/bash

# plua launcher script for VS Code MobDebug integration
# This script runs plua with proper environment and logging

# Set the working directory to the script's directory
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Enable debugging output
export PYTHONUNBUFFERED=1

# Log execution details
echo "=== eplua launcher started at $(date) ===" >> /tmp/eplua_launcher.log
echo "Working directory: $(pwd)" >> /tmp/eplua_launcher.log
echo "Arguments: $@" >> /tmp/eplua_launcher.log
echo "Python executable: $(which python)" >> /tmp/eplua_launcher.log

# Run eplua with all arguments passed through
python -m src.eplua.cli "$@"

# Log completion
echo "eplua completed with exit code: $?" >> /tmp/eplua_launcher.log
echo "=== eplua launcher ended at $(date) ===" >> /tmp/eplua_launcher.log
