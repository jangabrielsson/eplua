"""
EPLua GUI Module with HTML Rendering Support

This module provides GUI capabilities using tkinter with HTML/CSS/JS rendering
via tkinterweb. Windows can be created, controlled, and closed from Lua scripts.
"""

import logging
import threading
import uuid
from typing import Dict, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Global state
window_registry: Dict[str, 'HTMLWindow'] = {}
main_app = None
gui_thread = None

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    TKINTER_AVAILABLE = True
    logger.info("tkinter is available")
except ImportError:
    TKINTER_AVAILABLE = False
    logger.warning("tkinter is not available")

try:
    from tkhtmlview import HTMLScrolledText
    HTML_RENDERING_AVAILABLE = True
    HTML_ENGINE = "tkhtmlview"
    logger.info("tkhtmlview is available for HTML rendering")
except ImportError:
    try:
        import tkinterweb
        HTML_RENDERING_AVAILABLE = True
        HTML_ENGINE = "tkinterweb"
        logger.info("tkinterweb is available for HTML rendering")
    except ImportError:
        HTML_RENDERING_AVAILABLE = False
        HTML_ENGINE = "none"
        logger.warning("No HTML rendering library available")


class HTMLWindow:
    """A tkinter window with HTML rendering capability"""
    
    def __init__(self, window_id: str, title: str, width: int = 800, height: int = 600):
        self.window_id = window_id
        self.title = title
        self.width = width
        self.height = height
        self.window = None
        self.html_widget = None
        self.created = False
        
    def create(self):
        """Create the actual tkinter window"""
        try:
            # Create window
            self.window = tk.Toplevel() if main_app else tk.Tk()
            self.window.title(self.title)
            self.window.geometry(f"{self.width}x{self.height}")
            
            # Try to create HTML widget if available
            html_widget_created = False
            if HTML_RENDERING_AVAILABLE:
                try:
                    if HTML_ENGINE == "tkhtmlview":
                        # Use tkhtmlview (works with Tcl 9.x)
                        self.html_widget = HTMLScrolledText(self.window, html="<h1>Loading...</h1>")
                        self.html_widget.pack(fill=tk.BOTH, expand=True)
                        html_widget_created = True
                        logger.info(f"tkhtmlview HTML widget created for window {self.window_id}")
                    elif HTML_ENGINE == "tkinterweb":
                        # Use tkinterweb (requires Tcl 8.x)
                        import tkinterweb
                        self.html_widget = tkinterweb.HtmlFrame(self.window)
                        self.html_widget.pack(fill=tk.BOTH, expand=True)
                        html_widget_created = True
                        logger.info(f"tkinterweb HTML widget created for window {self.window_id}")
                except Exception as e:
                    logger.warning(f"Failed to create HTML widget ({HTML_ENGINE}): {e}")
                    html_widget_created = False
            
            if not html_widget_created:
                self._create_text_fallback()
            
            # Hide window initially
            self.window.withdraw()
            self.created = True
            logger.info(f"Window {self.window_id} created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create window {self.window_id}: {e}")
            raise
    
    def _create_text_fallback(self):
        """Create a text widget fallback when HTML rendering fails"""
        # Create a frame for the text widget and scrollbar
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with scrollbar
        self.html_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 12))
        scrollbar = tk.Scrollbar(frame)
        
        # Configure scrolling
        self.html_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.html_widget.yview)
        
        # Pack widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.html_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add welcome message
        welcome_msg = f"""
EPLua Window: {self.title}

HTML rendering not available due to compatibility issues.
This is a text-only fallback.

HTML content and URLs will be displayed as text below.

---

Window ID: {self.window_id}
Size: {self.width}x{self.height}

✓ Window creation: Working
✗ HTML rendering: Not available (tkinterweb compatibility issue)
✓ Text display: Working
✓ Window controls: Working

---

"""
        self.html_widget.insert(tk.END, welcome_msg)
        logger.warning(f"Using text widget fallback for window {self.window_id}")
    
    def set_html(self, html_content: str):
        """Set HTML content in the window"""
        if not self.created or not self.html_widget:
            raise ValueError("Window not created yet")
        
        try:
            # Check which HTML widget we have
            if HTML_ENGINE == "tkhtmlview" and hasattr(self.html_widget, 'set_html'):
                self.html_widget.set_html(html_content)
                logger.info(f"HTML content set for window {self.window_id} (tkhtmlview)")
            elif HTML_ENGINE == "tkinterweb" and hasattr(self.html_widget, 'load_html'):
                self.html_widget.load_html(html_content)
                logger.info(f"HTML content set for window {self.window_id} (tkinterweb)")
            else:
                # Fallback for text widget
                self.html_widget.delete(1.0, tk.END)
                self.html_widget.insert(tk.END, "HTML Content (text-only display):\n")
                self.html_widget.insert(tk.END, "=" * 50 + "\n\n")
                self.html_widget.insert(tk.END, html_content)
                logger.warning(f"HTML content displayed as text in window {self.window_id}")
        except Exception as e:
            logger.error(f"Failed to set HTML content for window {self.window_id}: {e}")
            raise
    
    def set_url(self, url: str):
        """Load a URL in the window"""
        if not self.created or not self.html_widget:
            raise ValueError("Window not created yet")
        
        try:
            # Check which HTML widget we have
            if HTML_ENGINE == "tkhtmlview":
                # tkhtmlview doesn't support direct URL loading, so we'll fetch and display
                import requests
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    self.html_widget.set_html(response.text)
                    logger.info(f"URL {url} loaded in window {self.window_id} (tkhtmlview)")
                except Exception as e:
                    error_html = f"<h1>Error loading URL</h1><p>Failed to load {url}: {e}</p>"
                    self.html_widget.set_html(error_html)
                    logger.error(f"Failed to load URL {url}: {e}")
            elif HTML_ENGINE == "tkinterweb" and hasattr(self.html_widget, 'load_url'):
                self.html_widget.load_url(url)
                logger.info(f"URL {url} loaded in window {self.window_id} (tkinterweb)")
            else:
                # Fallback for text widget
                self.html_widget.delete(1.0, tk.END)
                self.html_widget.insert(tk.END, "URL Request (text-only display):\n")
                self.html_widget.insert(tk.END, "=" * 50 + "\n\n")
                self.html_widget.insert(tk.END, f"Requested URL: {url}\n\n")
                self.html_widget.insert(tk.END, "Note: URL loading requires HTML rendering capability.\n")
                self.html_widget.insert(tk.END, "This window is using text-only fallback mode.")
                logger.warning(f"URL loading not available for window {self.window_id}")
        except Exception as e:
            logger.error(f"Failed to load URL {url} for window {self.window_id}: {e}")
            raise
    
    def show(self):
        """Show the window"""
        if not self.created:
            raise ValueError("Window not created yet")
        
        try:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            logger.info(f"Window {self.window_id} shown")
        except Exception as e:
            logger.error(f"Failed to show window {self.window_id}: {e}")
            raise
    
    def hide(self):
        """Hide the window"""
        if not self.created:
            raise ValueError("Window not created yet")
        
        try:
            self.window.withdraw()
            logger.info(f"Window {self.window_id} hidden")
        except Exception as e:
            logger.error(f"Failed to hide window {self.window_id}: {e}")
            raise
    
    def close(self):
        """Close and destroy the window"""
        if not self.created:
            return
        
        try:
            self.window.destroy()
            self.created = False
            logger.info(f"Window {self.window_id} closed")
        except Exception as e:
            logger.error(f"Failed to close window {self.window_id}: {e}")
            raise


