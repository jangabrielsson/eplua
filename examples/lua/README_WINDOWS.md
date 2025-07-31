# Windows Module for EPLua

The Windows module provides a comprehensive Lua-friendly interface for creating and managing GUI windows with both HTML rendering and native UI capabilities.

## Features

- 🪟 **Native UI Windows**: Create windows with native tkinter widgets
- 🌐 **HTML Windows**: Rich HTML content rendering (when supported)
- 📱 **JSON UI Builder**: Define interfaces using JSON format
- 🔧 **Dynamic Updates**: Update UI elements by ID at runtime
- 🎯 **Event Callbacks**: Handle user interactions with callback identification
- 🔗 **Method Chaining**: Fluent API for easy window creation

## Quick Start

### Native UI (Recommended)

```lua
local windows = require('windows')

-- Create native UI with JSON
local win = windows.createWindow("My App", 600, 400)
win:setUI({
    type = "frame",
    padding = 20,
    children = {
        {id = "title", type = "label", text = "Welcome to My App!", font = {"Arial", 16}},
        {id = "input", type = "entry", placeholder = "Enter your name"},
        {id = "submit", type = "button", text = "Submit", callback = "handleSubmit"}
    }
})
win:show()

-- Update elements dynamically
win:setText("title", "Hello " .. name .. "!")
```

### HTML Windows (Legacy)

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
- Returns: string ("cef", "cefpython3", or "none")

#### `windows.getCapabilities()`
Get comprehensive capability information.
- Returns: table with `gui`, `html`, `native_ui`, and `engine` fields

#### `windows.listWindows()`
Get information about all open windows.
- Returns: string with window details

#### `windows.demo()`
Create and show a demonstration window.
- Returns: Window object

#### `windows.help()`
Display help information.

### Window Object Methods

#### Native UI Methods

```lua
local win = windows.createWindow("My Window")

-- UI Content methods
win:setUI(ui_definition)        -- Set native UI from table/JSON
win:ui(definition)              -- Alias for setUI (chainable)

-- Element interaction methods
win:setText(elementId, text)    -- Update text of an element
win:setValue(elementId, value)  -- Update value of an element  
win:updateElement(elementId, updates)  -- Update multiple properties
win:getValue(elementId)         -- Get current value of an element
win:setCallback(elementId, callback)  -- Set callback for an element

-- HTML Content methods (legacy)
win:setHtml(html_content)       -- Set HTML content
win:setUrl(url)                 -- Load a URL
win:html(content)               -- Alias for setHtml (chainable)
win:url(address)                -- Alias for setUrl (chainable)

-- Display methods
win:show()                      -- Show the window
win:hide()                      -- Hide the window
win:display()                   -- Alias for show (chainable)
win:close()                     -- Close and destroy the window

-- Information methods
win:getId()                     -- Get window ID
win:isClosed()                  -- Check if window is closed
```

#### Method Chaining

All content and display methods return the Window object, enabling fluent method chaining:

```lua
-- Native UI chaining
windows.createWindow("Native Demo")
    :setUI({
        type = "frame",
        children = {
            {type = "label", text = "Hello Native UI!"},
            {type = "button", text = "Click Me"}
        }
    })
    :show()

-- HTML chaining (legacy)
windows.createWindow("HTML Demo")
    :setHtml("<h1>Hello!</h1>")
    :show()

-- Or with aliases
windows.create("Fluent Demo")
    :ui({type = "label", text = "Fluent API!"})
    :display()
```

### Functional Interface

For those who prefer functional programming style:

```lua
local id = windows.createWindow("Functional Style"):getId()

-- Native UI functions
windows.setWindowUI(id, {type = "label", text = "Hello!"})
windows.setWindowText(id, "myLabel", "Updated text")
windows.showWindow(id)
windows.closeWindow(id)

-- HTML functions (legacy)
windows.setWindowHtml(id, "<h1>Hello!</h1>")
windows.setWindowUrl(id, "https://example.com")
```

**Functional API:**
- `windows.setWindowUI(windowId, definition)` - Set native UI
- `windows.setWindowText(windowId, elementId, text)` - Update element text
- `windows.setWindowValue(windowId, elementId, value)` - Update element value
- `windows.updateWindowElement(windowId, elementId, updates)` - Update element properties
- `windows.getWindowValue(windowId, elementId)` - Get element value
- `windows.setWindowCallback(windowId, elementId, callback)` - Set element callback
- `windows.setWindowHtml(windowId, html)` - Set HTML content (legacy)
- `windows.setWindowUrl(windowId, url)` - Set URL (legacy)
- `windows.showWindow(windowId)` - Show window
- `windows.hideWindow(windowId)` - Hide window
- `windows.closeWindow(windowId)` - Close window

