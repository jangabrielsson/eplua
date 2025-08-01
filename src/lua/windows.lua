-- Windows Module for EPLua
-- Provides a Lua-friendly interface to the GUI window functions
-- Usage: local windows = require('windows')

local windows = {}

-- Module information
windows._VERSION = "1.0.0"
windows._DESCRIPTION = "EPLua Windows Module - Lua-friendly GUI interface"

-- Check if GUI is available
local function ensureGuiAvailable()
    if not _PY.gui_available() then
        error("GUI (tkinter) is not available on this system")
    end
end

-- Get capability information
function windows.isAvailable()
    return _PY.gui_available()
end

function windows.htmlSupported()
    return _PY.html_rendering_available()
end

function windows.getHtmlEngine()
    return _PY.get_html_engine()
end

function windows.getCapabilities()
    return {
        gui = _PY.gui_available(),
        html = _PY.html_rendering_available(),
        engine = _PY.get_html_engine(),
        native_ui = true
    }
end

-- Window class for object-oriented interface
local Window = {}
Window.__index = Window

function Window:new(id)
    local obj = {
        id = id,
        _closed = false
    }
    setmetatable(obj, Window)
    return obj
end

-- Native Window class for native UI windows
local NativeWindow = {}
NativeWindow.__index = NativeWindow

function NativeWindow:new(id)
    local obj = {
        id = id,
        _closed = false
    }
    setmetatable(obj, NativeWindow)
    return obj
end

function NativeWindow:setUI(uiDescription)
    if self._closed then
        error("Cannot operate on closed window")
    end
    
    -- Convert to table if it's a JSON string
    local uiTable
    if type(uiDescription) == "string" then
        local json = require('json')
        uiTable = json.decode(uiDescription)
    else
        uiTable = uiDescription
    end
    
    local result = _PY.setNativeUI(self.id, uiTable)
    if not result then
        error("Failed to set UI")
    end
    return self
end

function NativeWindow:show()
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.showNativeWindow(self.id)
    if not result then
        error("Failed to show window")
    end
    return self
end

function NativeWindow:hide()
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.hideNativeWindow(self.id)
    if not result then
        error("Failed to hide window")
    end
    return self
end

function NativeWindow:close()
    if self._closed then
        return self
    end
    local result = _PY.closeNativeWindow(self.id)
    if not result then
        error("Failed to close window")
    end
    self._closed = true
    return self
end

function NativeWindow:setCallback(elementId, callback)
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.setNativeCallback(self.id, elementId, callback)
    if not result then
        error("Failed to set callback")
    end
    return self
end

function NativeWindow:getValue(elementId)
    if self._closed then
        error("Cannot operate on closed window")
    end
    return _PY.getNativeValue(self.id, elementId)
end

function NativeWindow:setValue(elementId, value)
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.setNativeValue(self.id, elementId, value)
    if not result then
        error("Failed to set value")
    end
    return self
end

function NativeWindow:setText(elementId, text)
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.setNativeValue(self.id, elementId, text)
    if not result then
        error("Failed to set text")
    end
    return self
end

function NativeWindow:getId()
    return self.id
end

function NativeWindow:isClosed()
    return self._closed
end

function Window:setHtml(html)
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.set_window_html(self.id, html)
    if result:match("^ERROR:") then
        error(result)
    end
    return self
end

function Window:setUI(uiDescription)
    if self._closed then
        error("Cannot operate on closed window")
    end
    
    -- Convert to table if it's a JSON string
    local uiTable
    if type(uiDescription) == "string" then
        local json = require('json')
        uiTable = json.decode(uiDescription)
    else
        uiTable = uiDescription
    end
    
    local result = _PY.setNativeUI(self.id, uiTable)
    if not result then
        error("Failed to set UI")
    end
    return self
end

function Window:show()
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.show_window(self.id)
    if result:match("^ERROR:") then
        error(result)
    end
    return self
end

function Window:hide()
    if self._closed then
        error("Cannot operate on closed window")
    end
    local result = _PY.hide_window(self.id)
    if result:match("^ERROR:") then
        error(result)
    end
    return self
end

function Window:close()
    if self._closed then
        return self
    end
    local result = _PY.close_window(self.id)
    if result:match("^ERROR:") then
        error(result)
    end
    self._closed = true
    return self
end

function Window:isClosed()
    return self._closed
end

function Window:getId()
    return self.id
end

-- Element interaction methods
function Window:setCallback(elementId, callback)
    -- Store callback for this window and element
    if not self.callbacks then
        self.callbacks = {}
    end
    self.callbacks[elementId] = callback
    
    -- TODO: Register with bridge when callbacks are implemented
    print("Callback registered for element:", elementId)
    return self
end

function Window:getValue(elementId)
    local result = _PY.getElementValue(self.id, elementId)
    if result and not result:match("^ERROR:") then
        local json = require('json')
        local data = json.decode(result)
        if data.success then
            return data.value
        end
    end
    return nil
end

function Window:setValue(elementId, value)
    local result = _PY.updateElement(self.id, elementId, "value", value)
    if result and result:match("^ERROR:") then
        error("Failed to set value: " .. result)
    end
    return self
end

function Window:setText(elementId, text)
    local result = _PY.updateElement(self.id, elementId, "text", text)
    if result and result:match("^ERROR:") then
        error("Failed to set text: " .. result)
    end
    return self
end

function Window:updateElement(elementId, property, value)
    local result = _PY.updateElement(self.id, elementId, property, value)
    if result and result:match("^ERROR:") then
        error("Failed to update element: " .. result)
    end
    return self
