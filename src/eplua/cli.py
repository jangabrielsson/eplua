#!/usr/bin/env python3
"""
EPLua CLI - Python Lua Engine with Web UI

Simplified single-threaded architecture for running Lua scripts.
- Single thread architecture (main=lua engine)
- Interactive REPL mode with command history
- Focused on web UI without tkinter complexity
"""

import asyncio
import sys
import argparse
import io
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


# Fix Windows Unicode output issues
def setup_unicode_output():
    """Setup proper Unicode output for Windows console"""
    if sys.platform == "win32":
        try:
            # Try to set console to UTF-8 mode (Windows 10 1903+)
            os.system("chcp 65001 >nul 2>&1")

            # Wrap stdout/stderr with UTF-8 encoding
            if hasattr(sys.stdout, "buffer"):
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace"
                )
            if hasattr(sys.stderr, "buffer"):
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding="utf-8", errors="replace"
                )
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
            ascii_message = fallback_message
        else:
            # Convert Unicode characters to ASCII equivalents
            ascii_message = (
                message.encode("ascii", errors="replace").decode("ascii")
            )
        print(ascii_message)


def get_config():
    """Get platform and runtime configuration"""
    config = {
        "platform": sys.platform,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "architecture": "single-threaded",
        "ui_mode": "web",
        "fileSeparator": "\\\\" if sys.platform == "win32" else "/",
        "pathSeparator": ";" if sys.platform == "win32" else ":",
        "isWindows": sys.platform == "win32",
        "isMacOS": sys.platform == "darwin",
        "isLinux": sys.platform.startswith("linux"),
        "enginePath": str(Path(__file__).parent.parent).replace("\\", "\\\\"),
        "luaLibPath": str(Path(__file__).parent.parent / "lua").replace("\\", "\\\\"),
    }
    return config


