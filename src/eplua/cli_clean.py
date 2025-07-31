#!/usr/bin/env python3
"""
EPLua CLI - A Lua interpreter with async timer support and GUI capabilities

Usage:
    eplua <script.lua>           # Run a Lua script
    eplua --help                 # Show help
    eplua --version              # Show version
    eplua --no-gui               # Force disable GUI mode
"""

import sys
import argparse
import asyncio
import logging
import threading
import os
from typing import Optional
from eplua import LuaEngine
from eplua.gui_bridge import ThreadSafeGUIBridge, GUIManager, replace_gui_functions_with_bridge, GUI_AVAILABLE

__version__ = "0.1.0"


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(name)s - %(levelname)s - %(message)s'
    )


def run_eplua_engine(script_path: str, fragments: list, bridge: Optional[ThreadSafeGUIBridge] = None):
    """Run EPLua engine in worker thread (or main thread if no GUI)"""
    async def engine_main():
        try:
            async with LuaEngine() as engine:
                # Replace GUI functions with bridge versions if using GUI
                if bridge:
                    replace_gui_functions_with_bridge(engine, bridge)
                
                # Execute fragments first (if any)
                if fragments:
                    for fragment in fragments:
                        await engine.run_script(f'_PY.luaFragment({repr(fragment)})', "fragment")
                
                # Execute script file (if provided)
                if script_path:
                    await engine.run_script(f'_PY.mainLuaFile("{script_path}")', script_path)
                
                # Keep running while there are active operations
                while engine.has_active_operations() and engine.is_running():
                    await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"❌ EPLua engine error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Signal GUI to close
            if bridge and bridge.running:
                bridge.stop()
    
    # Run the async engine
    asyncio.run(engine_main())


def detect_gui_usage(script_path: str, fragments: list) -> bool:
    """Detect if the script or fragments use GUI functions"""
    gui_functions = [
        'create_window', 'show_window', 'hide_window', 'close_window',
        'set_window_html', 'list_windows'
    ]
    
    native_ui_functions = [
        'createNativeWindow', 'setNativeUI', 'showNativeWindow', 
        'hideNativeWindow', 'closeNativeWindow', 'listNativeWindows'
    ]
    
    gui_patterns = [
        # Direct _PY function calls
        *[f'_PY.{func}' for func in gui_functions],
        *[f'_PY.{func}' for func in native_ui_functions],
        # Windows module usage
        "require('windows')", 'require("windows")',
        'windows.createWindow', 'windows.create', 'windows.new',
        'windows.demo()', 'windows.showWindow',
        # Native UI module usage
        "require('native_ui')", 'require("native_ui")',
        'nativeUI.createWindow', 'nativeUI.create', 'native_ui.createWindow',
        'createNativeWindow', 'setNativeUI'
    ]
    
    # Check fragments
    if fragments:
        for fragment in fragments:
            for pattern in gui_patterns:
                if pattern in fragment:
                    return True
    
    # Check script file
    if script_path and os.path.exists(script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in gui_patterns:
                    if pattern in content:
                        return True
        except:
            pass
    
    return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="eplua",
        description="EPLua - Lua interpreter with async timer support and GUI capabilities",
        epilog="Examples:\n"
               "  eplua script.lua        # Run a Lua script (auto-detects GUI usage)\n"
               "  eplua -v script.lua     # Run with verbose output\n"
               "  eplua -e 'print(\"Hello\")' # Execute Lua fragment\n"
               "  eplua --no-gui script.lua # Force disable GUI mode\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "script",
        type=str,
        nargs='?',  # Make script optional when using -e
        help="Lua script file to execute"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "-e",
        type=str,
        dest="fragments",
        action="append",  # Allow multiple -e flags
        help="Execute lua fragment"
    )

    parser.add_argument(
        "-l",
        type=str,
        help="Ignored (compatibility with standard lua)"
    )
    
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Force disable GUI mode (run engine in main thread)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"EPLua {__version__}"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if we have either a script file or fragments
    if not args.script and not args.fragments:
        parser.print_help()
        return 1
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Prepare fragments list
    fragments = args.fragments or []
    
    # Detect if GUI is needed and available
    needs_gui = not args.no_gui and detect_gui_usage(args.script, fragments)
    use_gui_mode = needs_gui and GUI_AVAILABLE
    
    if args.verbose:
        print(f"GUI Available: {GUI_AVAILABLE}")
        print(f"GUI Needed: {needs_gui}")
        print(f"Using GUI Mode: {use_gui_mode}")
    
    try:
        if use_gui_mode:
            # Run with GUI-first architecture
            if args.verbose:
                print("🔧 Architecture: GUI in main thread, EPLua in worker thread")
            
            # Create bridge
            gui_bridge = ThreadSafeGUIBridge()
            gui_bridge.start()
            
            # Start EPLua engine in worker thread
            engine_thread = threading.Thread(
                target=run_eplua_engine,
                args=(args.script, fragments, gui_bridge),
                daemon=True
            )
            engine_thread.start()
            
            # Run GUI in main thread
            gui_manager = GUIManager(gui_bridge)
            gui_manager.start_gui_loop()
            
            # Wait for engine thread to complete
            engine_thread.join(timeout=1.0)
            
        else:
            # Run without GUI in main thread (traditional mode)
            if args.verbose:
                print("🔧 Architecture: EPLua in main thread (no GUI)")
            
            run_eplua_engine(args.script, fragments, None)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
