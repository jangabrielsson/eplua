"""
Lua-Python bindings for the EPLua engine.

This module provides the bridge between Lua scripts and Python functionality,
specifically for timer operations and other engine features.
"""

import logging
from typing import Any, Callable, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Registry for decorated functions
_exported_functions: Dict[str, Callable] = {}

# Global engine instance reference
_global_engine = None


def set_global_engine(engine):
    """Set the global engine instance."""
    global _global_engine
    _global_engine = engine


def get_global_engine():
    """Get the global engine instance."""
    return _global_engine


def python_to_lua_table(data: Any) -> Any:
    """
    Convert Python data structures to Lua tables using Lupa.
    
    Args:
        data: Python data (dict, list, or primitive)
        
    Returns:
        Lua table or primitive value
    """
    if _global_engine is None:
        raise RuntimeError("Global engine not set. Call set_global_engine() first.")
    
    if isinstance(data, (dict, list)):
        return _global_engine._lua.table_from(data, recursive=True)
    else:
        return data


def lua_to_python_table(lua_table: Any) -> Any:
    """
    Convert Lua tables to Python data structures.
    
    Args:
        lua_table: Lua table or primitive value
        
    Returns:
        Python dict, list, or primitive value
    """
    if _global_engine is None:
        raise RuntimeError("Global engine not set. Call set_global_engine() first.")
    
    # Check if it's a Lua table
    if hasattr(lua_table, '__class__') and 'lua' in str(lua_table.__class__).lower():
        try:
            # Convert to Python dict first
            temp_dict = {}
            for key, value in lua_table.items():
                # Recursively convert nested tables
                python_key = lua_to_python_table(key) if hasattr(key, '__class__') and 'lua' in str(key.__class__).lower() else key
                python_value = lua_to_python_table(value) if hasattr(value, '__class__') and 'lua' in str(value.__class__).lower() else value
                temp_dict[python_key] = python_value
            
            # Check if this looks like an array (consecutive integer keys starting from 1)
            if temp_dict and all(isinstance(k, (int, float)) and k > 0 for k in temp_dict.keys()):
                keys = sorted([int(k) for k in temp_dict.keys()])
                if keys == list(range(1, len(keys) + 1)):
                    # This is a Lua array, convert to Python list
                    return [temp_dict[k] for k in keys]
            
            return temp_dict
        except:
            # If conversion fails, return string representation
            return str(lua_table)
    else:
        return lua_table


def export_to_lua(name: Optional[str] = None):
    """
    Decorator to automatically export Python functions to the _PY table.
    
    Args:
        name: Optional name for the function in Lua. If None, uses the Python function name.
        
    Usage:
        @export_to_lua()
        def my_function(arg1, arg2):
            return arg1 + arg2
            
        @export_to_lua("custom_name")
        def another_function():
            print("Hello from Python!")
    """
    def decorator(func: Callable) -> Callable:
        lua_name = name if name is not None else func.__name__
        _exported_functions[lua_name] = func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_exported_functions() -> Dict[str, Callable]:
    """Get all functions marked for export to Lua."""
    return _exported_functions.copy()


