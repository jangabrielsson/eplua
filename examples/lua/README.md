# End-User Examples

These examples demonstrate EPLua's **user-friendly APIs** for end users writing Lua scripts.

## Available APIs

### Timer Functions
- `setTimeout(callback, milliseconds)` - Run function after delay
- `setInterval(callback, milliseconds)` - Run function repeatedly  
- `clearTimeout(id)` - Cancel a timeout
- `clearInterval(id)` - Cancel an interval

### Network Modules  
- `net.HTTPClient()` - HTTP/HTTPS requests
- `net.WebSocketClient()` - WebSocket connections
- `net.MQTTClient()` - MQTT messaging
- `net.TCPSocket()` - TCP connections
- `net.UDPSocket()` - UDP datagrams

## Examples

### `getting_started.lua`
**Perfect for beginners!** Step-by-step introduction to EPLua's main features:
- Basic timers and intervals
- HTTP requests
- WebSocket communication
- MQTT messaging
- Low-level networking

### `basic_example.lua`
Comprehensive overview showing:
- Timer usage patterns
- HTTP client with success/error callbacks
- WebSocket event handling
- Network client lifecycle

### `network_demo.lua`
In-depth networking examples:
- HTTP GET/POST requests with custom headers
- TCP socket connections
- UDP socket messaging
- MQTT publish/subscribe
- Error handling patterns

### `timer_examples.lua`
Complete timer functionality:
- Basic setTimeout/setInterval usage
- Clearing timers
- Timer chains
- Self-clearing intervals
- Performance testing

## Usage

```bash
# Run any example
python -m src.eplua.cli examples/lua/getting_started.lua
python -m src.eplua.cli examples/lua/network_demo.lua
```

## API Documentation

All user APIs are designed to be:
- **Simple** - Easy to learn and use
- **Consistent** - Similar patterns across all modules
- **Safe** - Automatic error handling
- **Async** - Non-blocking operations with callbacks

These APIs abstract away the internal `_PY.*` functions and provide a clean, Fibaro HC3-compatible interface.
