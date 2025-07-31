#!/usr/bin/env python3
"""
EPLua CLI - Native Windows Only

EPLua CLI for running Lua scripts with native tkinter UI support.
- If tkinter available: Start 2 threads (main=tkinter, worker=lua)
- If no tkinter: Start 1 thread (main=lua engine)
- Focused on native UI without HTML/CEF complexity
"""

import asyncio
import sys
import threading
import argparse
import io
from pathlib import Path
from typing import Optional

# Fix Windows Unicode output issues
def setup_unicode_output():
    """Setup proper Unicode output for Windows console"""
    if sys.platform == "win32":
        try:
            # Try to set console to UTF-8 mode (Windows 10 1903+)
            import os
            os.system("chcp 65001 >nul 2>&1")
            
            # Wrap stdout/stderr with UTF-8 encoding
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            # If anything fails, we'll fall back to ASCII-safe output
            pass

# Call this early
setup_unicode_output()

def safe_print(message, fallback_message=None):
    """Print with Unicode support, fallback to ASCII if needed"""
    try:
        print(message)
    except UnicodeEncodeError:
        if fallback_message:
            print(fallback_message)
        else:
            # Replace common Unicode characters with ASCII equivalents
            ascii_message = message.replace('🚀', '[ROCKET]').replace('🖥️', '[DESKTOP]').replace('📟', '[DEVICE]').replace('ℹ️', '[INFO]').replace('❌', '[ERROR]').replace('👋', '[WAVE]')
            print(ascii_message)

def check_tkinter_available() -> bool:
    """Check if tkinter is available"""
    try:
        import tkinter as tk
        return True
    except ImportError:
        return False

def run_engine_thread(script_path: Optional[str] = None, fragments: list = None, bridge=None):
    """Run Lua engine in a worker thread"""
    try:
        from eplua.engine import LuaEngine
        from eplua.gui_bridge import replace_gui_functions_with_bridge
        
        # Create the engine
        engine = LuaEngine()
        
        # Setup GUI bridge integration with shared bridge
        if bridge:
            replace_gui_functions_with_bridge(engine, bridge)
        
        # Run the engine
        async def engine_main():
            try:
                for fragment in fragments:
                    await engine.run_script(f'_PY.luaFragment({repr(fragment)})', "fragment")
                
                if script_path:
                    await engine.run_script(f'_PY.mainLuaFile("{script_path}")', script_path)
                
                # Keep running while operations are active
                while engine.has_active_operations() and engine.is_running():
                    await asyncio.sleep(0.1)
                
            except Exception as e:
                safe_print(f"❌ Engine error: {e}", f"[ERROR] Engine error: {e}")
                import traceback
                traceback.print_exc()
        
        # Run the async engine
        asyncio.run(engine_main())
        
    except Exception as e:
        safe_print(f"❌ Engine thread error: {e}", f"[ERROR] Engine thread error: {e}")
        import traceback
        traceback.print_exc()

def run_gui_thread(bridge=None):
    """Run GUI in main thread"""
    try:
        from eplua.gui_bridge import GUIManager
        
        # Create GUI manager with shared bridge
        if bridge:
            gui_manager = GUIManager(bridge)
        else:
            # Fallback - create our own bridge
            from eplua.gui_bridge import ThreadSafeGUIBridge
            bridge = ThreadSafeGUIBridge()
            bridge.start()
            gui_manager = GUIManager(bridge)
        
        # Start GUI loop (this will block until GUI closes)
        gui_manager.start_gui_loop()
        
    except Exception as e:
        safe_print(f"❌ GUI error: {e}", f"[ERROR] GUI error: {e}")
        import traceback
        traceback.print_exc()

def run_eplua_simple(script_path: Optional[str] = None, fragments: list = None):
    """
    Simplified EPLua runner
    
    Two modes:
    1. With tkinter: Main thread = GUI, Worker thread = Lua engine
    2. Without tkinter: Main thread = Lua engine only
    """
    fragments = fragments or []
    
    if check_tkinter_available():
        safe_print("🖥️ Native UI available - starting with GUI support", "[DESKTOP] Native UI available - starting with GUI support")
        
        # Create shared bridge instance
        from eplua.gui_bridge import ThreadSafeGUIBridge, GUIManager
        shared_bridge = ThreadSafeGUIBridge()
        shared_bridge.start()
        
        # Start Lua engine in worker thread with shared bridge
        engine_thread = threading.Thread(
            target=run_engine_thread, 
            args=(script_path, fragments, shared_bridge),
            daemon=True
        )
        engine_thread.start()
        
        # Run GUI in main thread with shared bridge (blocks until GUI closes)
        run_gui_thread(shared_bridge)
        
    else:
        safe_print("📟 Native UI not available - running engine only", "[DEVICE] Native UI not available - running engine only")
        
        # Setup basic stub GUI functions (do nothing but don't crash)
        def setup_stub_functions():
            """Setup stub GUI functions when tkinter is not available"""
            from eplua.lua_bindings import export_to_lua
            
            @export_to_lua("gui_available")
            def gui_available() -> bool:
                return False
            
            @export_to_lua("isNativeUIAvailable")
            def is_native_ui_available() -> bool:
                return False
                
            @export_to_lua("createNativeWindow")
            def create_native_window(title: str, width: int = 400, height: int = 300) -> str:
                return "ERROR: GUI not available"
        
        setup_stub_functions()
        
        # Run engine in main thread
        run_engine_thread(script_path, fragments)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="EPLua - Lua with Native UI and Async Timers")
    parser.add_argument("script", nargs="?", help="Lua script file to execute")
    parser.add_argument("-e", "--execute", action="append", dest="fragments", 
                      help="Execute Lua code fragment")
    parser.add_argument("-l", type=str, help="Ignored (compatibility with standard lua)")
    parser.add_argument("--no-gui", action="store_true", 
                      help="Force disable GUI mode (run engine in main thread)")
    
    args = parser.parse_args()
    
    # The -l flag is for compatibility with lua debugger (loads a package)
    # The script file comes as a positional argument, not in -l
    
    # Validate script file if provided
    script_path = None
    if args.script:
        script_file = Path(args.script)
        if not script_file.exists():
            safe_print(f"❌ Script file not found: {args.script}", f"[ERROR] Script file not found: {args.script}")
            sys.exit(1)
        script_path = str(script_file.resolve())
        script_path = script_path.replace("\\", "\\\\")  # Escape backslashes for Lua
    
    # Run EPLua
    try:
        run_eplua_simple(script_path, args.fragments or [])
    except KeyboardInterrupt:
        safe_print("\n👋 EPLua terminated by user", "\n[WAVE] EPLua terminated by user")
    except Exception as e:
        safe_print(f"❌ EPLua error: {e}", f"[ERROR] EPLua error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
