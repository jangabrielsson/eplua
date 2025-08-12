"""
Example module showing how to extend EPLua with custom functions using decorators.
"""

import os
import json
import logging
import importlib
import importlib.util
from typing import Dict, Any
from .lua_bindings import export_to_lua, python_to_lua_table, lua_to_python_table, get_exported_functions

# Import window manager for browser-based UI
try:
    from . import window_manager
    logging.info("Window manager loaded successfully")
except ImportError as e:
    logging.warning(f"Window manager not available: {e}")

# Import remaining extension modules (FFI libraries are now in pylib/)
# Use try/except to make imports safer
try:
    from . import web_server  # noqa: F401
except ImportError as e:
    logging.debug(f"web_server not available: {e}")

try:
    from . import sync_socket  # noqa: F401
except ImportError as e:
    logging.debug(f"sync_socket not available: {e}")

# Import pylib to register FFI libraries
try:
    import pylib  # noqa: F401
    logging.info("PyLib FFI libraries loaded successfully")
except ImportError as e:
    logging.warning(f"PyLib not available: {e}")


@export_to_lua("loadPythonModule")
def load_python_module(module_name: str) -> Dict[str, Any]:
    """
    Dynamically load a Python module and make its exported functions available to Lua.

    This function provides a FFI-like interface where Lua can load Python modules
    on demand. The module is imported (or reloaded) and all functions decorated
    with @export_to_lua are returned to Lua for immediate use.

    Search order:
    1. src/pylib/ directory (bundled FFI libraries)
    2. eplua package modules
    3. Standard Python modules

    Args:
        module_name: Name of the module to load (e.g., "filesystem", "http_client")

    Returns:
        Dict containing all exported functions from the module

    Example in Lua:
        local fs_funcs = _PY.loadPythonModule("filesystem")
        local attrs = fs_funcs.fs_attributes("/path/to/file")
    """
    try:
        logging.info(f"Loading Python module: {module_name}")

        # Store current exported functions count
        before_count = len(get_exported_functions())  # noqa: F841

        module = None
        full_module_name = None

        # Try different import strategies
        import_attempts = [
            # 1. Try pylib directory first (bundled FFI libraries)
            f"pylib.{module_name}",
            # 2. Try eplua package modules
            f"eplua.{module_name}",
            # 3. Try as direct module name
            module_name
        ]

        for attempt in import_attempts:
            try:
                # Check if module is already loaded
                if attempt in importlib.sys.modules:
                    logging.info(f"Reloading existing module: {attempt}")
                    module = importlib.reload(importlib.sys.modules[attempt])
                    full_module_name = attempt
                    break
                else:
                    logging.info(f"Trying to import: {attempt}")
                    module = importlib.import_module(attempt)
                    full_module_name = attempt
                    break
            except ImportError as e:
                logging.debug(f"Import attempt failed for {attempt}: {e}")
                continue

        if module is None:
            raise ImportError(f"Could not import module '{module_name}' from any location")

        logging.info(f"Successfully imported: {full_module_name}")

        # Get all exported functions after import
        all_exported = get_exported_functions()
        after_count = len(all_exported)  # noqa: F841

        # Find functions that were added by this module
        # (This is a simple heuristic - in practice, modules should prefix their functions)
        new_functions = {}
        if hasattr(module, '__name__'):
            # Look for functions that might belong to this module
            module_prefix = module.__name__.split('.')[-1]  # e.g., "filesystem" from "pylib.filesystem"
            for name, func in all_exported.items():
                # Include functions that start with module prefix or are likely from this module
                if (name.startswith(module_prefix.replace('_', '')) or
                    name.startswith(f"{module_prefix}_") or
                    hasattr(func, '__module__') and
                    module.__name__ in str(func.__module__)):
                    new_functions[name] = func

        # If we can't determine which functions are new, return all functions
        # This is safer and mimics the behavior of loading all available functions
        if not new_functions:
            new_functions = all_exported

        logging.info(f"Module {full_module_name} loaded successfully. "
                     f"Available functions: {list(new_functions.keys())}")

        return python_to_lua_table(new_functions)

    except ImportError as e:
        logging.error(f"Failed to import module {module_name}: {e}")
        return python_to_lua_table({"error": f"Module not found: {module_name}"})
    except Exception as e:
        logging.error(f"Error loading module {module_name}: {e}")
        return python_to_lua_table({"error": f"Failed to load module: {e}"})