## Native UI Reference

### Supported Widget Types

- **label**: Display text
- **button**: Clickable button with callback
- **entry**: Text input field
- **text**: Multi-line text area
- **frame**: Container for other widgets
- **checkbox**: Boolean checkbox
- **radio**: Radio button
- **combobox**: Dropdown selection
- **listbox**: Multi-item list
- **scale**: Slider for numeric values
- **progressbar**: Progress indicator
- **separator**: Visual separator line

### UI Definition Format

```lua
{
    type = "widget_type",
    id = "unique_id",           -- Optional, auto-generated if not provided
    text = "Display text",      -- For labels, buttons
    value = "default_value",    -- For inputs
    callback = "callback_name", -- For interactive elements
    
    -- Layout properties
    padding = 10,               -- Padding around widget
    sticky = "ew",             -- Grid sticky direction
    
    -- Container properties
    children = { ... },         -- Child widgets (for frames)
    
    -- Widget-specific properties
    font = {"Arial", 12},       -- Font family and size
    state = "normal",           -- Widget state
    placeholder = "hint text",  -- Entry placeholder
    options = {"opt1", "opt2"}, -- Combobox/listbox options
    from = 0, to = 100,        -- Scale range
    orient = "horizontal"       -- Scale/progressbar orientation
}
```

## Usage Examples

### Complete Native UI Application

```lua
local windows = require('windows')

-- Create main application window
local app = windows.createWindow("User Registration", 500, 400)

-- Define UI structure
local ui = {
    type = "frame",
    padding = 20,
    children = {
        {id = "title", type = "label", text = "User Registration", font = {"Arial", 16}},
        {type = "separator", sticky = "ew"},
        
        {id = "name_label", type = "label", text = "Full Name:"},
        {id = "name_entry", type = "entry", placeholder = "Enter your full name"},
        
        {id = "email_label", type = "label", text = "Email:"},
        {id = "email_entry", type = "entry", placeholder = "Enter your email"},
        
        {id = "age_label", type = "label", text = "Age:"},
        {id = "age_scale", type = "scale", from = 18, to = 100, value = 25, orient = "horizontal"},
        {id = "age_display", type = "label", text = "25"},
        
        {id = "newsletter", type = "checkbox", text = "Subscribe to newsletter", value = true},
        
        {type = "frame", children = {
            {id = "submit", type = "button", text = "Submit", callback = "handleSubmit"},
            {id = "cancel", type = "button", text = "Cancel", callback = "handleCancel"}
        }}
    }
}

-- Set the UI and show the window
app:setUI(ui):show()

-- Handle age slider updates
app:setCallback("age_scale", "updateAge")

function updateAge(elementId, value, windowId)
    local win = windows.getWindowById(windowId)
    win:setText("age_display", tostring(math.floor(value)))
end

function handleSubmit(elementId, value, windowId)
    local win = windows.getWindowById(windowId)
    local name = win:getValue("name_entry")
    local email = win:getValue("email_entry")
    local age = win:getValue("age_scale")
    local newsletter = win:getValue("newsletter")
    
    print(string.format("Registration: %s <%s>, Age: %d, Newsletter: %s", 
          name, email, math.floor(age), tostring(newsletter)))
    
    win:setText("title", "Registration Submitted!")
end

function handleCancel(elementId, value, windowId)
    local win = windows.getWindowById(windowId)
    win:close()
end
```

### JSON-Based UI Definition

```lua
local windows = require('windows')

-- Load UI from JSON string or file
local jsonUI = [[{
    "type": "frame",
    "padding": 15,
    "children": [
        {"id": "header", "type": "label", "text": "JSON UI Demo", "font": ["Arial", 14]},
        {"type": "separator", "sticky": "ew"},
        {"id": "message", "type": "label", "text": "This UI was created from JSON!"},
        {"id": "close_btn", "type": "button", "text": "Close", "callback": "closeWindow"}
    ]
}]]

local app = windows.createWindow("JSON Demo", 400, 200)
app:setUI(json.decode(jsonUI)):show()

function closeWindow(elementId, value, windowId)
    windows.getWindowById(windowId):close()
end
```

### Dynamic UI Updates