def run_engine(
    script_path: Optional[str] = None,
    fragments: list = None,
    config: Dict[str, Any] = None,
):
    """Run Lua engine in main thread"""
    try:
        from eplua.engine import LuaEngine

        async def engine_main():
            try:
                # Create and configure engine
                engine = LuaEngine(config=config)

                # Setup logging level from config
                if config and "loglevel" in config:
                    import logging
                    level_name = config["loglevel"].upper()
                    if hasattr(logging, level_name):
                        level = getattr(logging, level_name)
                        logging.getLogger().setLevel(level)
                        logging.getLogger().info(f"Set logging level to {level_name}")

                # Start Lua environment and bindings
                await engine.start()
                
                # Start FastAPI server process if enabled
                if config.get("api_enabled", True):
                    try:
                        # Kill any existing process using the API port
                        api_port = config.get("api_port", 8080)
                        try:
                            import subprocess
                            # Find processes using the port
                            result = subprocess.run(
                                ["lsof", "-ti", f":{api_port}"], 
                                capture_output=True, 
                                text=True, 
                                check=False
                            )
                            if result.stdout.strip():
                                pids = result.stdout.strip().split('\n')
                                for pid in pids:
                                    if pid:
                                        safe_print(f"🔧 Killing existing process {pid} using port {api_port}")
                                        subprocess.run(["kill", "-9", pid], check=False)
                        except Exception as e:
                            # Port cleanup failed, but continue anyway
                            safe_print(f"⚠️ Port cleanup failed: {e}")
                        
                        from eplua.fastapi_process import start_fastapi_process
                        
                        # Start FastAPI in separate process
                        api_manager = start_fastapi_process(
                            host=config.get("api_host", "localhost"),
                            port=api_port,
                            config=config
                        )
                        
                        # Give process a moment to start
                        await asyncio.sleep(1.0)
                        
                        # Connect process to engine via IPC
                        def lua_executor(code: str, timeout: float = 30.0):
                            """Thread-safe Lua executor for FastAPI process"""
                            try:
                                result = engine.execute_script_from_thread(code, timeout, is_json=False)
                                return result
                            except Exception as e:
                                return {"success": False, "error": str(e)}
                                
                        api_manager.set_lua_executor(lua_executor)
                        
                        # Always set up Fibaro callback - hook will determine availability
                        def fibaro_callback(method: str, path: str, data: str = None):
                            """Thread-safe Fibaro API callback - always calls the hook"""
                            try:
                                # Call Lua fibaro hook - always available in init.lua
                                # Return both values in a table to capture them properly
                                lua_code = f'local data, status = _PY.fibaroApiHook("{method}", "{path}", {data or "nil"}); return {{data=data, status=status}}'
                                result = engine.execute_script_from_thread(lua_code, 30.0, is_json=False)
                                
                                if result.get("success", False):
                                    # Result should be a table with data and status
                                    lua_result = result.get("result", {})
                                    if isinstance(lua_result, dict):
                                        hook_data = lua_result.get("data")
                                        hook_status = lua_result.get("status", 200)
                                        return hook_data, hook_status
                                    else:
                                        # Fallback for unexpected format
                                        return lua_result, 200
                                else:
                                    return "Lua execution error", 500
                                    
                            except Exception as e:
                                return f"Callback error: {str(e)}", 500
                                
                        api_manager.set_fibaro_callback(fibaro_callback)
                            
                        safe_print(f"🌐 FastAPI server process started at http://{config.get('api_host')}:{config.get('api_port')}")
                        safe_print("📡 Using multi-process architecture for maximum stability")
                        
                    except Exception as e:
                        safe_print(f"⚠️ Failed to start FastAPI server process: {e}")
                        safe_print("Continuing without API server...")

                if script_path:
                    safe_print(f"📄 Running script: {script_path}")
                    await engine.run_script(
                        f'_PY.mainLuaFile("{script_path}")', script_path
                    )
                elif fragments:
                    safe_print("📝 Running Lua fragments...")
                    for i, fragment in enumerate(fragments):
                        await engine.run_script(fragment, f"fragment_{i}")
                else:
                    safe_print("🎮 Starting interactive mode...")
                
                # Keep the engine running if there are active operations (timers, callbacks, etc.)
                if engine.has_active_operations():
                    safe_print("⏳ Keeping engine alive due to active operations (timers, callbacks, etc.)")
                    while engine.has_active_operations():
                        await asyncio.sleep(1)
                    safe_print("✅ All operations completed, shutting down")
                elif not script_path and not fragments:
                    # Interactive mode - keep running indefinitely
                    while True:
                        await asyncio.sleep(1)
                else:
                    # Script completed - check for active operations with timeout
                    safe_print("📋 Script completed, checking for active operations...")
                    await asyncio.sleep(0.5)  # Brief grace period for cleanup
                    
                    if not engine.has_active_operations():
                        safe_print("✅ No active operations detected - forcing clean shutdown")
                        # Force immediate termination - bypass any hanging background processes
                        import os
                        import sys
                        sys.stdout.flush()
                        sys.stderr.flush()
                        os._exit(0)
                    else:
                        safe_print("⏳ Active operations detected, will keep running")
                        while engine.has_active_operations():
                            await asyncio.sleep(1)
                        safe_print("✅ All operations completed - forcing shutdown")
                        import os
                        import sys
                        sys.stdout.flush()
                        sys.stderr.flush()
                        os._exit(0)

            except KeyboardInterrupt:
                safe_print("🛑 Interrupted by user")
            except Exception as e:
                safe_print(f"❌ Engine error: {e}", f"[ERROR] Engine error: {e}")
            finally:
                # Clean up FastAPI server process
                try:
                    from eplua.fastapi_process import stop_fastapi_process
                    stop_fastapi_process()
                except Exception:
                    pass

        # Run the async engine
        asyncio.run(engine_main())

    except ImportError as e:
        safe_print(f"❌ Import error: {e}", f"[ERROR] Import error: {e}")
    except Exception as e:
        safe_print(f"❌ Unexpected error: {e}", f"[ERROR] Unexpected error: {e}")


