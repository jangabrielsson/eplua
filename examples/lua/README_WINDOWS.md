# Windows Module for EPLua

The Windows module provides a Lua-friendly interface for creating and managing GUI windows with HTML rendering capabilities.

## Quick Start

```lua
local windows = require('windows')

-- Create and show a window
local win = windows.createWindow("My App", 800, 600)
win:setHtml("<h1>Hello World!</h1>")
win:show()

-- Or use method chaining
windows.create("Demo")
    :html("<h1>Beautiful Interface!</h1>")
    :show()
```

## API Reference

### Module Functions

#### `windows.createWindow(title, width, height)`
Creates a new window and returns a Window object.
- `title` (string, optional): Window title (default: "EPLua Window")
- `width` (number, optional): Window width in pixels (default: 800)
- `height` (number, optional): Window height in pixels (default: 600)
- Returns: Window object

**Aliases:** `windows.create()`, `windows.new()`

#### `windows.isAvailable()`
Check if GUI functionality is available.
- Returns: boolean

#### `windows.htmlSupported()`
Check if HTML rendering is supported.
- Returns: boolean

#### `windows.getHtmlEngine()`
Get the name of the HTML rendering engine.
- Returns: string ("tkhtmlview", "tkinterweb", or "none")

#### `windows.getCapabilities()`
Get comprehensive capability information.
- Returns: table with `gui`, `html`, and `engine` fields

#### `windows.listWindows()`
Get information about all open windows.
- Returns: string with window details

#### `windows.demo()`
Create and show a demonstration window.
- Returns: Window object

#### `windows.help()`
Display help information.

### Window Object Methods

#### Object-Oriented Interface

```lua
local win = windows.createWindow("My Window")

-- Content methods
win:setHtml(html_content)    -- Set HTML content
win:setUrl(url)              -- Load a URL
win:html(content)            -- Alias for setHtml (chainable)
win:url(address)             -- Alias for setUrl (chainable)

-- Display methods
win:show()                   -- Show the window
win:hide()                   -- Hide the window
win:display()                -- Alias for show (chainable)
win:close()                  -- Close and destroy the window

-- Information methods
win:getId()                  -- Get window ID
win:isClosed()               -- Check if window is closed
```

#### Method Chaining

All content and display methods return the Window object, enabling fluent method chaining:

```lua
windows.createWindow("Chained Demo")
    :setHtml("<h1>Hello!</h1>")
    :show()

-- Or with aliases
windows.create("Fluent Demo")
    :html("<h1>Beautiful!</h1>")
    :display()
```

### Functional Interface

For those who prefer functional programming style:

```lua
local id = windows.createWindow("Functional Style"):getId()
windows.setWindowHtml(id, "<h1>Hello!</h1>")
windows.showWindow(id)
windows.closeWindow(id)
```

**Functional API:**
- `windows.setWindowHtml(windowId, html)`
- `windows.setWindowUrl(windowId, url)`
- `windows.showWindow(windowId)`
- `windows.hideWindow(windowId)`
- `windows.closeWindow(windowId)`

## Usage Examples

### Basic Window with HTML

```lua
local windows = require('windows')

local win = windows.createWindow("My App", 600, 400)
win:setHtml([[
    <html>
    <head><title>My App</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>Welcome to My App!</h1>
        <p>This is a beautiful HTML interface.</p>
    </body>
    </html>
]])
win:show()
```

### Loading Web Pages

```lua
local windows = require('windows')

if windows.htmlSupported() then
    local browser = windows.createWindow("Web Browser", 1000, 700)
    browser:setUrl("https://example.com")
    browser:show()
else
    print("HTML rendering not available")
end
```

### Advanced Styling

```lua
local windows = require('windows')

local app = windows.createWindow("Styled App", 800, 600)
app:setHtml([[
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .card {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { text-align: center; margin-top: 0; }
            .button {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
                margin: 5px;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 Modern Interface</h1>
            <p>Beautiful, modern design with CSS3 effects!</p>
            <button class="button">Button 1</button>
            <button class="button">Button 2</button>
        </div>
    </body>
    </html>
]])
app:show()
```

