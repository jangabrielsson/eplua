"""
Example module showing how to extend EPLua with custom functions using decorators.
"""

import os
import json
import logging
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any
from .lua_bindings import export_to_lua, python_to_lua_table, lua_to_python_table, get_exported_functions

# GUI modules removed - now using web UI approach
GUI_AVAILABLE = False
NATIVE_UI_AVAILABLE = False
logging.info("Native GUI disabled - using web UI approach")

# Import remaining extension modules (FFI libraries are now in pylib/)
# Use try/except to make imports safer
try:
    from . import web_server
except ImportError as e:
    logging.debug(f"web_server not available: {e}")

try:
    from . import sync_socket
except ImportError as e:
    logging.debug(f"sync_socket not available: {e}")

# Import pylib to register FFI libraries
try:
    import pylib
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
        before_count = len(get_exported_functions())

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
        after_count = len(all_exported)

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
        if hasattr(module, '__name__'):
            # Look for functions that might belong to this module
            module_prefix = module.__name__.split('.')[-1]  # e.g., "filesystem" from "eplua.filesystem"
            for name, func in all_exported.items():
                # Include functions that start with module prefix or are likely from this module
                if (name.startswith(module_prefix.replace('_', '')) or
                    name.startswith(f"{module_prefix}_") or
                    hasattr(func, '__module__') and module.__name__ in str(func.__module__)):
                    new_functions[name] = func

        # If we can't determine which functions are new, return all functions
        # This is safer and mimics the behavior of loading all available functions
        if not new_functions:
            new_functions = all_exported

        logging.info(f"Module {module_name} loaded successfully. "
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


# GUI Function Exports - Now using Web UI approach
# Provide stubs for compatibility until web UI is implemented
@export_to_lua("gui_available")
def gui_available() -> bool:
    """Check if GUI is available."""
    return False

@export_to_lua("html_rendering_available")
def html_rendering_available() -> bool:
    """Check if HTML rendering is available."""
    return False

@export_to_lua("get_html_engine")
def get_html_engine() -> str:
    """Get the name of the HTML rendering engine."""
    return "web"

@export_to_lua("create_window")
def create_window(title: str, width: int = 800, height: int = 600) -> str:
    """Create a new window."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("set_window_html")
def set_window_html(window_id: str, html_content: str) -> str:
    """Set HTML content for a window."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("set_window_url")
def set_window_url(window_id: str, url: str) -> str:
    """Load a URL in a window."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("show_window")
def show_window(window_id: str) -> str:
    """Show a window."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("hide_window")
def hide_window(window_id: str) -> str:
    """Hide a window."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("close_window")
def close_window(window_id: str) -> str:
    """Close and destroy a window."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("list_windows")
def list_windows() -> str:
    """List all open windows."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("show_gui")
def show_gui() -> str:
    """Show GUI - backwards compatibility function."""
    return "ERROR: Web UI not yet implemented"


# Native UI Functions - Now using Web UI approach
# Provide stubs for compatibility until web UI is implemented

@export_to_lua("createNativeWindow")
def create_native_window(title: str, width: int = 800, height: int = 600) -> Dict[str, Any]:
    """Create a new window."""
    return {"error": "Web UI not yet implemented"}

@export_to_lua("setNativeUI")
def set_native_ui(window_id: str, ui_description) -> bool:
    """Set UI description for a window."""
    return False

@export_to_lua("setNativeCallback")
def set_native_callback(window_id: str, element_id: str, callback_func) -> bool:
    """Set callback for a UI element."""
    return False

@export_to_lua("getNativeValue")
def get_native_value(window_id: str, element_id: str):
    """Get value of a UI element."""
    return None

@export_to_lua("setNativeValue")
def set_native_value(window_id: str, element_id: str, value) -> bool:
    """Set value of a UI element."""
    return False

@export_to_lua("showNativeWindow")
def show_native_window(window_id: str) -> bool:
    """Show a window."""
    return False

@export_to_lua("hideNativeWindow")
def hide_native_window(window_id: str) -> bool:
    """Hide a window."""
    return False

@export_to_lua("closeNativeWindow")
def close_native_window(window_id: str) -> bool:
    """Close a window."""
    return False

@export_to_lua("listNativeWindows")
def list_native_windows() -> str:
    """List all windows."""
    return "ERROR: Web UI not yet implemented"

@export_to_lua("isNativeUIAvailable")
def is_native_ui_available() -> bool:
    """Check if UI is available."""
    return False
