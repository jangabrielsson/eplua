<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# EPLua Project Instructions

This is a Python project that integrates Lua script execution with async timer functionality.

## Key Components:
- **LuaEngine**: Core class for managing Lua script execution
- **AsyncTimerManager**: Handles Python async timers that can be controlled from Lua
- **Lua Bindings**: Bridge between Lua and Python functionality
- **Network Modules**: Modular network functionality (http.py, tcp.py, udp.py, websocket.py, mqtt.py)

## Architecture Guidelines:
- Use async/await for all timer operations
- Ensure proper cleanup of timers and resources
- Maintain thread safety between Lua and Python contexts
- Follow Python asyncio best practices
- Use Lupa for Lua-Python interoperability
- Keep the number of _PY functions minimal and well-documented
- End-user convenience functions should be done in lua
- Use decorators to expose Python functions to Lua

## Engine and Callback System:

### Core Engine Architecture:
- **LuaEngine**: Single global instance manages Lua runtime and Python-Lua bridge
- **Global Engine Access**: Use `get_global_engine()` to access engine from any module
- **Lua Environment**: Exposes `_PY` table containing all Python functions exported via decorators

### Callback Management:
- **Callback Registry**: Engine maintains a registry of all active callbacks (timers, HTTP, threads)
- **Unique Callback IDs**: Each callback gets a UUID for tracking and cleanup
- **Callback Tracking**: Lua-side counting ensures CLI stays alive while callbacks are pending
- **Automatic Cleanup**: Callbacks are automatically removed from registry when completed

### Asyncio Integration:
- **Main Event Loop**: Engine runs in primary asyncio event loop
- **Timer Operations**: `setTimeout`/`setInterval` use asyncio tasks for precise timing
- **HTTP Requests**: Network calls use aiohttp for non-blocking async operations
- **Keep-Alive Logic**: CLI monitors both pending callbacks and running intervals

### Thread Safety:
- **Cross-Thread Communication**: Thread-safe queue for posting results from Python threads to Lua
- **Queue Processor**: Background asyncio task processes thread callbacks in main loop
- **Thread Integration**: Use `post_callback_from_thread()` to safely deliver results from any thread
- **Callback Delivery**: All callbacks (timers, HTTP, threads) use the same unified delivery mechanism

### Extension Pattern:
- **Decorator System**: Use `@export_to_lua` to automatically expose Python functions to Lua
- **Table Conversion**: `python_to_lua_table()` and `lua_to_python_table()` for data exchange
- **Module Organization**: Each network protocol (HTTP, TCP, UDP, WebSocket, MQTT) in separate modules

## Code Style:
- Follow PEP 8 conventions
- Use type hints where applicable
- Write comprehensive docstrings
- Include error handling for Lua script errors
- Use logging for debugging and monitoring
- Always use the global engine instance for consistency
- Register all async operations in the callback system
- Use the decorator pattern for extending Lua functionality
- dev/ is the testing directory (create test scripts here to avoid polluting top level)
