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
from typing import Optional, Dict, Any

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

def create_config_table(offline: bool = False, nodebugger: bool = False, 
                       debugger_host: str = "localhost", debugger_port: int = 8172,
                       run_for: Optional[int] = None,
                       fibaro: bool = False,
                       headers: Optional[list] = None) -> Dict[str, Any]:
    """Create configuration table with platform info and CLI flags"""
    config = {
        "platform": sys.platform,  # 'win32', 'darwin', 'linux', etc.
        "fileSeparator": "\\\\" if sys.platform == "win32" else "/",
        "pathSeparator": ";" if sys.platform == "win32" else ":",
        "isWindows": sys.platform == "win32",
        "isMacOS": sys.platform == "darwin", 
        "isLinux": sys.platform.startswith("linux"),
        "pythonVersion": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "enginePath": str(Path(__file__).parent.parent).replace("\\", "\\\\"),
        "luaLibPath": str(Path(__file__).parent.parent / "lua").replace("\\", "\\\\"),
        "offline": offline,  # CLI flag for offline mode
        "debugger": not nodebugger,  # CLI flag for debugger (inverted because --nodebugger)
        "debugger_host": debugger_host,  # CLI flag for debugger host
        "debugger_port": debugger_port,  # CLI flag for debugger port
        "run_for": 10000000 if run_for == -1 else run_for,  # CLI flag for time limit (-1 -> very large number)
        "fibaro": fibaro,  # CLI flag for Fibaro API compatibility
        "headers": headers or [],  # CLI flag for QuickApp headers
    }
    return config

def run_engine_thread(script_path: Optional[str] = None, fragments: list = None, bridge=None, config: Dict[str, Any] = None):
    """Run Lua engine in a worker thread"""
    try:
        from eplua.engine import LuaEngine
        from eplua.gui_bridge import replace_gui_functions_with_bridge
        
        # Create the engine with config
        engine = LuaEngine(config=config)
        
        # Setup GUI bridge integration with shared bridge
        if bridge:
            replace_gui_functions_with_bridge(engine, bridge)
        
        # Run the engine
        async def engine_main():
            try:
                # Set up time limit timer if specified
                timeout_task = None
                run_for_seconds = config.get("run_for")
                if run_for_seconds is not None:
                    async def timeout_handler():
                        await asyncio.sleep(run_for_seconds)
                        print(f"⏰ Time limit reached ({run_for_seconds}s), terminating...")
                        import os
                        os._exit(0)
                    
                    timeout_task = asyncio.create_task(timeout_handler())
                
                for fragment in fragments:
                    await engine.run_script(f'_PY.luaFragment({repr(fragment)})', "fragment")
                
                if script_path:
                    await engine.run_script(f'_PY.mainLuaFile("{script_path}")', script_path)
                
                # Keep running while operations are active (with different behaviors based on run_for)
                if run_for_seconds == -1 or run_for_seconds == 10000000:
                    # Run forever mode: ignore active operations, just keep running
                    try:
                        while True:
                            await asyncio.sleep(1)  # Just sleep forever, Ctrl-C to exit
                    except KeyboardInterrupt:
                        pass
                elif run_for_seconds is not None:
                    # Time limit mode: normal active operations check + timeout
                    while engine.has_active_operations() and engine.is_running():
                        await asyncio.sleep(0.1)
                    
                    # If we exit the loop naturally, terminate
                    import os
                    os._exit(0)
                else:
                    # Default mode: exit when no active operations
                    while engine.has_active_operations() and engine.is_running():
                        await asyncio.sleep(0.1)
                    
                    # If we exit the loop, it means no active operations - terminate the process
                    import os
                    os._exit(0)
                
                # Cancel timeout task if we exit naturally
                if timeout_task and not timeout_task.done():
                    timeout_task.cancel()
                
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

def run_eplua_simple(script_path: Optional[str] = None, fragments: list = None, config: Dict[str, Any] = None):
    """
    Simplified EPLua runner
    
    Two modes:
    1. With tkinter: Main thread = GUI, Worker thread = Lua engine
    2. Without tkinter: Main thread = Lua engine only
    """
    fragments = fragments or []
    config = config or {}
    
    if check_tkinter_available():
        safe_print("🖥️ Native UI available - starting with GUI support", "[DESKTOP] Native UI available - starting with GUI support")
        
        # Create shared bridge instance
        from eplua.gui_bridge import ThreadSafeGUIBridge, GUIManager
        shared_bridge = ThreadSafeGUIBridge()
        shared_bridge.start()
        
        # Start Lua engine in worker thread with shared bridge
        engine_thread = threading.Thread(
            target=run_engine_thread, 
            args=(script_path, fragments, shared_bridge, config),
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
        run_engine_thread(script_path, fragments, None, config)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="EPLua - Lua with Native UI and Async Timers")
    parser.add_argument("script", nargs="?", help="Lua script file to execute")
    parser.add_argument("-e", "--execute", action="append", dest="fragments", 
                      help="Execute Lua code fragment")
    parser.add_argument("-l", type=str, help="Ignored (compatibility with standard lua)")
    parser.add_argument("--no-gui", action="store_true", 
                      help="Force disable GUI mode (run engine in main thread)")
    parser.add_argument("-o", "--offline", action="store_true",
                      help="Run in offline mode (disable network connections)")
    parser.add_argument("--nodebugger", action="store_true",
                      help="Disable Lua debugger (mobdebug) connection attempts")
    parser.add_argument("--debugger-port", type=int, default=8172,
                      help="Port for Lua debugger (mobdebug) connection (default: 8172)")
    parser.add_argument("--debugger-host", type=str, default="localhost",
                      help="Host for Lua debugger (mobdebug) connection (default: localhost)")
    parser.add_argument("--run-for", type=int, default=None,
                      help="Maximum time to run in seconds before terminating (-1 for indefinite, default: terminate when script completes)")
    parser.add_argument("--fibaro", action="store_true",
                      help="Enable Fibaro API compatibility (sets config.fibaro=true)")
    parser.add_argument("--header", "-H", action="append", dest="headers",
                      help="Add QuickApp header (can be specified multiple times, collected in config.headers table)")
    
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
    
    # Create config table with CLI flags
    config = create_config_table(
        offline=args.offline, 
        nodebugger=args.nodebugger,
        debugger_host=getattr(args, 'debugger_host', 'localhost'),
        debugger_port=getattr(args, 'debugger_port', 8172),
        run_for=args.run_for,
        fibaro=args.fibaro,
        headers=args.headers or []
    )
    
    # Run EPLua
    try:
        run_eplua_simple(script_path, args.fragments or [], config)
    except KeyboardInterrupt:
        safe_print("\n👋 EPLua terminated by user", "\n[WAVE] EPLua terminated by user")
    except Exception as e:
        safe_print(f"❌ EPLua error: {e}", f"[ERROR] EPLua error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
