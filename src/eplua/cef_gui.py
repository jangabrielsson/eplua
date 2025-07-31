"""
EPLua CEF GUI Module with Automatic Cleanup

This module provides GUI capabilities using tkinter + CEF (Chromium Embedded Framework)
for full HTML/CSS/JavaScript support with automatic cleanup when process dies.
"""

import logging
import sys
import threading
import tkinter as tk
import uuid
import time
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to import psutil for robust parent monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, using basic parent monitoring")

# Global state
cef_window_registry: Dict[str, 'CEFWindow'] = {}
cef_initialized = False
parent_pid = os.getppid()  # Store parent process ID
monitor_thread = None

try:
    from cefpython3 import cefpython as cef
    CEF_AVAILABLE = True
    logger.info("cefpython3 is available")
except ImportError:
    CEF_AVAILABLE = False
    logger.warning("cefpython3 is not available")


def start_parent_monitor():
    """Start monitoring parent process for automatic cleanup"""
    global monitor_thread, parent_pid
    
    if monitor_thread and monitor_thread.is_alive():
        return
    
    def monitor_parent():
        """Monitor parent process and cleanup if it dies"""
        while True:
            try:
                # Check if parent process is still alive
                if PSUTIL_AVAILABLE:
                    # Use psutil for robust checking
                    if not psutil.pid_exists(parent_pid):
                        logger.warning("Parent process died, cleaning up CEF windows...")
                        cleanup_cef()
                        break
                else:
                    # Fallback: try to send signal 0 to parent (doesn't actually send signal)
                    try:
                        os.kill(parent_pid, 0)  # This will raise OSError if process doesn't exist
                    except OSError:
                        logger.warning("Parent process died, cleaning up CEF windows...")
                        cleanup_cef()
                        break
                
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error monitoring parent process: {e}")
                break
    
    monitor_thread = threading.Thread(target=monitor_parent, daemon=True)
    monitor_thread.start()
    logger.info(f"Started monitoring parent process {parent_pid}")


def initialize_cef():
    """Initialize CEF - should be called once"""
    global cef_initialized
    
    if not CEF_AVAILABLE or cef_initialized:
        return
    
    try:
        # CEF settings
        settings = {
            "auto_zooming": "system_dpi",
            "background_color": 0xffffffff,  # White background
            "context_menu": {
                "enabled": False,  # Disable right-click menu
            },
        }
        
        # Initialize CEF
        cef.Initialize(settings)
        cef_initialized = True
        logger.info("CEF initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize CEF: {e}")
        raise


def shutdown_cef():
    """Shutdown CEF properly"""
    global cef_initialized
    
    if CEF_AVAILABLE and cef_initialized:
        try:
            cef.Shutdown()
            cef_initialized = False
            logger.info("CEF shutdown successfully")
        except Exception as e:
            logger.warning(f"CEF shutdown warning: {e}")