```lua
local windows = require('windows')

local counter = 0
local app = windows.createWindow("Counter App", 300, 150)

app:setUI({
    type = "frame",
    padding = 20,
    children = {
        {id = "counter", type = "label", text = "Count: 0", font = {"Arial", 14}},
        {id = "increment", type = "button", text = "+1", callback = "increment"},
        {id = "decrement", type = "button", text = "-1", callback = "decrement"},
        {id = "reset", type = "button", text = "Reset", callback = "reset"}
    }
}):show()

function increment(elementId, value, windowId)
    counter = counter + 1
    updateCounter(windowId)
end

function decrement(elementId, value, windowId)
    counter = counter - 1
    updateCounter(windowId)
end

function reset(elementId, value, windowId)
    counter = 0
    updateCounter(windowId)
end

function updateCounter(windowId)
    local win = windows.getWindowById(windowId)
    win:setText("counter", "Count: " .. counter)
end
```

### Legacy HTML Examples

#### Basic Window with HTML

```lua
local windows = require('windows')

local win = windows.createWindow("My App", 600, 400)
win:setHtml([[
    <html>
    <head><title>My App</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>Welcome to My App!</h1>
        <p>This is a beautiful HTML interface powered by CEF (Chromium).</p>
        <p><strong>Note:</strong> Consider using native UI for better performance and consistency.</p>
        <p><em>CEF supports full HTML5, CSS3, and JavaScript!</em></p>
    </body>
    </html>
]])
win:show()
```

#### Loading Web Pages

```lua
local windows = require('windows')

if windows.htmlSupported() then
    local browser = windows.createWindow("Web Browser", 1000, 700)
    browser:setUrl("https://example.com")
    browser:show()
    print("Using HTML engine:", windows.getHtmlEngine()) -- Should show "cef" or "cefpython3"
else
    print("CEF HTML rendering not available - use native UI instead")
end
```

## Error Handling

The windows module provides comprehensive error handling:

```lua
local windows = require('windows')

-- Check availability before use
if not windows.isAvailable() then
    error("GUI not available")
end

-- Safe window operations with native UI
local win = windows.createWindow("Test")
local success, err = pcall(function()
    win:setUI({
        type = "frame",
        children = {
            {type = "label", text = "Test UI"},
            {type = "button", text = "OK"}
        }
    })
    win:show()
end)

if not success then
    print("Error:", err)
end

-- Element update error handling
local updateSuccess, updateErr = pcall(function()
    win:setText("nonexistent_id", "This will fail")
end)

if not updateSuccess then
    print("Update error:", updateErr)
end

-- Operations on closed windows will throw errors
win:close()
-- win:show() -- This would throw an error
```

## Platform Support

- **Windows**: Full support with native tkinter widgets and optional CEF HTML rendering
- **macOS**: Full support (GUI operations run on main thread automatically, CEF available)
- **Linux**: Full support with native tkinter widgets and optional CEF HTML rendering

**UI Rendering:**
- **Native UI**: Always available (tkinter-based, recommended)
- **HTML Rendering**: Optional, powered by Chromium Embedded Framework (CEF)
  - **cefpython3**: Modern HTML5/CSS3/JavaScript support with full web standards
  - **CEF Browser**: Embedded Chromium browser for rich web content
  - **Fallback**: Native UI mode when CEF is not available or installed

**Performance Notes:**
- Native UI provides better performance and platform consistency
- CEF HTML rendering offers full web browser capabilities but uses more resources
- Consider native UI for forms and controls, CEF for rich web content and dashboards

## Integration Examples

### With Native UI Module

```lua
local windows = require('windows')
local native_ui = require('native_ui')

-- Use the enhanced native UI builder
local app = native_ui.createWindow("Enhanced App", 600, 400)
    :addLabel("Welcome to Enhanced UI!")
    :addEntry("name_input", "Enter your name")
    :addButton("submit", "Submit", function(id, value, windowId)
        local name = app:getValue("name_input")
        app:addLabel("greeting", "Hello " .. name .. "!")
    end)
    :show()
```

### With HTTP Module

```lua
local windows = require('windows')
local net = require('net')

local app = windows.createWindow("API Dashboard", 600, 400)

-- Create loading UI
app:setUI({
    type = "frame",
    padding = 20,
    children = {
        {id = "status", type = "label", text = "Loading data..."},
        {id = "progress", type = "progressbar", sticky = "ew"},
        {id = "data", type = "text", state = "readonly", sticky = "nsew"}
    }
}):show()

-- Load data from API and update UI
net.HTTPClient():request({
    url = "https://api.example.com/data",
    method = "GET"
}, function(response)
    if response.status == 200 then
        local data = json.decode(response.data)
        app:setText("status", "Data loaded successfully!")
        app:setValue("data", json.encodeFormated(data))
    else
        app:setText("status", "Failed to load data: " .. response.status)
        app:setValue("data", "Error: " .. (response.data or "Unknown error"))
    end
end)
```

### With Timers