def _ensure_main_thread():
    """Ensure we're running on the main thread (required for GUI on macOS)"""
    import platform
    if platform.system() == "Darwin":  # macOS
        if threading.current_thread() != threading.main_thread():
            raise RuntimeError("ERROR: GUI operations must run on main thread on macOS")


def _init_gui_if_needed():
    """Initialize GUI if not already done"""
    global main_app
    
    if not TKINTER_AVAILABLE:
        raise ImportError("tkinter is not available")
    
    _ensure_main_thread()
    
    if main_app is None:
        main_app = tk.Tk()
        main_app.withdraw()  # Hide the main window
        
        # Try to fix the tcl_platform issue
        try:
            main_app.tk.call('set', 'tcl_platform(threaded)', '1')
        except tk.TclError:
            # If that fails, try creating a minimal platform array
            try:
                main_app.tk.call('array', 'set', 'tcl_platform', 
                                'threaded', '1', 
                                'platform', 'unix',
                                'os', 'Darwin')
            except tk.TclError as e:
                logger.warning(f"Could not set tcl_platform: {e}")
        
        logger.info("GUI initialized")


# Functions exported to Lua
def gui_available() -> bool:
    """Check if GUI (tkinter) is available"""
    return TKINTER_AVAILABLE


def html_rendering_available() -> bool:
    """Check if HTML rendering is available"""
    return HTML_RENDERING_AVAILABLE


