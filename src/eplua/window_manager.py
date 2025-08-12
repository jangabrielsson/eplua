"""
Window Manager for EPLua - External Browser Window Management

This module provides functionality to create and manage external web browser windows
for the EPLua UI system. It replaces the previous Tkinter-based UI with browser windows
that can display web content from URLs.
"""

import subprocess
import platform
import logging
import threading
import time
import os
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class BrowserWindow:
    """Represents a single browser window instance."""
    
    def __init__(self, window_id: str, url: str, width: int = 800, height: int = 600,
                 x: int = 100, y: int = 100):
        self.window_id = window_id
        self.url = url
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.process = None
        self.is_open = False
        
    def __str__(self):
        return f"BrowserWindow({self.window_id}, {self.url}, {self.width}x{self.height})"


class WindowManager:
    """Manages external browser windows for EPLua UI."""
    
    def __init__(self):
        self.windows: Dict[str, BrowserWindow] = {}
        self.system = platform.system().lower()
        logger.info(f"WindowManager initialized for {self.system}")

    def create_window(self, window_id: str, url: str, width: int = 800, height: int = 600,
                      x: int = 100, y: int = 100) -> bool:
        """
        Create a new browser window.
        
        Args:
            window_id: Unique identifier for the window
            url: URL to display in the window
            width: Window width in pixels
            height: Window height in pixels
            x: Window x position
            y: Window y position
            
        Returns:
            True if window was created successfully, False otherwise
        """
        if window_id in self.windows:
            logger.warning(f"Window {window_id} already exists, closing existing window")
            self.close_window(window_id)
            
        window = BrowserWindow(window_id, url, width, height, x, y)
        
        try:
            if self._launch_browser(window):
                self.windows[window_id] = window
                window.is_open = True
                logger.info(f"Created window {window_id}: {url}")
                return True
            else:
                logger.error(f"Failed to launch browser for window {window_id}")
                return False
        except Exception as e:
            logger.error(f"Error creating window {window_id}: {e}")
            return False
            
    def close_window(self, window_id: str) -> bool:
        """
        Close a browser window.
        
        Args:
            window_id: ID of the window to close
            
        Returns:
            True if window was closed successfully, False otherwise
        """
        if window_id not in self.windows:
            logger.warning(f"Window {window_id} not found")
            return False
            
        window = self.windows[window_id]
        
        try:
            if window.process and window.process.poll() is None:
                window.process.terminate()
                # Give it a moment to terminate gracefully
                time.sleep(0.5)
                if window.process.poll() is None:
                    window.process.kill()
                    
            window.is_open = False
            del self.windows[window_id]
            logger.info(f"Closed window {window_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing window {window_id}: {e}")
            return False
            
    def set_window_url(self, window_id: str, url: str) -> bool:
        """
        Update the URL of an existing window.
        
        Args:
            window_id: ID of the window to update
            url: New URL to display
            
        Returns:
            True if URL was updated successfully, False otherwise
        """
        if window_id not in self.windows:
            logger.warning(f"Window {window_id} not found")
            return False
            
        window = self.windows[window_id]
        old_url = window.url
        window.url = url
        
        # For now, we'll close and reopen the window with the new URL
        # In the future, we could use browser automation to navigate
        try:
            width, height = window.width, window.height
            x, y = window.x, window.y
            
            self.close_window(window_id)
            success = self.create_window(window_id, url, width, height, x, y)
            
            if success:
                logger.info(f"Updated window {window_id} URL: {old_url} -> {url}")
            else:
                logger.error(f"Failed to update window {window_id} URL")
                
            return success
            
        except Exception as e:
            logger.error(f"Error updating window {window_id} URL: {e}")
            return False
            
    def get_window_info(self, window_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a window.
        
        Args:
            window_id: ID of the window
            
        Returns:
            Dictionary with window information, or None if window not found
        """
        if window_id not in self.windows:
            return None
            
        window = self.windows[window_id]
        return {
            "id": window.window_id,
            "url": window.url,
            "width": window.width,
            "height": window.height,
            "x": window.x,
            "y": window.y,
            "is_open": window.is_open
        }
        
    def list_windows(self) -> Dict[str, Dict[str, Any]]:
        """
        List all managed windows.
        
        Returns:
            Dictionary mapping window IDs to window information
        """
        return {wid: self.get_window_info(wid) for wid in self.windows.keys()}
        
    def close_all_windows(self):
        """Close all managed windows."""
        window_ids = list(self.windows.keys())
        for window_id in window_ids:
            self.close_window(window_id)
        logger.info("All windows closed")
        
    def _launch_browser(self, window: BrowserWindow) -> bool:
        """
        Launch a browser window with the specified parameters.
        
        Args:
            window: BrowserWindow instance to launch
            
        Returns:
            True if browser was launched successfully, False otherwise
        """
        try:
            if self.system == "darwin":  # macOS
                return self._launch_browser_macos(window)
            elif self.system == "linux":
                return self._launch_browser_linux(window)
            elif self.system == "windows":
                return self._launch_browser_windows(window)
            else:
                logger.error(f"Unsupported operating system: {self.system}")
                return False
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            return False
            
    def _launch_browser_macos(self, window: BrowserWindow) -> bool:
        """Launch browser on macOS using AppleScript for positioning."""
        try:
            # First, open the URL in the default browser
            subprocess.run(["open", window.url], check=True)
            
            # Wait a moment for the browser to start
            time.sleep(1)
            
            # Use AppleScript to position and resize the window
            # Note: This works with Safari and Chrome, may need adjustment for other browsers
            applescript = f'''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                if frontApp contains "Safari" or frontApp contains "Chrome" or frontApp contains "Firefox" then
                    tell process frontApp
                        set frontWindow to front window
                        set position of frontWindow to {{{window.x}, {window.y}}}
                        set size of frontWindow to {{{window.width}, {window.height}}}
                    end tell
                end if
            end tell
            '''
            
            # Run AppleScript in a separate thread to avoid blocking
            def run_applescript():
                try:
                    subprocess.run(["osascript", "-e", applescript], 
                                 capture_output=True, text=True, check=False)
                except Exception as e:
                    logger.warning(f"AppleScript positioning failed: {e}")
                    
            threading.Thread(target=run_applescript, daemon=True).start()
            
            logger.info(f"Launched browser on macOS for {window.url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser on macOS: {e}")
            return False
            
    def _launch_browser_linux(self, window: BrowserWindow) -> bool:
        """Launch browser on Linux."""
        try:
            # Try to launch with Chrome/Chromium with specific window size and position
            chrome_commands = [
                "google-chrome",
                "chromium-browser", 
                "chromium",
                "chrome"
            ]
            
            chrome_args = [
                f"--window-size={window.width},{window.height}",
                f"--window-position={window.x},{window.y}",
                "--new-window",
                window.url
            ]
            
            for cmd in chrome_commands:
                try:
                    window.process = subprocess.Popen([cmd] + chrome_args,
                                                    stdout=subprocess.DEVNULL,
                                                    stderr=subprocess.DEVNULL)
                    logger.info(f"Launched {cmd} on Linux for {window.url}")
                    return True
                except FileNotFoundError:
                    continue
                    
            # Fallback to default browser
            window.process = subprocess.Popen(["xdg-open", window.url],
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
            logger.info(f"Launched default browser on Linux for {window.url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser on Linux: {e}")
            return False
            
    def _launch_browser_windows(self, window: BrowserWindow) -> bool:
        """Launch browser on Windows."""
        try:
            # Try Chrome first with positioning
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome\Application\chrome.exe"
            ]
            
            chrome_args = [
                f"--window-size={window.width},{window.height}",
                f"--window-position={window.x},{window.y}",
                "--new-window",
                window.url
            ]
            
            for chrome_path in chrome_paths:
                try:
                    expanded_path = os.path.expandvars(chrome_path)
                    if os.path.exists(expanded_path):
                        window.process = subprocess.Popen([expanded_path] + chrome_args,
                                                        stdout=subprocess.DEVNULL,
                                                        stderr=subprocess.DEVNULL)
                        logger.info(f"Launched Chrome on Windows for {window.url}")
                        return True
                except Exception:
                    continue
                    
            # Fallback to default browser
            import webbrowser
            webbrowser.open(window.url)
            logger.info(f"Launched default browser on Windows for {window.url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch browser on Windows: {e}")
            return False


# Global window manager instance
_window_manager = None

def get_window_manager() -> WindowManager:
    """Get the global window manager instance."""
    global _window_manager
    if _window_manager is None:
        _window_manager = WindowManager()
    return _window_manager


# _PY functions for Lua integration
def create_window(window_id: str, url: str, width: int = 800, height: int = 600,
                 x: int = 100, y: int = 100) -> bool:
    """
    Create a new browser window (Lua callable).
    
    Args:
        window_id: Unique identifier for the window
        url: URL to display in the window
        width: Window width in pixels (default: 800)
        height: Window height in pixels (default: 600)
        x: Window x position (default: 100)
        y: Window y position (default: 100)
        
    Returns:
        True if window was created successfully, False otherwise
    """
    return get_window_manager().create_window(window_id, url, width, height, x, y)


def close_window(window_id: str) -> bool:
    """
    Close a browser window (Lua callable).
    
    Args:
        window_id: ID of the window to close
        
    Returns:
        True if window was closed successfully, False otherwise
    """
    return get_window_manager().close_window(window_id)


def set_window_url(window_id: str, url: str) -> bool:
    """
    Update the URL of an existing window (Lua callable).
    
    Args:
        window_id: ID of the window to update
        url: New URL to display
        
    Returns:
        True if URL was updated successfully, False otherwise
    """
    return get_window_manager().set_window_url(window_id, url)


def get_window_info(window_id: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a window (Lua callable).
    
    Args:
        window_id: ID of the window
        
    Returns:
        Dictionary with window information, or None if window not found
    """
    return get_window_manager().get_window_info(window_id)


def list_windows() -> Dict[str, Dict[str, Any]]:
    """
    List all managed windows (Lua callable).
    
    Returns:
        Dictionary mapping window IDs to window information
    """
    return get_window_manager().list_windows()


def close_all_windows():
    """Close all managed windows (Lua callable)."""
    get_window_manager().close_all_windows()
