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
import queue
import time
import os
from typing import Any, Dict, Optional
from eplua import LuaEngine

__version__ = "0.1.0"

# Check if GUI is available
try:
    import tkinter as tk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(name)s - %(levelname)s - %(message)s'
    )


class ThreadSafeGUIBridge:
    """Bridge for thread-safe communication between EPLua engine and GUI"""
    
    def __init__(self):
        self.command_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.running = False
        
    def send_gui_command(self, command: str, **kwargs) -> Any:
        """Send a command to the GUI thread and wait for result"""
        if not self.running:
            return "ERROR: GUI bridge not running"
        
        # Create a unique command ID
        cmd_id = f"cmd_{time.time()}"
        cmd_data = {
            'id': cmd_id,
            'command': command,
            'args': kwargs
        }
        
        # Send command to GUI thread
        self.command_queue.put(cmd_data)
        
        # Wait for result (with timeout)
        timeout = 10  # 10 second timeout
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = self.result_queue.get(timeout=0.1)
                if result.get('id') == cmd_id:
                    return result.get('result', 'No result')
            except queue.Empty:
                continue
        
        return "ERROR: GUI command timeout"
    
    def start(self):
        """Start the bridge"""
        self.running = True
    
    def stop(self):
        """Stop the bridge"""
        self.running = False


class GUIManager:
    """Manages the GUI in the main thread"""
    
    def __init__(self, bridge: ThreadSafeGUIBridge):
        self.bridge = bridge
        self.root = None
        self.windows = {}
        
    def start_gui_loop(self):
        """Start the GUI event loop in main thread"""
        if not GUI_AVAILABLE:
            return
        
        # Initialize tkinter
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        self.root.title("EPLua GUI Manager")
        
        # Process GUI commands
        self.root.after(100, self._process_commands)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self.bridge.stop()
    
    def _process_commands(self):
        """Process commands from the engine thread"""
        if not self.bridge.running:
            return
        
        try:
            # Process all pending commands
            while True:
                try:
                    cmd_data = self.bridge.command_queue.get_nowait()
                    result = self._execute_command(cmd_data)
                    
                    # Send result back
                    self.bridge.result_queue.put({
                        'id': cmd_data['id'],
                        'result': result
                    })
                except queue.Empty:
                    break
        except Exception as e:
            pass
        
        # Schedule next check
        if self.bridge.running:
            self.root.after(50, self._process_commands)
    
    def _execute_command(self, cmd_data: Dict[str, Any]) -> Any:
        """Execute a GUI command"""
        command = cmd_data['command']
        args = cmd_data['args']
        
        try:
            if command == 'create_window':
                return self._create_window(**args)
            elif command == 'set_window_html':
                return self._set_window_html(**args)
            elif command == 'show_window':
                return self._show_window(**args)
            elif command == 'hide_window':
                return self._hide_window(**args)
            elif command == 'close_window':
                return self._close_window(**args)
            elif command == 'list_windows':
                return self._list_windows()
            elif command == 'gui_available':
                return True
            elif command == 'html_rendering_available':
                return self._html_rendering_available()
            elif command == 'get_html_engine':
                return self._get_html_engine()
            else:
                return f"ERROR: Unknown command: {command}"
        except Exception as e:
            return f"ERROR: {e}"
    
    def _create_window(self, title: str, width: int = 800, height: int = 600) -> str:
        """Create a new window"""
        try:
            from eplua.gui import HTMLWindow
            import uuid
            
            window_id = str(uuid.uuid4())
            window = HTMLWindow(window_id, title, width, height)
            window.create()
            
            self.windows[window_id] = window
            return window_id
        except Exception as e:
            return f"ERROR: Failed to create window: {e}"
    
    def _set_window_html(self, window_id: str, html_content: str) -> str:
        """Set HTML content for a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.set_html(html_content)
            return "SUCCESS: HTML content set"
        except Exception as e:
            return f"ERROR: Failed to set HTML content: {e}"
    
    def _show_window(self, window_id: str) -> str:
        """Show a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.show()
            return "SUCCESS: Window shown"
        except Exception as e:
            return f"ERROR: Failed to show window: {e}"
    
    def _hide_window(self, window_id: str) -> str:
        """Hide a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.hide()
            return "SUCCESS: Window hidden"
        except Exception as e:
            return f"ERROR: Failed to hide window: {e}"
    
    def _close_window(self, window_id: str) -> str:
        """Close and destroy a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.close()
            del self.windows[window_id]
            return "SUCCESS: Window closed"
        except Exception as e:
            return f"ERROR: Failed to close window: {e}"
    
    def _list_windows(self) -> str:
        """List all open windows"""
        if not self.windows:
            return "No windows open"
        
        windows_info = []
        for window_id, window in self.windows.items():
            status = "created" if window.created else "not created"
            windows_info.append(f"  {window_id}: '{window.title}' ({status})")
        
        return f"Open windows ({len(self.windows)}):\n" + "\n".join(windows_info)
    
    def _html_rendering_available(self) -> bool:
        """Check if HTML rendering is available"""
        try:
            from eplua.gui import HTML_RENDERING_AVAILABLE
            return HTML_RENDERING_AVAILABLE
        except:
            return False
    
    def _get_html_engine(self) -> str:
        """Get HTML engine name"""
        try:
            from eplua.gui import HTML_ENGINE
            return HTML_ENGINE
        except:
            return "none"