def get_html_engine() -> str:
    """Get the name of the HTML rendering engine"""
    return HTML_ENGINE


def create_window(title: str, width: int = 800, height: int = 600) -> str:
    """Create a new HTML-capable window"""
    try:
        _init_gui_if_needed()
        
        window_id = str(uuid.uuid4())
        window = HTMLWindow(window_id, title, width, height)
        window.create()
        
        window_registry[window_id] = window
        logger.info(f"Created window '{title}' with ID {window_id}")
        return window_id
        
    except Exception as e:
        error_msg = f"ERROR: Failed to create window: {e}"
        logger.error(error_msg)
        return error_msg


def set_window_html(window_id: str, html_content: str) -> str:
    """Set HTML content for a window"""
    try:
        if window_id not in window_registry:
            return f"ERROR: Window {window_id} not found"
        
        window = window_registry[window_id]
        window.set_html(html_content)
        return "SUCCESS: HTML content set"
        
    except Exception as e:
        error_msg = f"ERROR: Failed to set HTML content: {e}"
        logger.error(error_msg)
        return error_msg


def set_window_url(window_id: str, url: str) -> str:
    """Load a URL in a window"""
    try:
        if window_id not in window_registry:
            return f"ERROR: Window {window_id} not found"
        
        window = window_registry[window_id]
        window.set_url(url)
        return "SUCCESS: URL loaded"
        
    except Exception as e:
        error_msg = f"ERROR: Failed to load URL: {e}"
        logger.error(error_msg)
        return error_msg


def show_window(window_id: str) -> str:
    """Show a window"""
    try:
        if window_id not in window_registry:
            return f"ERROR: Window {window_id} not found"
        
        window = window_registry[window_id]
        window.show()
        return "SUCCESS: Window shown"
        
    except Exception as e:
        error_msg = f"ERROR: Failed to show window: {e}"
        logger.error(error_msg)
        return error_msg


def hide_window(window_id: str) -> str:
    """Hide a window"""
    try:
        if window_id not in window_registry:
            return f"ERROR: Window {window_id} not found"
        
        window = window_registry[window_id]
        window.hide()
        return "SUCCESS: Window hidden"
        
    except Exception as e:
        error_msg = f"ERROR: Failed to hide window: {e}"
        logger.error(error_msg)
        return error_msg


def close_window(window_id: str) -> str:
    """Close and destroy a window"""
    try:
        if window_id not in window_registry:
            return f"ERROR: Window {window_id} not found"
        
        window = window_registry[window_id]
        window.close()
        del window_registry[window_id]
        return "SUCCESS: Window closed"
        
    except Exception as e:
        error_msg = f"ERROR: Failed to close window: {e}"
        logger.error(error_msg)
        return error_msg


def list_windows() -> str:
    """List all open windows"""
    if not window_registry:
        return "No windows open"
    
    windows_info = []
    for window_id, window in window_registry.items():
        status = "created" if window.created else "not created"
        windows_info.append(f"  {window_id}: '{window.title}' ({status})")
    
    return f"Open windows ({len(window_registry)}):\n" + "\n".join(windows_info)


# For backwards compatibility - simple functions that can be called from launcher
class EPLuaGUI:
    """Backwards compatibility class for the launcher"""
    
    def __init__(self):
        pass
    
    def run(self):
        """Run the GUI - this is now a no-op since windows are created on demand"""
        if not TKINTER_AVAILABLE:
            print("❌ tkinter is not available")
            return
        
        print("✅ GUI module loaded - windows can be created from Lua")
        print("📝 Use create_window(), show_window(), etc. from Lua scripts")


def show_gui():
    """Show GUI - backwards compatibility function"""
    if not TKINTER_AVAILABLE:
        return "ERROR: tkinter is not available"
    
    try:
        _ensure_main_thread()
        return "SUCCESS: GUI ready - use window functions from Lua"
    except Exception as e:
        return f"ERROR: {e}"