```lua
local windows = require('windows')

local seconds = 0
local clock = windows.createWindow("Live Clock", 400, 200)

-- Create clock UI
clock:setUI({
    type = "frame",
    padding = 30,
    children = {
        {id = "time", type = "label", text = "00:00:00", font = {"Courier", 24}},
        {id = "elapsed", type = "label", text = "Elapsed: 0s"},
        {id = "reset", type = "button", text = "Reset", callback = "resetTimer"}
    }
}):show()

-- Update clock every second
setInterval(function()
    local time = os.date("%H:%M:%S")
    seconds = seconds + 1
    
    clock:setText("time", time)
    clock:setText("elapsed", "Elapsed: " .. seconds .. "s")
end, 1000)

function resetTimer(elementId, value, windowId)
    seconds = 0
    local win = windows.getWindowById(windowId)
    win:setText("elapsed", "Elapsed: 0s")
end
```

### Form Validation Example

```lua
local windows = require('windows')

local form = windows.createWindow("Contact Form", 500, 350)

form:setUI({
    type = "frame",
    padding = 20,
    children = {
        {id = "title", type = "label", text = "Contact Form", font = {"Arial", 16}},
        {type = "separator", sticky = "ew"},
        
        {id = "name_label", type = "label", text = "Name:"},
        {id = "name", type = "entry", placeholder = "Required"},
        {id = "name_error", type = "label", text = "", font = {"Arial", 9}},
        
        {id = "email_label", type = "label", text = "Email:"},
        {id = "email", type = "entry", placeholder = "Required"},
        {id = "email_error", type = "label", text = "", font = {"Arial", 9}},
        
        {id = "message_label", type = "label", text = "Message:"},
        {id = "message", type = "text", placeholder = "Optional"},
        
        {type = "frame", children = {
            {id = "submit", type = "button", text = "Submit", callback = "validateAndSubmit"},
            {id = "clear", type = "button", text = "Clear", callback = "clearForm"}
        }}
    }
}):show()

function validateAndSubmit(elementId, value, windowId)
    local win = windows.getWindowById(windowId)
    local valid = true
    
    -- Clear previous errors
    win:setText("name_error", "")
    win:setText("email_error", "")
    
    -- Validate name
    local name = win:getValue("name")
    if not name or name:trim() == "" then
        win:setText("name_error", "⚠ Name is required")
        valid = false
    end
    
    -- Validate email
    local email = win:getValue("email")
    if not email or not email:match("^[^@]+@[^@]+%.[^@]+$") then
        win:setText("email_error", "⚠ Valid email is required")
        valid = false
    end
    
    if valid then
        local message = win:getValue("message")
        print(string.format("Form submitted: %s <%s>: %s", name, email, message or ""))
        win:setText("title", "✓ Form submitted successfully!")
        
        -- Clear form after success
        setTimeout(function()
            clearForm(nil, nil, windowId)
            win:setText("title", "Contact Form")
        end, 2000)
    end
end

function clearForm(elementId, value, windowId)
    local win = windows.getWindowById(windowId)
    win:setValue("name", "")
    win:setValue("email", "")
    win:setValue("message", "")
    win:setText("name_error", "")
    win:setText("email_error", "")
end
```

## Migration from HTML

If you're migrating from HTML-based windows to native UI:

### Before (HTML)
```lua
local win = windows.createWindow("App")
win:setHtml([[
    <form>
        <label>Name:</label>
        <input type="text" id="name">
        <button onclick="submit()">Submit</button>
    </form>
]])
```

### After (Native UI)
```lua
local win = windows.createWindow("App")
win:setUI({
    type = "frame",
    children = {
        {type = "label", text = "Name:"},
        {id = "name", type = "entry"},
        {id = "submit", type = "button", text = "Submit", callback = "handleSubmit"}
    }
})

function handleSubmit(elementId, value, windowId)
    local name = windows.getWindowById(windowId):getValue("name")
    print("Submitted:", name)
end
```

## Module Information

- **Version**: 2.0.0
- **Dependencies**: EPLua core, tkinter, optional cefpython3 for HTML rendering
- **License**: Same as EPLua project
- **Thread Safety**: GUI operations automatically handled on main thread
- **Recommended**: Use native UI for new projects, CEF HTML for rich web content
- **CEF Support**: Full HTML5/CSS3/JavaScript when cefpython3 is available

## See Also

- [Enhanced Native UI Documentation](../../docs/ENHANCED_NATIVE_UI.md) - Comprehensive native UI guide
- [Native UI Module](native_ui_demo.lua) - Quick UI builder examples
- [Network Modules](../../docs/NETWORK_MODULES.md) - HTTP, WebSocket, MQTT integration
- [Timer Examples](timer_examples.lua) - Async timer functionality
- [JSON Module](README_JSON.md) - JSON encoding/decoding for UI definitions
