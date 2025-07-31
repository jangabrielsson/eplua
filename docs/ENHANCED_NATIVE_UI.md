# Enhanced Native UI System - JSON Format & ID Management

## Overview

The EPLua Native UI system now supports:

1. **JSON format specification** - Define UIs with JSON strings
2. **Better ID management** - Automatic and explicit element IDs
3. **Element updates** - Update text/values by ID at runtime
4. **Callback identification** - Know which element triggered callbacks

## JSON Format Support

### Creating UI from JSON

```lua
local nativeUI = require('native_ui')
local json = require('json')

-- Define UI in JSON format
local uiJSON = json.encode({
    elements = {
        {
            type = "header",
            text = "My App",
            level = 1,
            id = "main_title"  -- Explicit ID
        },
        {
            type = "label",
            text = "Status: Ready",
            id = "status_label"
        },
        {
            type = "button",
            text = "Click Me",
            action = "click_action",
            style = { primary = true },
            id = "main_button"
        },
        {
            type = "slider",
            text = "Volume",
            min = 0,
            max = 100,
            value = 50,
            id = "volume_slider"
        }
    }
})

-- Create window from JSON
local window = nativeUI.createWindow("JSON Demo", 400, 300)
local ui = nativeUI.fromJSON(uiJSON)
window:setUI(ui)
window:show()
```

### Builder with Custom IDs

```lua
-- Quick builder with explicit IDs
local ui = nativeUI.quickUI()
    :header("Control Panel", 1, "panel_title")
    :label("Device: Offline", "device_status")
    :button("Connect", "connect", true, "connect_btn")
    :slider("Brightness", 0, 100, 50, "brightness_slider")
    :switch("Auto Mode", false, "auto_switch")
    :dropdown("Profile", {"Home", "Away"}, "Home", "profile_select")
    :build()

window:setUI(ui)
```

## Element Interaction

### Updating Elements by ID

```lua
-- Update text content
window:setText("status_label", "Status: Connected ✅")
window:setText("main_button", "Processing...")

-- Update values
window:setValue("volume_slider", 75)
window:setValue("auto_switch", true)
window:setValue("profile_select", "Away")

-- Generic property updates
window:updateElement("main_button", "enabled", false)
```

### Getting Element Values

```lua
-- Get current values
local volume = window:getValue("volume_slider")  -- Returns number
local autoMode = window:getValue("auto_switch")   -- Returns boolean
local profile = window:getValue("profile_select") -- Returns string

print("Volume:", volume)
print("Auto mode:", autoMode and "ON" or "OFF")
print("Profile:", profile)
```

### Callbacks with Element Identification

```lua
-- Callbacks receive element information
window:setCallback("main_button", function(data)
    print("Button clicked!")
    print("Element ID:", data.element_id or "main_button")
    print("Action:", data.action)
    
    -- Update other elements based on this callback
    window:setText("status_label", "Status: Button clicked!")
end)

window:setCallback("volume_slider", function(data)
    local value = data.value or window:getValue("volume_slider")
    print("Volume changed to:", value)
    print("Element ID:", data.element_id or "volume_slider")
    
    -- Update related elements
    window:setText("status_label", "Volume: " .. value .. "%")
end)
```

## Element Types & Properties

### Supported Element Types

| Type | Properties | Updatable Properties |
|------|------------|---------------------|
| `header` | text, level, id | text |
| `label` | text, id | text |
| `button` | text, action, style, id | text, enabled |
| `slider` | text, min, max, value, id | value |
| `switch` | text, value, id | value |
| `dropdown` | text, options, value, id | value |
| `multiselect` | text, options, values, height, id | values |
| `separator` | id | none |

### Element Definition Format

```lua
{
    type = "button",           -- Required: element type
    text = "Click Me",         -- Display text
    action = "my_action",      -- Action identifier for callbacks
    style = { primary = true }, -- Style options
    id = "my_button"           -- Unique identifier (auto-generated if not provided)
}
```

## ID Management

### Automatic ID Generation

If you don't specify an ID, the system automatically generates one:

```lua
local ui = nativeUI.quickUI()
    :header("Title")       -- Gets ID like "header_1"
    :button("Click")       -- Gets ID like "button_2"
    :slider("Value")       -- Gets ID like "slider_3"
    :build()
```

### Explicit ID Assignment

For reliable element access, always specify IDs:

```lua
local ui = nativeUI.quickUI()
    :header("Title", 1, "main_title")
    :button("Click", "action", true, "action_button")
    :slider("Value", 0, 100, 50, "value_slider")
    :build()
```

## Real-time Updates Example

```lua
-- Create UI with known IDs
local window = nativeUI.createWindow("Live Demo", 400, 300)
local ui = nativeUI.quickUI()
    :header("Live Updates", 1, "title")
    :label("Counter: 0", "counter_display")
    :button("Increment", "increment", true, "inc_button")
    :button("Reset", "reset", false, "reset_button")
    :slider("Speed", 1, 10, 5, "speed_slider")
    :build()

window:setUI(ui)

-- Set up interactivity
local counter = 0

window:setCallback("inc_button", function(data)
    counter = counter + 1
    window:setText("counter_display", "Counter: " .. counter)
    print("Incremented to:", counter)
end)

window:setCallback("reset_button", function(data)
    counter = 0
    window:setText("counter_display", "Counter: " .. counter)
    window:setValue("speed_slider", 5)
    print("Reset counter")
end)

window:setCallback("speed_slider", function(data)
    local speed = data.value
    print("Speed changed to:", speed)
    window:setText("title", "Live Updates (Speed: " .. speed .. ")")
end)

-- Real-time updates
setInterval(function()
    local timestamp = os.date("%H:%M:%S")
    window:setText("title", "Live Updates @ " .. timestamp)
end, 1000)

window:show()
```

## Best Practices

1. **Always use explicit IDs** for elements you need to interact with
2. **Use descriptive ID names** like `status_label`, `connect_button`
3. **Store element references** if updating frequently:
   ```lua
   local statusId = "status_label"
   window:setText(statusId, "Ready")
   ```
4. **Handle callback errors** gracefully
5. **Validate element values** before using them:
   ```lua
   local value = window:getValue("slider") or 0
   ```

## Complete Example Files

- `dev/json_native_ui_demo.lua` - JSON format demonstration
- `dev/enhanced_native_ui_demo.lua` - Comprehensive feature showcase
- `examples/lua/native_ui_demo.lua` - Updated with ID management

## Migration Guide

### From Old System
```lua
-- Old way (auto-generated IDs)
window:setCallback("button_3", function(data)
    -- Hard to maintain
end)

-- New way (explicit IDs)
window:setCallback("turn_on_button", function(data)
    print("Element ID:", data.element_id)
    window:setText("status_label", "Device ON")
end)
```

This enhanced system provides reliable, maintainable UI development with proper element identification and real-time update capabilities.