@export_to_lua("read_file")
def read_file(filename: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


@export_to_lua("write_file")
def write_file(filename: str, content: str) -> bool:
    """Write content to a file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


@export_to_lua("list_directory")
def list_directory(path: str = ".") -> Any:
    """List directory contents (returns Lua table)."""
    try:
        entries = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            entries.append({
                "name": entry,
                "is_file": os.path.isfile(full_path),
                "is_directory": os.path.isdir(full_path),
                "size": os.path.getsize(full_path) if os.path.isfile(full_path) else 0
            })
        result = {"entries": entries, "count": len(entries)}
        return python_to_lua_table(result)
    except Exception as e:
        error_result = {"error": str(e), "entries": [], "count": 0}
        return python_to_lua_table(error_result)


@export_to_lua("parse_json")
def parse_json(json_string: str) -> Any:
    """Parse a JSON string and return as Lua table."""
    try:
        data = json.loads(json_string)
        return python_to_lua_table(data)
    except Exception as e:
        error_result = {"error": f"JSON parse error: {e}"}
        return python_to_lua_table(error_result)


@export_to_lua("to_json")
def to_json(lua_data: Any) -> str:
    """Convert data to flat JSON string."""
    try:
        # Convert Lua data to Python data structures first
        python_data = lua_to_python_table(lua_data)
        return json.dumps(python_data, ensure_ascii=False, separators=(",", ":"))
    except Exception as e:
        return f'{{"error": "JSON encode error: {e}"}}'


@export_to_lua("to_json_formatted")
def to_json_formatted(lua_data: Any) -> str:
    """Convert data to JSON string."""
    try:
        # Convert Lua data to Python data structures first
        python_data = lua_to_python_table(lua_data)
        return json.dumps(python_data, ensure_ascii=False, indent=2)
    except Exception as e:
        return f'{{"error": "JSON encode error: {e}"}}'


@export_to_lua("get_env")
def get_env(var_name: str, default: str = "") -> str:
    """Get environment variable."""
    return os.environ.get(var_name, default)


@export_to_lua("set_env")
def set_env(var_name: str, value: str) -> bool:
    """Set environment variable."""
    try:
        os.environ[var_name] = value
        return True
    except Exception:
        return False


# =============================================================================
# BROWSER WINDOW MANAGEMENT
# External browser-based UI system replacing old Tkinter GUI
# =============================================================================

@export_to_lua("get_html_engine")
def get_html_engine() -> str:
    """Get the name of the HTML rendering engine."""
    return "browser"


# Primary Browser Window Functions
@export_to_lua("create_browser_window")
def create_browser_window(window_id: str, url: str, width: int = 800, height: int = 600,
                          x: int = 100, y: int = 100) -> bool:
    """Create a new browser window with full control over position and size."""
    try:
        return window_manager.create_window(window_id, url, width, height, x, y)
    except Exception as e:
        logging.error(f"Error creating browser window: {e}")
        return False


@export_to_lua("close_browser_window")
def close_browser_window(window_id: str) -> bool:
    """Close a browser window."""
    try:
        return window_manager.close_window(window_id)
    except Exception as e:
        logging.error(f"Error closing browser window: {e}")
        return False


@export_to_lua("set_browser_window_url")
def set_browser_window_url(window_id: str, url: str) -> bool:
    """Set the URL of a browser window."""
    try:
        return window_manager.set_window_url(window_id, url)
    except Exception as e:
        logging.error(f"Error setting browser window URL: {e}")
        return False


@export_to_lua("get_browser_window_info")
def get_browser_window_info(window_id: str) -> Any:
    """Get information about a browser window."""
    try:
        info = window_manager.get_window_info(window_id)
        return python_to_lua_table(info) if info else None
    except Exception as e:
        logging.error(f"Error getting browser window info: {e}")
        return None


@export_to_lua("list_browser_windows")
def list_browser_windows() -> Any:
    """List all browser windows."""
    try:
        windows = window_manager.list_windows()
        return python_to_lua_table(windows)
    except Exception as e:
        logging.error(f"Error listing browser windows: {e}")
        return python_to_lua_table({"error": str(e)})


@export_to_lua("close_all_browser_windows")
def close_all_browser_windows() -> bool:
    """Close all browser windows."""
    try:
        window_manager.close_all_windows()
        return True
    except Exception as e:
        logging.error(f"Error closing all browser windows: {e}")
        return False





