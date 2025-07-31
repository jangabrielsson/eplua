"""
Native UI Module for EPLua
Wrapper around gui.py for native tkinter-based UI building
"""

import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Try to import gui module with error handling
try:
    from . import gui
    _GUI_IMPORT_SUCCESS = True
    logger.info("GUI module imported successfully in native_ui")
except Exception as e:
    _GUI_IMPORT_SUCCESS = False
    logger.error(f"Failed to import GUI module in native_ui: {e}")
    gui = None

# Window registry for native UI windows
native_window_registry: Dict[str, 'NativeUIWindow'] = {}
logger.info(f"Native UI registry initialized: {len(native_window_registry)} windows")

class NativeUIWindow:
    """A native UI window that wraps gui.UIWindow"""
    
    def __init__(self, window_id: str, title: str, width: int, height: int):
        self.window_id = window_id
        self.title = title
        self.width = width
        self.height = height
        self.ui_window = None
        self._callbacks = {}
        logger.info(f"Created NativeUIWindow: {window_id}")
        
    def create_window(self):
        """Create the actual GUI window (or use existing one)"""
        if self.ui_window:
            return self.ui_window
            
        if not _GUI_IMPORT_SUCCESS or not gui.GUI_AVAILABLE:
            raise RuntimeError("GUI not available")
            
        # This should only be called if ui_window wasn't set in create_native_window
        self.ui_window = gui.create_native_window(self.title, self.width, self.height)
        self.window_id = self.ui_window.window_id
        logger.info(f"Created GUI window with ID: {self.window_id}")
        return self.ui_window
        
    def set_ui(self, ui_description: Dict[str, Any]):
        """Set UI from description"""
        if not self.ui_window:
            self.create_window()
            
        # Build UI from description using the correct method
        logger.info(f"Setting UI for window {self.window_id}")
        self.ui_window.set_ui(ui_description)
        
    def set_callback(self, element_id: str, callback: Callable):
        """Set callback for an element"""
        logger.info(f"Setting callback for {element_id} in window {self.window_id}")
        self._callbacks[element_id] = callback
        if self.ui_window:
            self.ui_window.set_callback(element_id, callback)
    
    def get_value(self, element_id: str):
        """Get value of an element"""
        if self.ui_window:
            logger.info(f"Getting value for {element_id} in window {self.window_id}")
            return self.ui_window.get_value(element_id)
        return None
    
    def set_value(self, element_id: str, value):
        """Set value of an element"""
        if self.ui_window:
            logger.info(f"Setting value for {element_id} in window {self.window_id} to {value}")
            self.ui_window.set_value(element_id, value)
            
    def show(self):
        """Show the window"""
        if self.ui_window:
            logger.info(f"Showing window {self.window_id}")
            self.ui_window.show()
            
    def hide(self):
        """Hide the window"""
        if self.ui_window:
            logger.info(f"Hiding window {self.window_id}")
            self.ui_window.hide()
            
    def close(self):
        """Close the window"""
        if self.ui_window:
            logger.info(f"Closing window {self.window_id}")
            self.ui_window.close()
        # Remove from registry
        if self.window_id in native_window_registry:
            del native_window_registry[self.window_id]


def create_native_window(title: str, width: int = 800, height: int = 600) -> NativeUIWindow:
    """Create a new native UI window"""
    if not is_native_ui_available():
        raise RuntimeError("Native UI not available")
        
    logger.info(f"Starting window creation for: {title}")
    
    # Create the actual GUI window first to get its ID
    ui_window = gui.create_native_window(title, width, height)
    logger.info(f"Created GUI window object with ID: {ui_window.window_id}")
    
    ui_window.create()  # Important: Create the window immediately so it's registered
    logger.info(f"Called create() on GUI window")
    
    window_id = ui_window.window_id
    logger.info(f"Final window ID: {window_id}")
    
    # Create wrapper with the same ID
    window = NativeUIWindow(window_id, title, width, height)
    window.ui_window = ui_window  # Use the already created window
    
    # Register with the actual window ID
    native_window_registry[window_id] = window
    logger.info(f"Registered window in registry: {window_id}")
    logger.info(f"Registry now has {len(native_window_registry)} windows")
    
    logger.info(f"Created native UI window: {window_id}")
    return window


def is_native_ui_available() -> bool:
    """Check if native UI is available"""
    return _GUI_IMPORT_SUCCESS and gui and gui.GUI_AVAILABLE


def get_window(window_id: str) -> Optional[NativeUIWindow]:
    """Get window by ID"""
    return native_window_registry.get(window_id)


def list_windows() -> Dict[str, Dict[str, Any]]:
    """List all native UI windows"""
    result = {}
    for window_id, window in native_window_registry.items():
        result[window_id] = {
            'title': window.title,
            'width': window.width,
            'height': window.height
        }
    return result


def close_all_windows():
    """Close all native UI windows"""
    for window in list(native_window_registry.values()):
        try:
            window.close()
        except Exception as e:
            logger.error(f"Error closing window {window.window_id}: {e}")
    native_window_registry.clear()

# Log module initialization
logger.info(f"Native UI module initialized. Available: {is_native_ui_available()}")