### Dashboard Example

```lua
local windows = require('windows')

local dashboard = windows.createWindow("Dashboard", 900, 700)
dashboard:html([[
    <!DOCTYPE html>
    <html>
    <head>
        <title>EPLua Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }
            .header {
                background: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            .widget {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .widget h3 {
                color: #2c3e50;
                margin-bottom: 15px;
            }
            .metric {
                font-size: 2em;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }
            .status {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                margin: 5px 0;
            }
            .status.online { background: #d5f4e6; color: #27ae60; }
            .status.offline { background: #fceaea; color: #e74c3c; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 EPLua System Dashboard</h1>
            <p>Real-time monitoring and control panel</p>
        </div>
        
        <div class="grid">
            <div class="widget">
                <h3>📊 System Status</h3>
                <div class="metric">99.9%</div>
                <p>Uptime</p>
                <span class="status online">● Online</span>
            </div>
            
            <div class="widget">
                <h3>🔗 Connections</h3>
                <div class="metric">1,247</div>
                <p>Active connections</p>
                <span class="status online">● Healthy</span>
            </div>
            
            <div class="widget">
                <h3>⚡ Performance</h3>
                <div class="metric">34ms</div>
                <p>Average response time</p>
                <span class="status online">● Excellent</span>
            </div>
            
            <div class="widget">
                <h3>💾 Storage</h3>
                <div class="metric">67%</div>
                <p>Disk usage</p>
                <span class="status online">● Normal</span>
            </div>
        </div>
    </body>
    </html>
]]):show()
```

## Error Handling

The windows module provides proper error handling:

```lua
local windows = require('windows')

-- Check availability before use
if not windows.isAvailable() then
    error("GUI not available")
end

-- Safe window operations
local win = windows.createWindow("Test")
local success, err = pcall(function()
    win:setHtml("<h1>Test</h1>")
    win:show()
end)

if not success then
    print("Error:", err)
end

-- Operations on closed windows will throw errors
win:close()
-- win:show() -- This would throw an error
```

## Platform Support

- **Windows**: Full support with tkinter and HTML rendering
- **macOS**: Full support (GUI operations must run on main thread)
- **Linux**: Full support with tkinter and HTML rendering

**HTML Rendering Engines:**
- **tkhtmlview**: Recommended, works with modern Tcl versions
- **tkinterweb**: Alternative, requires older Tcl versions
- **Fallback**: Text-only mode when HTML rendering unavailable

## Integration Examples

### With HTTP Module

```lua
local windows = require('windows')
local net = require('net')

local app = windows.createWindow("API Dashboard", 800, 600)

-- Load data from API and display
net.HTTPClient():request({
    url = "https://api.example.com/data",
    method = "GET"
}, function(response)
    if response.status == 200 then
        local data = json.decode(response.data)
        app:html(string.format([[
            <h1>API Data</h1>
            <pre>%s</pre>
        ]], json.encodeFormated(data)))
    end
end)

app:show()
```

### With Timers

```lua
local windows = require('windows')

local clock = windows.createWindow("Live Clock", 400, 200)

-- Update clock every second
setInterval(function()
    local time = os.date("%H:%M:%S")
    clock:html(string.format([[
        <div style="font-family: monospace; font-size: 3em; 
                    text-align: center; padding: 50px;">
            %s
        </div>
    ]], time))
end, 1000)

clock:show()
```

## Module Information

- **Version**: 1.0.0
- **Dependencies**: EPLua core, tkinter, optional HTML rendering libraries
- **License**: Same as EPLua project
- **Thread Safety**: GUI operations must run on main thread (especially on macOS)

## See Also

- [GUI Module Documentation](../src/eplua/gui.py) - Low-level GUI functions
- [Network Modules](NETWORK_MODULES.md) - HTTP, WebSocket, etc.
- [Timer Examples](timer_examples.lua) - Async timer functionality
- [JSON Module](README_JSON.md) - JSON encoding/decoding