class LuaBindings:
    """
    Provides Python functions that can be called from Lua scripts.
    
    This class creates the bridge between Lua and Python, exposing
    Python functionality to Lua scripts in a controlled manner.
    """
    
    def __init__(self, timer_manager, engine_instance):
        """
        Initialize Lua bindings.
        
        Args:
            timer_manager: Instance of AsyncTimerManager
            engine_instance: Instance of LuaEngine for callbacks
        """
        self.timer_manager = timer_manager
        self.engine = engine_instance
        self._setup_exported_functions()
        
    def _setup_exported_functions(self):
        """Setup exported functions with access to self."""
        # Timer functions
        @export_to_lua("set_timeout")
        def set_timeout(callback_id: int, delay_ms: int) -> str:
            """
            Set a timeout timer from Lua.
            
            Args:
                callback_id: ID of the Lua callback
                delay_ms: Delay in milliseconds
                
            Returns:
                Python timer ID
            """
            logger.debug(f"Setting timeout: {delay_ms}ms for callback {callback_id}")
            
            def python_callback():
                """Callback that notifies Lua when timer expires."""
                try:
                    # Call back into Lua
                    self.engine._lua.globals()["_PY"]["timerExpired"](callback_id)
                except Exception as e:
                    logger.error(f"Error in timeout callback {callback_id}: {e}")
                    
            return self.timer_manager.set_timeout(delay_ms, python_callback)
        
        @export_to_lua("clear_timeout")
        def clear_timeout(timer_id: str) -> bool:
            """
            Clear a timeout timer from Lua.
            
            Args:
                timer_id: Python timer ID to clear
                
            Returns:
                True if timer was cleared, False otherwise
            """
            logger.debug(f"Clearing timeout: {timer_id}")
            return self.timer_manager.clear_timer(timer_id)
        
        @export_to_lua("get_timer_count")
        def get_timer_count() -> int:
            """Get the number of active timers."""
            return self.timer_manager.get_timer_count()
        
        # Engine functions
        @export_to_lua("print")
        def lua_print(*args) -> None:
            """Enhanced print function for Lua scripts."""
            message = " ".join(str(arg) for arg in args)
            logger.info(f"Lua: {message}")
            print(f"[Lua] {message}", flush=True)
        
        @export_to_lua("log")
        def lua_log(level: str, message: str) -> None:
            """Logging function for Lua scripts."""
            level = level.upper()
            if level == "DEBUG":
                logger.debug(f"Lua: {message}")
            elif level == "INFO":
                logger.info(f"Lua: {message}")
            elif level == "WARNING":
                logger.warning(f"Lua: {message}")
            elif level == "ERROR":
                logger.error(f"Lua: {message}")
            else:
                logger.info(f"Lua [{level}]: {message}")
        
        @export_to_lua("get_time")
        def get_time() -> float:
            """Get current time in seconds."""
            import time
            return time.time()
        
        @export_to_lua("sleep")
        def sleep(seconds: float) -> None:
            """Sleep function (note: this is blocking, prefer timers for async)."""
            import time
            time.sleep(seconds)
            
        @export_to_lua("get_platform")
        def get_platform() -> Any:
            """Get the current platform information as Lua table."""
            import platform
            platform_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
            return python_to_lua_table(platform_info)
            
        @export_to_lua("get_system_info")
        def get_system_info() -> Any:
            """Get comprehensive system information as Lua table."""
            import platform
            import os
            import time
            
            info = {
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "python_version": platform.python_version()
                },
                "environment": {
                    "cwd": os.getcwd(),
                    "user": os.environ.get("USER", "unknown"),
                    "home": os.environ.get("HOME", "unknown"),
                    "path_separator": os.pathsep,
                    "line_separator": os.linesep
                },
                "runtime": {
                    "current_time": time.time(),
                    "pid": os.getpid()
                }
            }
            return python_to_lua_table(info)
            
        # Additional utility functions
        @export_to_lua("math_add")
        def math_add(a: float, b: float) -> float:
            """Add two numbers."""
            return a + b
            
        @export_to_lua("random_number")
        def random_number(min_val: float = 0, max_val: float = 1) -> float:
            """Generate a random number between min_val and max_val."""
            import random
            return random.uniform(min_val, max_val)
            
        @export_to_lua("threadRequestResult")
        def thread_request_result(request_id: str, result: Any) -> None:
            """
            Handle the result of a thread-safe script execution request.
            Called from Lua when a threadRequest completes.
            
            Args:
                request_id: The ID of the execution request
                result: The result data from the Lua execution
            """
            if self.engine:
                self.engine.handle_thread_request_result(request_id, result)
                
        @export_to_lua("parse_json")
        def parse_json(json_string: str) -> Any:
            """
            Parse a JSON string and return the corresponding Python/Lua data structure.
            
            Args:
                json_string: The JSON string to parse
                
            Returns:
                Tuple of (parsed_data, error). If successful, error is None.
                If failed, parsed_data is None and error contains the error message.
            """
            import json
            try:
                parsed_data = json.loads(json_string)
                # Convert Python data to Lua-compatible format
                lua_data = python_to_lua_table(parsed_data)
                return lua_data, None
            except json.JSONDecodeError as e:
                return None, str(e)
            except Exception as e:
                return None, f"Unexpected error: {str(e)}"
        
    def get_all_bindings(self) -> Dict[str, Any]:
        """
        Get all available bindings for Lua.
        
        Returns:
            Dictionary containing all exported functions
        """
        return get_exported_functions()
        
    def create_timer_bindings(self) -> Dict[str, Callable]:
        """
        Legacy method for timer bindings (deprecated, use get_all_bindings).
        """
        bindings = get_exported_functions()
        return {
            "set_timeout": bindings["set_timeout"],
            "clear_timeout": bindings["clear_timeout"], 
            "get_timer_count": bindings["get_timer_count"],
        }
        
    def create_engine_bindings(self) -> Dict[str, Callable]:
        """
        Legacy method for engine bindings (deprecated, use get_all_bindings).
        """
        bindings = get_exported_functions()
        return {
            "print": bindings["print"],
            "log": bindings["log"],
            "get_time": bindings["get_time"],
            "sleep": bindings["sleep"],
        }
