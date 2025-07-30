"""
EPLua - Python Lua Engine with Async Timer Support
"""

from .engine import LuaEngine
from .timers import AsyncTimerManager
from .lua_bindings import export_to_lua, python_to_lua_table
# Import remaining core modules
from . import threading_support
from . import web_server

__version__ = "0.1.0"
__all__ = ["LuaEngine", "AsyncTimerManager", "export_to_lua", "python_to_lua_table"]
