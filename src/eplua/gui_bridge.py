"""
GUI Bridge Module for EPLua
Handles thread-safe communication between EPLua engine and GUI components
"""

import tkinter as tk
import queue
import time
import uuid
import re
from typing import Dict, Any
import json
from typing import Any, Dict, Optional

# Check if GUI is available
try:
    import tkinter as tk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


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
            
        # Create a hidden root window for tkinter
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        
        # Schedule command processing
        self._schedule_command_processing()
        
        # Start tkinter mainloop - this is essential for proper GUI operation
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup_all_windows()
            self.bridge.stop()
    
    def _schedule_command_processing(self):
        """Schedule command processing using tkinter's after method"""
        if self.bridge.running and self.root:
            self._process_commands()
            # Schedule next processing cycle
            self.root.after(10, self._schedule_command_processing)
    
    def _cleanup_all_windows(self):
        """Close all open windows and cleanup resources"""
        try:
            # Close all windows
            for window_id, window in list(self.windows.items()):
                try:
                    window.close()
                except Exception:
                    pass
            self.windows.clear()
            
            # Destroy root window if it exists
            if self.root:
                try:
                    self.root.quit()
                    self.root.destroy()
                except Exception:
                    pass
                self.root = None
        except Exception:
            pass
    
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
        
        # No need to schedule next check - handled by _process_commands_loop
    
    def _execute_command(self, cmd_data: Dict[str, Any]) -> Any:
        """Execute a GUI command"""
        command = cmd_data['command']
        args = cmd_data['args']
        
        try:
            # Legacy command aliases for backward compatibility
            if command == 'create_window':
                return self._create_native_window(**args)
            elif command == 'set_window_html':
                return self._set_window_html(**args)
            elif command == 'show_window':
                return self._show_native_window(**args)
            elif command == 'hide_window':
                return self._hide_native_window(**args)
            elif command == 'close_window':
                return self._close_native_window(**args)
            elif command == 'list_windows':
                return self._list_native_windows()
            # Core GUI functions
            elif command == 'gui_available':
                return True
            elif command == 'html_rendering_available':
                return self._html_rendering_available()
            elif command == 'get_html_engine':
                return self._get_html_engine()
            # Native window commands
            elif command == 'create_native_window':
                return self._create_native_window(**args)
            elif command == 'set_native_ui':
                return self._set_native_ui(**args)
            elif command == 'set_native_ui_structured':
                return self._set_native_ui_structured(**args)
            elif command == 'show_native_window':
                return self._show_native_window(**args)
            elif command == 'hide_native_window':
                return self._hide_native_window(**args)
            elif command == 'close_native_window':
                return self._close_native_window(**args)
            elif command == 'list_native_windows':
                return self._list_native_windows()
            elif command == 'update_element':
                return self._update_element(**args)
            elif command == 'get_element_value':
                return self._get_element_value(**args)
            else:
                return f"ERROR: Unknown command: {command}"
        except Exception as e:
            return f"ERROR: {e}"
    
    def _set_window_html(self, window_id: str, content: str) -> str:
        """For backward compatibility - now just redirects to native UI for JSON"""
        # Only handle JSON content, ignore HTML
        if content.strip().startswith('{'):
            # Parse and set native UI directly without recursion
            try:
                if window_id not in self.windows:
                    return f"ERROR: Window {window_id} not found"
                
                window = self.windows[window_id]
                ui_description = json.loads(content)
                window.set_ui(ui_description)
                return "SUCCESS: Native UI set via HTML compatibility"
            except json.JSONDecodeError as e:
                return f"ERROR: Invalid JSON: {e}"
            except Exception as e:
                return f"ERROR: Failed to set UI: {e}"
        else:
            return "ERROR: HTML content not supported in native-only mode"
    
    def _html_rendering_available(self) -> bool:
        """Check if HTML rendering is available - always False for native-only mode"""
        return False
    
    def _get_html_engine(self) -> str:
        """Get HTML engine name - always 'none' for native-only mode"""
        return "none"

    def _create_native_window(self, title: str, width: int = 400, height: int = 300) -> Dict[str, Any]:
        """Create a new native UI window"""
        try:
            from eplua.gui import UIWindow
            
            window_id = str(uuid.uuid4())
            window = UIWindow(window_id, title, width, height)
            window.create()  # Use normal window creation
            
            self.windows[window_id] = window
            
            # IMPORTANT: Also register in native_ui registry for callback support
            try:
                from eplua import native_ui
                # Create a wrapper for native UI registry
                class BridgeNativeUIWindow:
                    def __init__(self, ui_window):
                        self.window_id = ui_window.window_id
                        self.title = ui_window.title
                        self.width = ui_window.width
                        self.height = ui_window.height
                        self.ui_window = ui_window
                        self._callbacks = {}
                    
                    def set_callback(self, element_id: str, callback_func):
                        """Set callback for an element"""
                        self._callbacks[element_id] = callback_func
                        if self.ui_window:
                            # Import here to avoid circular imports
                            from .lua_bindings import get_global_engine
                            
                            # Create a proper async callback that uses EPLua's callback system
                            def gui_callback(data):
                                # Get the global engine to post the callback
                                engine = get_global_engine()
                                if engine and callback_func:
                                    # Use EPLua's thread-safe callback posting
                                    # The callback_func is actually a callback_id from Lua's registerCallback
                                    # We need to call it directly in this thread and let EPLua handle the threading
                                    try:
                                        # Call the Lua callback function directly
                                        callback_func(data)
                                    except Exception as e:
                                        import logging
                                        logging.error(f"Error in GUI callback for {element_id}: {e}")
                                        print(f"[GUI] Error in callback for {element_id}: {e}")
                                else:
                                    print(f"[GUI] No engine or callback for {element_id}: {data}")
                            
                            self.ui_window.set_callback(element_id, gui_callback)
                    
                    def set_ui(self, ui_description):
                        """Set UI description"""
                        if self.ui_window:
                            self.ui_window.set_ui(ui_description)
                    
                    def set_value(self, element_id: str, value):
                        """Set value for an element"""
                        if self.ui_window:
                            self.ui_window.set_value(element_id, value)
                    
                    def get_value(self, element_id: str):
                        """Get value for an element"""
                        if self.ui_window:
                            return self.ui_window.get_value(element_id)
                        return None
                    
                    def show(self):
                        """Show the window"""
                        if self.ui_window:
                            self.ui_window.show()
                    
                    def close(self):
                        """Close the window"""
                        if self.ui_window:
                            self.ui_window.close()
                
                bridge_wrapper = BridgeNativeUIWindow(window)
                native_ui.native_window_registry[window_id] = bridge_wrapper
            except Exception as reg_error:
                print(f"[DEBUG] Failed to register in native UI registry: {reg_error}")
            
            # Return table format like the direct version
            return {
                "window_id": window_id,
                "title": title, 
                "width": width,
                "height": height
            }
        except Exception as e:
            return {"error": f"Failed to create native window: {e}"}

    def _set_native_ui(self, window_id: str, ui_json: str) -> str:
        """Set UI description for a window using JSON"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            
            # Parse JSON UI description
            try:
                ui_description = json.loads(ui_json)
                window.set_ui(ui_description)
                return "SUCCESS: Native UI set"
            except json.JSONDecodeError as e:
                return f"ERROR: Invalid JSON: {e}"
                
        except Exception as e:
            return f"ERROR: Failed to set native UI: {e}"

    def _set_native_ui_structured(self, window_id: str, ui_definition: list) -> str:
        """Set structured UI description for a native window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            
            # Wrap the list in a dictionary with 'elements' key
            ui_dict = {
                "elements": ui_definition,
                "padding": 10
            }
            
            window.set_ui(ui_dict)
            return "SUCCESS: Structured UI set"
        except Exception as e:
            return f"ERROR: Failed to set structured UI: {e}"

    def _show_native_window(self, window_id: str) -> str:
        """Show a native window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.show()
            return "SUCCESS: Native window shown"
        except Exception as e:
            return f"ERROR: Failed to show native window: {e}"

    def _hide_native_window(self, window_id: str) -> str:
        """Hide a native window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.hide()
            return "SUCCESS: Native window hidden"
        except Exception as e:
            return f"ERROR: Failed to hide native window: {e}"

    def _close_native_window(self, window_id: str) -> str:
        """Close and destroy a native window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            window.close()
            del self.windows[window_id]
            return "SUCCESS: Native window closed"
        except Exception as e:
            return f"ERROR: Failed to close native window: {e}"

    def _list_native_windows(self) -> str:
        """List all open windows (now same as regular list_windows)"""
        return self._list_windows()

    def _update_element(self, window_id: str, element_id: str, property_name: str, value) -> str:
        """Update a specific element property in a window"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            result = window.update_element(element_id, property_name, value)
            return "SUCCESS: Element updated" if result else f"ERROR: Failed to update element {element_id}"
        except Exception as e:
            return f"ERROR: Failed to update element: {e}"

    def _get_element_value(self, window_id: str, element_id: str) -> str:
        """Get the current value of an element"""
        try:
            if window_id not in self.windows:
                return f"ERROR: Window {window_id} not found"
            
            window = self.windows[window_id]
            value = window.get_element_value(element_id)
            return json.dumps({"success": True, "value": value}) if value is not None else json.dumps({"success": False, "error": "Element not found"})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})


