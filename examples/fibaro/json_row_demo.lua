-- JSON UI Row Demo - Simple _PY functions approach
-- Shows how to create JSON UI with row functionality

local nativeUI = require('native_ui')
local json = require('json')

print("🎛️ JSON UI Row Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Create JSON UI with rows
print("\n📝 Creating JSON UI with rows...")

local jsonUIWithRows = json.encode({
    elements = {
        {
            type = "header",
            text = "JSON UI Row Demo",
            level = 1,
            id = "title"
        },
        {
            type = "label", 
            text = "This demo shows JSON UI with row functionality",
            id = "description"
        },
        {
            type = "separator",
            id = "sep1"
        },
        
        -- Row 1: Status display row
        {
            type = "row",
            id = "status_row",
            elements = {
                {
                    type = "label",
                    text = "Status:",
                    id = "status_label"
                },
                {
                    type = "label", 
                    text = "Ready",
                    id = "status_value"
                },
                {
                    type = "label",
                    text = "Count: 0", 
                    id = "count_display"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep2"
        },
        
        -- Row 2: Button row
        {
            type = "row",
            id = "button_row",
            elements = {
                {
                    type = "button",
                    text = "Start",
                    action = "start",
                    style = { primary = true },
                    id = "start_btn"
                },
                {
                    type = "button", 
                    text = "Stop",
                    action = "stop",
                    id = "stop_btn"
                },
                {
                    type = "button",
                    text = "Reset",
                    action = "reset",
                    id = "reset_btn"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep3"
        },
        
        -- Row 3: Control row with slider and dropdown
        {
            type = "row", 
            id = "control_row",
            elements = {
                {
                    type = "slider",
                    text = "Level",
                    min = 0,
                    max = 100,
                    value = 50,
                    id = "level_slider"
                },
                {
                    type = "dropdown",
                    text = "Mode",
                    options = {"Auto", "Manual", "Debug"},
                    value = "Auto",
                    id = "mode_select"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep4"
        },
        
        -- Row 4: Switch and button combination
        {
            type = "row",
            id = "switch_row", 
            elements = {
                {
                    type = "switch",
                    text = "Enable",
                    value = true,
                    id = "enable_switch"
                },
                {
                    type = "button",
                    text = "Apply",
                    action = "apply",
                    id = "apply_btn"
                },
                {
                    type = "label",
                    text = "Output: OFF",
                    id = "output_status"
                }
            }
        },
        
        {
            type = "separator", 
            id = "sep5"
        },
        
        -- Single element (not in row)
        {
            type = "label",
            text = "Log: Ready to start...",
            id = "log_display"
        }
    }
})

-- Create window from JSON
local window = nativeUI.createWindow("JSON Row Demo", 500, 650)
local ui = nativeUI.fromJSON(jsonUIWithRows)
window:setUI(ui)

-- Demo state
local isRunning = false
local counter = 0
local currentLevel = 50

-- Set up callbacks using simple _PY functions approach
print("\n📞 Setting up callbacks...")

-- Start button
window:setCallback("start_btn", function(data)
    print("🟢 Start clicked")
    isRunning = true
    window:setText("status_value", "Running")
    window:setText("log_display", "Log: Started at " .. os.date("%H:%M:%S"))
    window:setText("start_btn", "Running...")
    
    -- Update output based on switch state
    local switchEnabled = window:getValue("enable_switch")
    if switchEnabled then
        window:setText("output_status", "Output: ON")
    end
end)

-- Stop button  
window:setCallback("stop_btn", function(data)
    print("🔴 Stop clicked")
    isRunning = false
    window:setText("status_value", "Stopped")
    window:setText("log_display", "Log: Stopped at " .. os.date("%H:%M:%S"))
    window:setText("start_btn", "Start")
    window:setText("output_status", "Output: OFF")
end)

-- Reset button
window:setCallback("reset_btn", function(data)
    print("🔄 Reset clicked")
    isRunning = false
    counter = 0
    currentLevel = 50
    
    -- Reset all displays
    window:setText("status_value", "Ready")
    window:setText("count_display", "Count: 0")
    window:setText("log_display", "Log: Reset at " .. os.date("%H:%M:%S"))
    window:setValue("level_slider", 50)
    window:setValue("mode_select", "Auto")
    window:setValue("enable_switch", true)
    window:setText("start_btn", "Start")
    window:setText("output_status", "Output: OFF")
end)

-- Level slider
window:setCallback("level_slider", function(data)
    currentLevel = data.value or 50
    print("🎚️ Level changed to:", currentLevel)
    window:setText("log_display", "Log: Level set to " .. currentLevel)
    
    -- Update output if running and enabled
    if isRunning then
        local switchEnabled = window:getValue("enable_switch")
        if switchEnabled then
            window:setText("output_status", "Output: " .. currentLevel .. "%")
        end
    end
end)

-- Mode dropdown
window:setCallback("mode_select", function(data)
    local mode = data.value or "Auto"
    print("⚙️ Mode changed to:", mode)
    window:setText("log_display", "Log: Mode changed to " .. mode)
    
    -- Change behavior based on mode
    if mode == "Debug" then
        window:setText("status_value", "Debug Mode")
    elseif isRunning then
        window:setText("status_value", "Running (" .. mode .. ")")
    end
end)

-- Enable switch
window:setCallback("enable_switch", function(data)
    local enabled = data.value
    print("🔘 Enable switch:", enabled and "ON" or "OFF")
    window:setText("log_display", "Log: Enable " .. (enabled and "ON" or "OFF"))
    
    -- Update output status
    if isRunning and enabled then
        window:setText("output_status", "Output: " .. currentLevel .. "%")
    else
        window:setText("output_status", "Output: OFF")
    end
end)

-- Apply button
window:setCallback("apply_btn", function(data)
    print("✅ Apply clicked")
    local mode = window:getValue("mode_select") or "Auto"
    local enabled = window:getValue("enable_switch")
    
    window:setText("log_display", "Log: Applied settings - Mode: " .. mode .. ", Enable: " .. (enabled and "ON" or "OFF"))
    
    if enabled and isRunning then
        window:setText("output_status", "Output: APPLIED")
        
        -- Reset to normal after 1 second
        setTimeout(function()
            window:setText("output_status", "Output: " .. currentLevel .. "%")
        end, 1000)
    end
end)

-- Show the window
window:show()
print("✅ JSON Row Demo window created!")

-- Set up real-time counter updates
print("\n🔄 Setting up real-time updates...")

setInterval(function()
    if isRunning then
        counter = counter + 1
        window:setText("count_display", "Count: " .. counter)
        
        -- Update log every 5 counts
        if counter % 5 == 0 then
            window:setText("log_display", "Log: Running... count = " .. counter)
        end
        
        print("📊 Counter updated:", counter)
    end
end, 1000)

print("\n🎉 JSON UI Row Demo complete!")
print("\n✨ Features demonstrated:")
print("   📄 JSON UI specification with rows")
print("   🏷️ Row elements with multiple controls")  
print("   🔘 Mixed element types in rows (buttons, labels, sliders, etc.)")
print("   📞 Simple callback functions for each element")
print("   🔄 Real-time updates using element IDs")
print("   🎛️ Cross-element interactions (switch affects output)")
print("\n💡 All interactions use simple _PY function callbacks!")