def run_eplua_engine(script_path: str, fragments: list, bridge: Optional[ThreadSafeGUIBridge] = None):
    """Run EPLua engine in worker thread (or main thread if no GUI)"""
    async def engine_main():
        try:
            async with LuaEngine() as engine:
                # Replace GUI functions with bridge versions if using GUI
                if bridge:
                    _replace_gui_functions_with_bridge(engine, bridge)
                
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


def _replace_gui_functions_with_bridge(engine, bridge: ThreadSafeGUIBridge):
    """Replace GUI functions in the engine with bridge versions"""
    
    # Thread-safe GUI function wrappers
    def gui_available() -> bool:
        if not GUI_AVAILABLE:
            return False
        return bridge.send_gui_command('gui_available')
    
    def html_rendering_available() -> bool:
        if not GUI_AVAILABLE:
            return False
        return bridge.send_gui_command('html_rendering_available')
    
    def get_html_engine() -> str:
        if not GUI_AVAILABLE:
            return "none"
        return bridge.send_gui_command('get_html_engine')
    
    def create_window(title: str, width: int = 800, height: int = 600) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('create_window', title=title, width=width, height=height)
    
    def set_window_html(window_id: str, html_content: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('set_window_html', window_id=window_id, html_content=html_content)
    
    def show_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('show_window', window_id=window_id)
    
    def hide_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('hide_window', window_id=window_id)
    
    def close_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('close_window', window_id=window_id)
    
    def list_windows() -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('list_windows')
    
    # Replace the exported functions directly in the Lua environment
    py_table = engine.get_lua_global("_PY")
    py_table.gui_available = gui_available
    py_table.html_rendering_available = html_rendering_available
    py_table.get_html_engine = get_html_engine
    py_table.create_window = create_window
    py_table.set_window_html = set_window_html
    py_table.show_window = show_window
    py_table.hide_window = hide_window
    py_table.close_window = close_window
    py_table.list_windows = list_windows


def detect_gui_usage(script_path: str, fragments: list) -> bool:
    """Detect if the script or fragments use GUI functions"""
    gui_functions = [
        'create_window', 'show_window', 'hide_window', 'close_window',
        'set_window_html', 'list_windows'
    ]
    
    # Check fragments
    if fragments:
        for fragment in fragments:
            for func in gui_functions:
                if f'_PY.{func}' in fragment:
                    return True
    
    # Check script file
    if script_path and os.path.exists(script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for func in gui_functions:
                    if f'_PY.{func}' in content:
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