end

-- Method chaining for fluent interface
function Window:html(content)
    return self:setHtml(content)
end

function Window:url(address)
    return self:setUrl(address)
end

function Window:display()
    return self:show()
end

-- Window creation function
function windows.createWindow(title, width, height)
    ensureGuiAvailable()
    
    -- Set defaults
    title = title or "EPLua Window"
    width = width or 800
    height = height or 600
    
    local result = _PY.create_window(title, width, height)
    if result:match("^ERROR:") then
        error(result)
    end
    
    -- Return a Window object
    return Window:new(result)
end

-- Native UI window creation function
function windows.createNativeWindow(title, width, height)
    ensureGuiAvailable()
    
    -- Set defaults
    title = title or "EPLua Native Window"
    width = width or 800
    height = height or 600
    
    local result = _PY.createNativeWindow(title, width, height)
    if type(result) ~= "table" or not result.window_id then
        error("Failed to create native window")
    end
    
    -- Return a NativeWindow object with the native window ID
    return NativeWindow:new(result.window_id)
end

-- Convenience function aliases
windows.create = windows.createWindow
windows.new = windows.createWindow

-- Direct function interface (for those who prefer functional style)
function windows.setWindowHtml(windowId, html)
    local result = _PY.set_window_html(windowId, html)
    if result:match("^ERROR:") then
        error(result)
    end
    return true
end

function windows.setWindowUrl(windowId, url)
    local result = _PY.set_window_url(windowId, url)
    if result:match("^ERROR:") then
        error(result)
    end
    return true
end

function windows.showWindow(windowId)
    local result = _PY.show_window(windowId)
    if result:match("^ERROR:") then
        error(result)
    end
    return true
end

function windows.hideWindow(windowId)
    local result = _PY.hide_window(windowId)
    if result:match("^ERROR:") then
        error(result)
    end
    return true
end

function windows.closeWindow(windowId)
    local result = _PY.close_window(windowId)
    if result:match("^ERROR:") then
        error(result)
    end
    return true
end

function windows.listWindows()
    return _PY.list_windows()
end

-- Utility functions
function windows.showGui()
    local result = _PY.show_gui()
    if result:match("^ERROR:") then
        error(result)
    end
    return true
end

-- Quick demo function
function windows.demo()
    if not windows.isAvailable() then
        print("❌ GUI not available")
        return false
    end
    
    print("🪟 Creating demo window...")
    local win = windows.createWindow("EPLua Demo", 600, 400)
    
    local html = [[
<!DOCTYPE html>
<html>
<head>
    <title>EPLua Demo</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 10px; 
            backdrop-filter: blur(10px);
        }
        .title { 
            font-size: 24px; 
            margin-bottom: 20px; 
            text-align: center;
        }
        .info { 
            margin: 10px 0; 
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 5px;
        }
        .success { color: #4ade80; }
        .engine { color: #f59e0b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="title">🚀 EPLua Windows Demo</div>
        <div class="info">
            <strong>GUI Available:</strong> 
            <span class="success">✅ Yes</span>
        </div>
        <div class="info">
            <strong>HTML Rendering:</strong> 
            <span class="]] .. (windows.htmlSupported() and "success\">✅ Yes" or "\">❌ No") .. [[</span>
        </div>
        <div class="info">
            <strong>Rendering Engine:</strong> 
            <span class="engine">]] .. windows.getHtmlEngine() .. [[</span>
        </div>
        <div class="info">
            <strong>Window ID:</strong> 
            <code>]] .. win:getId() .. [[</code>
        </div>
        <div class="info" style="margin-top: 20px; text-align: center;">
            <strong>🎉 Windows module is working!</strong><br>
            <small>You can now create beautiful HTML windows from Lua</small>
        </div>
    </div>
</body>
</html>
]]
    
    win:setHtml(html):show()
    
    print("✅ Demo window created and shown!")
    print("📝 Window ID:", win:getId())
    print("🔧 Use win:close() to close the window")
    
    return win
end

-- Help function
function windows.help()
    print([[
🪟 EPLua Windows Module Help

OBJECT-ORIENTED INTERFACE:
  local win = windows.createWindow("Title", 800, 600)
  win:setHtml("<h1>Hello!</h1>")  -- Set HTML content
  win:setUrl("https://example.com")  -- Load URL
  win:show()                         -- Show window
  win:hide()                         -- Hide window
  win:close()                        -- Close window

FLUENT INTERFACE (METHOD CHAINING):
  windows.createWindow("Demo")
    :html("<h1>Hello World!</h1>")
    :show()

FUNCTIONAL INTERFACE:
  local id = windows.createWindow("Title")
  windows.setWindowHtml(id, "<h1>Hello!</h1>")
  windows.showWindow(id)
  windows.closeWindow(id)

UTILITY FUNCTIONS:
  windows.isAvailable()      -- Check if GUI is available
  windows.htmlSupported()    -- Check if HTML rendering works
  windows.getHtmlEngine()    -- Get HTML engine name
  windows.getCapabilities()  -- Get all capability info
  windows.listWindows()      -- List all open windows
  windows.demo()             -- Show a demo window
  windows.help()             -- Show this help

ALIASES:
  windows.create()  = windows.createWindow()
  windows.new()     = windows.createWindow()
]])
end

-- Module metadata
windows.capabilities = windows.getCapabilities
windows.info = windows.help

return windows
