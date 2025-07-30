# EPLua - Python Lua Engine with Async Timers

A Python project that uses Lupa to execute Lua scripts with integrated async timer functionality. The core engine allows Lua scripts to create and manage Python-based async timers.

## Features

- Execute Lua scripts from Python using Lupa
- Async timer system controllable from Lua
- Core engine class for managing script execution
- Event-driven architecture

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

```python
import asyncio
from eplua import LuaEngine

async def main():
    async with LuaEngine() as engine:
        # Create timers from Lua
        await engine.run_script("""
        print("Creating timers...")
        
        -- Create a timeout timer (fires once after delay)
        local timeout_id = timer.setTimeout(1000)  -- 1 second
        
        -- Create an interval timer (fires repeatedly)
        local interval_id = timer.setInterval(500)  -- every 500ms
        
        print("Timers created! Count: " .. timer.getTimerCount())
        """)
        
        # Let timers run
        await asyncio.sleep(3)
        
        print("Demo completed!")

asyncio.run(main())
```

## Project Structure

```
src/eplua/
├── __init__.py
├── engine.py          # Core Lua engine
├── timers.py          # Async timer system
└── lua_bindings.py    # Lua-Python bindings

tests/
├── test_engine.py
├── test_timers.py
└── scripts/           # Test Lua scripts

examples/
└── basic_usage.py
```

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black src tests examples
```

Lint:
```bash
flake8 src tests examples
```