def replace_gui_functions_with_bridge(engine, bridge: ThreadSafeGUIBridge):
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

    def create_native_window(title: str, width: int = 400, height: int = 300):
        if not GUI_AVAILABLE:
            return {"error": "GUI not available"}
        result = bridge.send_gui_command('create_native_window', title=title, width=width, height=height)
        # Convert result to Lua table format if it's a dict
        if isinstance(result, dict):
            try:
                from .lua_bindings import python_to_lua_table
                lua_result = python_to_lua_table(result)
                return lua_result
            except Exception as e:
                return result
        return result

    def set_native_ui(window_id: str, ui_definition) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        
        # Convert Lua table to Python dict if needed
        if hasattr(ui_definition, 'values'):  # Lua table
            from .lua_bindings import lua_to_python_table
            ui_definition = lua_to_python_table(ui_definition)
        
        # Handle list/array UI definitions (our structured format)
        if isinstance(ui_definition, list):
            # Use the bridge system to send the structured UI to the main thread
            return bridge.send_gui_command('set_native_ui_structured', window_id=window_id, ui_definition=ui_definition)
        
        # Convert to JSON string if it's a dict
        if isinstance(ui_definition, dict):
            import json
            ui_json = json.dumps(ui_definition)
        elif isinstance(ui_definition, str):
            ui_json = ui_definition
        else:
            return f"ERROR: Invalid UI definition type: {type(ui_definition)}"
            
        result = bridge.send_gui_command('set_native_ui', window_id=window_id, ui_json=ui_json)
        return result

    def show_native_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('show_native_window', window_id=window_id)

    def hide_native_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('hide_native_window', window_id=window_id)

    def close_native_window(window_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('close_native_window', window_id=window_id)

    def list_native_windows() -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('list_native_windows')

    def update_element(window_id: str, element_id: str, property_name: str, value) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('update_element', window_id=window_id, element_id=element_id, property_name=property_name, value=value)

    def get_element_value(window_id: str, element_id: str) -> str:
        if not GUI_AVAILABLE:
            return "ERROR: GUI not available"
        return bridge.send_gui_command('get_element_value', window_id=window_id, element_id=element_id)
    
    # Replace the exported functions directly in the Lua environment
    py_table = engine.get_lua_global("_PY")
    py_table.gui_available = gui_available
    py_table.html_rendering_available = html_rendering_available
    py_table.get_html_engine = get_html_engine
    
    # Legacy aliases (for backward compatibility) - these use the bridge's command aliases
    py_table.create_window = create_native_window  # Legacy alias for createNativeWindow
    py_table.set_window_html = set_native_ui        # Legacy alias for setNativeUI (JSON only)
    py_table.show_window = show_native_window       # Legacy alias for showNativeWindow
    py_table.hide_window = hide_native_window       # Legacy alias for hideNativeWindow 
    py_table.close_window = close_native_window     # Legacy alias for closeNativeWindow
    py_table.list_windows = list_native_windows     # Legacy alias for listNativeWindows
    
    # Native functions (primary interface)
    py_table.createNativeWindow = create_native_window
    py_table.setNativeUI = set_native_ui
    py_table.showNativeWindow = show_native_window
    py_table.hideNativeWindow = hide_native_window
    py_table.closeNativeWindow = close_native_window
    py_table.listNativeWindows = list_native_windows
    py_table.updateElement = update_element
    py_table.getElementValue = get_element_value