class CEFWindow:
    """A tkinter window with embedded CEF browser for full HTML/CSS/JS support"""
    
    def __init__(self, window_id: str, title: str, width: int = 800, height: int = 600):
        self.window_id = window_id
        self.title = title
        self.width = width
        self.height = height
        self.tk_window = None
        self.browser = None
        self.created = False
        self.html_content = "<h1>Loading...</h1>"
    
    def create(self):
        """Create the tkinter window with embedded CEF browser"""
        global cef_window_registry
        
        if not CEF_AVAILABLE:
            raise RuntimeError("cefpython3 is not available")
        
        try:
            # Initialize CEF if not already done
            initialize_cef()
            
            # Create tkinter window
            self.tk_window = tk.Toplevel() if tk._default_root else tk.Tk()
            self.tk_window.title(self.title)
            self.tk_window.geometry(f"{self.width}x{self.height}")
            
            # Create CEF browser
            window_info = cef.WindowInfo()
            window_info.SetAsChild(self.tk_window.winfo_id(), [0, 0, self.width, self.height])
            
            browser_settings = {
                "background_color": 0xffffffff,
            }
            
            self.browser = cef.CreateBrowserSync(
                window_info,
                url=cef.GetDataUrl(self.html_content),
                settings=browser_settings
            )
            
            # Hide window initially
            self.tk_window.withdraw()
            self.created = True
            
            cef_window_registry[self.window_id] = self
            logger.info(f"CEF window {self.window_id} created successfully")
            
            # Set up message loop
            self._setup_message_loop()
            
        except Exception as e:
            logger.error(f"Failed to create CEF window {self.window_id}: {e}")
            raise
    
    def _setup_message_loop(self):
        """Set up CEF message loop integration with tkinter"""
        def message_loop():
            cef.MessageLoopWork()
            if self.created and self.tk_window:
                self.tk_window.after(10, message_loop)
        
        if self.tk_window:
            self.tk_window.after(10, message_loop)
    
    def set_html(self, html_content: str):
        """Set HTML content in the browser"""
        self.html_content = html_content
        
        if not self.created or not self.browser:
            return
        
        try:
            # Load HTML content as data URL
            data_url = cef.GetDataUrl(html_content)
            self.browser.LoadUrl(data_url)
            logger.info(f"HTML content set for CEF window {self.window_id}")
        except Exception as e:
            logger.error(f"Failed to set HTML content for CEF window {self.window_id}: {e}")
            raise
    
    def set_url(self, url: str):
        """Load a URL in the browser"""
        if not self.created or not self.browser:
            raise ValueError("Window not created yet")
        
        try:
            self.browser.LoadUrl(url)
            logger.info(f"URL {url} loaded in CEF window {self.window_id}")
        except Exception as e:
            logger.error(f"Failed to load URL {url} for CEF window {self.window_id}: {e}")
            raise
    
    def show(self):
        """Show the window"""
        if not self.created:
            self.create()
        
        if self.tk_window:
            self.tk_window.deiconify()
            self.tk_window.lift()
            logger.info(f"CEF window {self.window_id} shown")
    
    def hide(self):
        """Hide the window"""
        if self.tk_window:
            self.tk_window.withdraw()
            logger.info(f"CEF window {self.window_id} hidden")
    
    def close(self):
        """Close the window"""
        global cef_window_registry
        
        try:
            # Close browser first
            if self.browser:
                try:
                    self.browser.CloseBrowser(True)
                except Exception as e:
                    logger.warning(f"Error closing CEF browser: {e}")
                self.browser = None
            
            # Destroy tkinter window
            if self.tk_window:
                try:
                    self.tk_window.quit()  # Stop mainloop
                    self.tk_window.destroy()
                except Exception as e:
                    logger.warning(f"Error destroying tkinter window: {e}")
                self.tk_window = None
            
            self.created = False
            
            # Remove from registry
            if self.window_id in cef_window_registry:
                del cef_window_registry[self.window_id]
            
            logger.info(f"CEF window {self.window_id} closed")
            
        except Exception as e:
            logger.error(f"Error closing CEF window {self.window_id}: {e}")
    
    def is_closed(self):
        """Check if the window is closed"""
        return not self.created or not self.tk_window


def create_cef_window(title: str, width: int = 800, height: int = 600) -> CEFWindow:
    """Create a new CEF window"""
    # Start parent process monitor if not already running
    start_parent_monitor()
    
    window_id = str(uuid.uuid4())
    window = CEFWindow(window_id, title, width, height)
    cef_window_registry[window_id] = window
    logger.info(f"CEF window {window_id} created")
    return window


def list_cef_windows() -> str:
    """List all CEF windows"""
    if not cef_window_registry:
        return "No CEF windows open"
    
    result = f"Open CEF windows ({len(cef_window_registry)}):\n"
    for window_id, window in cef_window_registry.items():
        status = "created" if window.created else "not created"
        result += f"  {window_id}: '{window.title}' ({status})\n"
    
    return result.rstrip()


def is_cef_available() -> bool:
    """Check if CEF is available"""
    return CEF_AVAILABLE


# Set up automatic cleanup
import atexit
import signal
import os


def cleanup_cef():
    """Enhanced cleanup function that closes all windows and shuts down CEF"""
    global cef_window_registry
    
    try:
        # Close all CEF windows first
        for window_id, window in list(cef_window_registry.items()):
            try:
                if window and window.browser:
                    logger.info(f"Closing CEF window {window_id}")
                    window.close()
            except Exception as e:
                logger.warning(f"Error closing CEF window {window_id}: {e}")
        
        # Clear the registry
        cef_window_registry.clear()
        
        # Shutdown CEF
        shutdown_cef()
        
    except Exception as e:
        logger.warning(f"Error during CEF cleanup: {e}")


def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {signum}, cleaning up CEF...")
    cleanup_cef()
    # Re-raise the signal to ensure proper termination
    if signum in (signal.SIGTERM, signal.SIGINT):
        os._exit(1)


# Register cleanup handlers
atexit.register(cleanup_cef)

# Handle signals (SIGINT = Ctrl+C, SIGTERM = normal termination)
try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
except (ValueError, OSError):
    # Some systems may not support all signals
    pass