def run_script_with_config(
    script_path: Optional[str] = None, 
    fragments: list = None, 
    config: Dict[str, Any] = None,
    force_no_gui: bool = False
):
    """Main entry point for running scripts"""
    
    config = config or get_config()
    
    # Always use simplified single-threaded architecture
    safe_print(
        "🚀 EPLua - Python Lua Engine",
        "[EPLua] EPLua - Python Lua Engine",
    )
    safe_print("============================")
    safe_print("ℹ️ Activated .venv virtual environment")
    safe_print(
        "📟 Single-threaded mode - engine running in main thread",
        "[SIMPLE] Single-threaded mode - engine running in main thread",
    )

    # Setup basic stub UI functions (for compatibility)
    def setup_stub_functions():
        """Setup stub UI functions when web UI is not yet implemented"""
        from eplua.lua_bindings import export_to_lua

        @export_to_lua("gui_available")
        def gui_available() -> bool:
            return False

        @export_to_lua("isNativeUIAvailable") 
        def is_native_ui_available() -> bool:
            return False

        @export_to_lua("createNativeWindow")
        def create_native_window(
            title: str, width: int = 400, height: int = 300
        ) -> str:
            return "ERROR: Web UI not yet implemented"

    setup_stub_functions()

    # Run engine in main thread
    run_engine(script_path, fragments, config)


def run_interactive_repl():
    """Start interactive REPL mode by spawning a REPL client process"""
    try:
        # The telnet server should already be running in the current EPLua process
        # We just need to spawn the REPL client process
        safe_print("📟 Starting REPL client...")
        safe_print("Connecting to telnet server on localhost:8080...")

        # Find the repl.py file
        repl_path = Path(__file__).parent / "repl.py"
        if not repl_path.exists():
            safe_print("❌ REPL client not found")
            return

        # Spawn the REPL client process
        subprocess.run([sys.executable, str(repl_path)], check=False)

    except KeyboardInterrupt:
        safe_print("🛑 REPL interrupted")
    except Exception as e:
        safe_print(f"❌ REPL error: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="EPLua - Python Lua Engine with Web UI"
    )
    parser.add_argument(
        "script", nargs="?", help="Lua script file to run (optional)"
    )
    parser.add_argument(
        "-e", "--eval", action="append", help="Execute Lua code fragments"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Start REPL mode"
    )
    parser.add_argument(
        "--loglevel",
        choices=["debug", "info", "warning", "error"],
        default="warning",
        help="Set logging level",
    )
    parser.add_argument(
        "-o",
        "--offline",
        action="store_true",
        help="Run in offline mode (disable network connections)",
    )
    parser.add_argument(
        "--nodebugger",
        action="store_true",
        help="Disable Lua debugger support",
    )
    parser.add_argument(
        "--fibaro",
        action="store_true",
        help="Enable Fibaro HC3 emulation mode",
    )
    parser.add_argument(
        "-l",
        help="Ignored, for compatibility with Lua CLI",
    )
    parser.add_argument(
        "--header",
        action="append",
        help="Add header string (can be used multiple times)",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8080,
        help="Port for FastAPI server (default: 8080)",
    )
    parser.add_argument(
        "--api-host",
        default="localhost", 
        help="Host for FastAPI server (default: localhost)",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Disable FastAPI server",
    )
    parser.add_argument(
        "--run-for",
        type=int,
        help="Run script for specified seconds then terminate",
    )

    args = parser.parse_args()

    # Prepare config
    config = get_config()
    config["loglevel"] = args.loglevel
    config["offline"] = args.offline
    config["debugger"] = not args.nodebugger
    config["fibaro"] = args.fibaro
    config["headers"] = args.header or []
    config["api_enabled"] = not args.no_api
    config["api_host"] = args.api_host
    config["api_port"] = args.api_port
    config["runFor"] = args.run_for

    if args.interactive:
        run_interactive_repl()
    else:
        run_script_with_config(
            script_path=args.script,
            fragments=args.eval,
            config=config,
        )


if __name__ == "__main__":
    main()