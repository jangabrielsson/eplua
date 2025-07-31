#!/bin/bash

# Minimal eplua launcher for VS Code MobDebug integration
# Just activates virtual environment and runs eplua directly

# Set the working directory to the script's directory
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Run eplua directly with all arguments
exec eplua "$@"
