-- Native UI Module for EPLua
-- Wrapper around the windows module for backward compatibility

local windows = require('windows')

-- Re-export windows functions with native UI names for compatibility
local nativeUI = {}

-- Direct mapping to windows module
nativeUI.createWindow = windows.createNativeWindow  -- Use native window creation
nativeUI.create = windows.createNativeWindow        -- Use native window creation
nativeUI.isAvailable = windows.isAvailable
nativeUI.listWindows = windows.listWindows

-- Quick UI builder (for backward compatibility)
function nativeUI.quickUI()
    local builder = {}
    builder.elements = {}
    builder.nextId = 1
    
    -- Helper to generate ID if not provided
    function builder:_generateId(prefix)
        local id = prefix .. "_" .. self.nextId
        self.nextId = self.nextId + 1
        return id
    end
    
    function builder:header(text, level, id)
        table.insert(self.elements, {
            type = "header",
            text = text or "Header",
            level = level or 1,
            id = id or self:_generateId("header")
        })
        return self
    end
    
    function builder:label(text, id)
        table.insert(self.elements, {
            type = "label",
            text = text or "Label",
            id = id or self:_generateId("label")
        })
        return self
    end
    
    function builder:button(text, action, isPrimary, id)
        table.insert(self.elements, {
            type = "button",
            text = text or "Button",
            action = action or "click",
            style = { primary = isPrimary or false },
            id = id or self:_generateId("button")
        })
        return self
    end
    
    function builder:switch(text, defaultValue, id)
        table.insert(self.elements, {
            type = "switch",
            text = text or "Switch",
            value = defaultValue or false,
            id = id or self:_generateId("switch")
        })
        return self
    end
    
    function builder:slider(text, min, max, value, id)
        table.insert(self.elements, {
            type = "slider",
            text = text or "Slider",
            min = min or 0,
            max = max or 100,
            value = value or 50,
            id = id or self:_generateId("slider")
        })
        return self
    end
    
    function builder:dropdown(text, options, defaultValue, id)
        table.insert(self.elements, {
            type = "dropdown",
            text = text or "Select",
            options = options or {"Option 1", "Option 2"},
            value = defaultValue or (options and options[1]) or "Option 1",
            id = id or self:_generateId("dropdown")
        })
        return self
    end
    
    function builder:multiselect(text, options, defaultValues, height, id)
        table.insert(self.elements, {
            type = "multiselect",
            text = text or "Multi-select",
            options = options or {"Option 1", "Option 2", "Option 3"},
            values = defaultValues or {},
            height = height or 4,
            id = id or self:_generateId("multiselect")
        })
        return self
    end
    
    function builder:separator(id)
        table.insert(self.elements, {
            type = "separator",
            id = id or self:_generateId("separator")
        })
        return self
    end
    
    function builder:buttonRow(buttons, id)
        -- Create a horizontal row of buttons
        -- buttons: array of {text, action, isPrimary, id} or just strings
        local buttonElements = {}
        for i, btn in ipairs(buttons) do
            if type(btn) == "string" then
                -- Simple string format
                table.insert(buttonElements, {
                    text = btn,
                    action = btn:lower():gsub("%s+", "_"),
                    style = { primary = false },
                    id = self:_generateId("btn")
                })
            else
                -- Full button specification
                table.insert(buttonElements, {
                    text = btn.text or "Button",
                    action = btn.action or (btn.text and btn.text:lower():gsub("%s+", "_")) or "click",
                    style = { primary = btn.isPrimary or btn.primary or false },
                    id = btn.id or self:_generateId("btn")
                })
            end
        end
        
        table.insert(self.elements, {
            type = "button_row",
            buttons = buttonElements,
            id = id or self:_generateId("button_row")
        })
        return self
    end
    
    function builder:build()
        return {
            elements = self.elements
        }
    end
    
    return builder
end

-- JSON format builder for direct specification
function nativeUI.fromJSON(jsonString)
    local json = require('json')
    local ui = json.decode(jsonString)
    
    -- Ensure all elements have IDs
    if ui.elements then
        local nextId = 1
        for i, element in ipairs(ui.elements) do
            if not element.id then
                element.id = (element.type or "element") .. "_" .. nextId
                nextId = nextId + 1
            end
        end
    end
    
    return ui
end

-- Create UI from table with automatic ID assignment
function nativeUI.fromTable(uiTable)
    local ui = {}
    for k, v in pairs(uiTable) do
        ui[k] = v
    end
    
    -- Ensure all elements have IDs
    if ui.elements then
        local nextId = 1
        for i, element in ipairs(ui.elements) do
            if not element.id then
                element.id = (element.type or "element") .. "_" .. nextId
                nextId = nextId + 1
            end
        end
    end
    
    return ui
end

-- Example UI descriptions
nativeUI.examples = {}

-- Quick app UI
nativeUI.examples.quickApp = {
    elements = {
        {
            type = "header",
            text = "QuickApp 5555",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "Connected",
            id = "status"
        },
        {
            type = "separator",
            id = "sep1"
        },
        {
            type = "label",
            text = "0",
            id = "display"
        },
        {
            type = "button",
            text = "Turn On",
            action = "turn_on",
            style = { primary = true },
            id = "btn_on"
        },
        {
            type = "button",
            text = "Turn Off",
            action = "turn_off",
            id = "btn_off"
        },
        {
            type = "slider",
            text = "",
            min = 0,
            max = 100,
            value = 0,
            id = "slider1"
        },
        {
            type = "label",
            text = "Hello Tue Jul 1 06_34:53 2025",
            id = "time_display"
        }
    }
}

-- Simple demo UI
nativeUI.examples.demo = {
    elements = {
        {
            type = "header",
            text = "🎛️ Native UI Demo",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "This UI is built from JSON using native tkinter widgets",
            id = "description"
        },
        {
            type = "separator",
            id = "sep1"
        },
        {
            type = "button",
            text = "Primary Action",
            action = "primary",
            style = { primary = true },
            id = "primary_btn"
        },
        {
            type = "button",
            text = "Secondary Action",
            action = "secondary",
            id = "secondary_btn"
        },
        {
            type = "switch",
            text = "Enable Feature",
            value = true,
            id = "feature_switch"
        },
        {
            type = "slider",
            text = "Volume",
            min = 0,
            max = 100,
            value = 75,
            id = "volume_slider"
        },
        {
            type = "dropdown",
            text = "Theme",
            options = {"Light", "Dark", "Auto"},
            value = "Auto",
            id = "theme_select"
        }
    }
}

return nativeUI
