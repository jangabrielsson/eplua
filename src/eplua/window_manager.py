"""
Window Manager for EPLua - External Browser Window Management

This module provides functionality to create and manage external web browser windows
for the EPLua UI system. It replaces the previous Tkinter-based UI with browser windows
that can display web content from URLs.
"""

import platform
import logging
import time
import os
import json
import webbrowser
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

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
        self.created_in_session = False  # Track if window was created in this session
        self.created_at = datetime.now().isoformat()  # Track creation time
        
    def __str__(self):
        return f"BrowserWindow({self.window_id}, {self.url}, {self.width}x{self.height})"


class WindowManager:
    """Manages external browser windows for EPLua UI."""
    
    def __init__(self):
        self.windows: Dict[str, BrowserWindow] = {}
        self.system = platform.system().lower()
        
        # Use ~/.plua/ directory for state file
        plua_dir = os.path.expanduser("~/.plua")
        os.makedirs(plua_dir, exist_ok=True)
        self.state_file = os.path.join(plua_dir, "windows.json")
        
        self._load_window_state()
        logger.info(f"WindowManager initialized for {self.system}, state file: {self.state_file}")

    def _load_window_state(self):
        """Load window state from persistent storage and clean up stale entries"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                # Clean up entries older than 10 minutes
                cutoff_time = datetime.now() - timedelta(minutes=10)
                valid_windows = {}
                stale_count = 0
                
                for window_id, window_data in state.items():
                    # Check if window has created_at timestamp
                    if 'created_at' in window_data:
                        try:
                            created_at = datetime.fromisoformat(window_data['created_at'])
                            if created_at > cutoff_time:
                                # Window is recent enough to keep
                                window = BrowserWindow(
                                    window_id=window_data['window_id'],
                                    url=window_data['url'],
                                    width=window_data['width'],
                                    height=window_data['height'],
                                    x=window_data['x'],
                                    y=window_data['y']
                                )
                                window.is_open = True
                                window.created_in_session = False
                                window.created_at = window_data['created_at']
                                valid_windows[window_id] = window
                            else:
                                stale_count += 1
                        except (ValueError, KeyError):
                            # Invalid timestamp, treat as stale
                            stale_count += 1
                    else:
                        # Old entry without timestamp, treat as stale
                        stale_count += 1
                
                self.windows = valid_windows
                
                if stale_count > 0:
                    logger.debug(f"Cleaned up {stale_count} stale window entries (older than 10 minutes)")
                    # Save the cleaned state immediately
                    self._save_window_state()
                    
                logger.debug(f"Loaded {len(self.windows)} valid window states from {self.state_file}")
        except Exception as e:
            logger.debug(f"Could not load window state: {e}")

    def _save_window_state(self):
        """Save window state to persistent storage"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            
            # Only save windows that were created in this session and are still open
            state_to_save = {}
            for window_id, window in self.windows.items():
                if window.is_open and getattr(window, 'created_in_session', True):
                    state_to_save[window_id] = {
                        'window_id': window.window_id,
                        'url': window.url,
                        'width': window.width,
                        'height': window.height,
                        'x': window.x,
                        'y': window.y,
                        'created_at': getattr(window, 'created_at', datetime.now().isoformat())
                    }
            
            with open(self.state_file, 'w') as f:
                json.dump(state_to_save, f, indent=2)
                
            logger.debug(f"Saved {len(state_to_save)} window states to {self.state_file}")
        except Exception as e:
            logger.debug(f"Could not save window state: {e}")

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
        logger.debug(f"Creating window {window_id} for URL: {url}")
        
        # Check if we already have a window with the same URL
        existing_window = self._find_window_by_url(url)
        if existing_window:
            # Verify the window is still actually open by trying to check if the browser process exists
            if self._is_window_still_open(existing_window):
                logger.info(f"Reusing existing window {existing_window.window_id} for URL: {url}")
                # Update the window_id mapping to point to the existing window
                if window_id != existing_window.window_id:
                    self.windows[window_id] = existing_window
                self._save_window_state()
                return True
            else:
                logger.info(f"Existing window {existing_window.window_id} no longer open, creating new one")
                # Remove the stale window reference
                self._remove_window_reference(existing_window)
            
        # Only close existing window if we're not reusing by URL
        if window_id in self.windows:
            logger.warning(f"Window {window_id} already exists, closing existing window")
            self.close_window(window_id)
            
        window = BrowserWindow(window_id, url, width, height, x, y)
        window.created_in_session = True  # Mark as created in current session
        
        try:
            if self._launch_browser(window):
                self.windows[window_id] = window
                window.is_open = True
                self._save_window_state()
                logger.info(f"Created new window {window_id}: {url}")
                return True
            else:
                logger.error(f"Failed to launch browser for window {window_id}")
                return False
        except Exception as e:
            logger.error(f"Error creating window {window_id}: {e}")
            return False
    
    def _find_window_by_url(self, url: str) -> Optional[BrowserWindow]:
        """
        Find an existing window that displays the same URL.
        
        Args:
            url: URL to search for
            
        Returns:
            BrowserWindow instance if found, None otherwise
        """
        for window in self.windows.values():
            if window.url == url and window.is_open:
                # Only reuse windows created in current session, or if we can verify they're still open
                if getattr(window, 'created_in_session', False) or self._is_window_still_open(window):
                    logger.debug(f"Reusing existing window for URL: {url}")
                    return window
        return None

    def _is_window_still_open(self, window: BrowserWindow) -> bool:
        """
        Check if a window is still actually open.
        Since we can't reliably track browser windows across processes,
        we'll assume windows from previous runs are no longer valid.
        
        Args:
            window: BrowserWindow to check
            
        Returns:
            False - always assume windows from previous runs are closed
        """
        # For windows created in this session, we could potentially track them,
        # but for simplicity and reliability, we'll always assume windows from
        # persistent state are no longer valid and create new ones.
        # This ensures users always get a visible window.
        logger.debug(f"Assuming window {window.window_id} is no longer open (safer approach)")
        return False

    def _remove_window_reference(self, window: BrowserWindow):
        """Remove all references to a window that's no longer open"""
        windows_to_remove = []
        for window_id, win in self.windows.items():
            if win == window:
                windows_to_remove.append(window_id)
        
        for window_id in windows_to_remove:
            del self.windows[window_id]
        
        self._save_window_state()
            
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
            self._save_window_state()
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
        Launch a browser window using Python's webbrowser module.
        
        Args:
            window: BrowserWindow instance to launch
            
        Returns:
            True if browser was launched successfully, False otherwise
        """
        try:
            logger.debug(f"Launching browser for URL: {window.url}")
            
            # Use webbrowser module with new=1 to force a new window
            # This is cross-platform and much simpler than platform-specific approaches
            success = webbrowser.open(window.url, new=1, autoraise=True)
            
            if success:
                logger.info(f"Successfully launched browser window for {window.url}")
                return True
            else:
                logger.error(f"Failed to launch browser for {window.url}")
                return False
                
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
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
