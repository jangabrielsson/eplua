#!/usr/bin/env python3
"""
EPLua Windows Wrapper Script

This script serves as a Windows-compatible interpreter wrapper for EPLua,
similar to run.sh on macOS. It runs the EPLua CLI with all passed arguments.
Since we installed with 'pip install -e .', the package should be available.
"""

import sys
import os
from pathlib import Path

# Import and run the EPLua CLI
try:
    from eplua.cli import main as cli_main
    # Replace sys.argv to pass through all arguments except this script name
    sys.argv = ['eplua'] + sys.argv[1:]
    cli_main()
except ImportError as e:
    # Fallback: try to add src directory to Python path if package not found
    script_dir = Path(__file__).parent.absolute()
    src_path = script_dir / "src"
    
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        try:
            from eplua.cli import main as cli_main
            sys.argv = ['eplua'] + sys.argv[1:]
            cli_main()
        except ImportError as e2:
            print(f"❌ Failed to import EPLua: {e2}")
            print(f"   Original error: {e}")
            print(f"   Tried src directory: {src_path}")
            print(f"   Current Python path: {sys.path}")
            sys.exit(1)
    else:
        print(f"❌ Failed to import EPLua: {e}")
        print(f"   Make sure to install with: pip install -e .")
        print(f"   Or ensure src directory exists: {src_path if 'src_path' in locals() else 'N/A'}")
        sys.exit(1)
except Exception as e:
    print(f"❌ EPLua error: {e}")
    sys.exit(1)
