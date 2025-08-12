-- Native UI Demo - QuickApp Style Interface
-- Demonstrates dynamic UI building from JSON using native tkinter widgets

local nativeUI = require('native_ui')
local json = require('json')

print("🎛️ EPLua Native UI Demo")

-- Check if native UI is available
if not nativeUI.isAvailable() then
    print("❌ Native UI not available on this system")
    return
end

print("✅ Native UI available!")

-- Create the main window
print("\n📝 Creating QuickApp-style window...")

local mainWindow = nativeUI.createWindow("QuickApp 5555", 400, 600)

-- Build UI using the quick builder with explicit IDs
local ui = nativeUI.quickUI()
    :header("QuickApp 5555", 1, "main_title")
    :label("Connected ✅", "connection_status")
    :separator("sep1")
    :label("Current Value: 0", "value_display")
    :button("Turn On", "turn_on", true, "turn_on_btn")  -- Primary button
    :button("Turn Off", "turn_off", false, "turn_off_btn")
    :slider("Level", 0, 100, 25, "level_slider")
    :separator("sep2")
    :label("Status: Ready", "device_status")
    :buttonRow({
        {text = "Btn 1", action = "btn1", isPrimary = true},
        {text = "Btn 2", action = "btn2", isPrimary = false},
        {text = "Btn 3", action = "btn3", isPrimary = false},
        {text = "Btn 5", action = "btn5", isPrimary = false},
    })
    -- :button("Btn 1", "btn1", false, "action_btn1")
    -- :button("Btn 2", "btn2", false, "action_btn2")
    -- :button("Btn 3", "btn3", false, "action_btn3")
    -- :button("Btn 5", "btn5", false, "action_btn5")
    :separator("sep3")
    :slider("Secondary", 0, 100, 50, "secondary_slider")
    :dropdown("Mode", {"Auto", "Manual", "Off"}, "Auto", "mode_dropdown")
    :multiselect("Options", {"Feature A", "Feature B", "Feature C", "Debug Mode"}, {"Feature A"}, 3, "options_multiselect")
    :build()

-- Set the UI
mainWindow:setUI(ui)

-- Set up callbacks for interactive elements with proper IDs
local currentValue = 0
local isOn = false

-- Turn On button
mainWindow:setCallback("turn_on_btn", function(data)
    print("🟢 Turn On clicked (Element ID: " .. (data.element_id or "turn_on_btn") .. ")")
    isOn = true
    currentValue = mainWindow:getValue("level_slider") or 50
    mainWindow:setText("value_display", "Current Value: " .. currentValue)
    mainWindow:setText("device_status", "Status: Device ON")
    print("  Value set to:", currentValue)
end)

-- Turn Off button  
mainWindow:setCallback("turn_off_btn", function(data)
    print("🔴 Turn Off clicked (Element ID: " .. (data.element_id or "turn_off_btn") .. ")")
    isOn = false
    currentValue = 0
    mainWindow:setText("value_display", "Current Value: " .. currentValue)
    mainWindow:setText("device_status", "Status: Device OFF")
    mainWindow:setValue("level_slider", 0)
    print("  Value set to:", currentValue)
end)

-- Level slider
mainWindow:setCallback("level_slider", function(data)
    local value = data.value or mainWindow:getValue("level_slider") or 0
    print("🎚️ Level slider changed (Element ID: " .. (data.element_id or "level_slider") .. ") to:", value)
    if isOn then
        currentValue = value
        mainWindow:setText("value_display", "Current Value: " .. currentValue)
    end
end)

-- Mode dropdown
mainWindow:setCallback("mode_dropdown", function(data)
    local mode = data.value or mainWindow:getValue("mode_dropdown") or "Auto"
    print("⚙️ Mode changed (Element ID: " .. (data.element_id or "mode_dropdown") .. ") to:", mode)
    mainWindow:setText("device_status", "Status: Mode = " .. mode)
end)

-- Multi-select
mainWindow:setCallback("options_multiselect", function(data)
    local selected = data.values or {}
    print("☑️ Options selected (Element ID: " .. (data.element_id or "options_multiselect") .. "):", json.encode(selected))
end)

-- Action buttons with proper IDs
local actionButtons = {
    {id = "action_btn1", name = "Btn 1"},
    {id = "action_btn2", name = "Btn 2"}, 
    {id = "action_btn3", name = "Btn 3"},
    {id = "action_btn5", name = "Btn 5"}
}

for _, btn in ipairs(actionButtons) do
    mainWindow:setCallback(btn.id, function(data)
        local action = data.action or btn.name
        print("🔘 Button clicked (Element ID: " .. (data.element_id or btn.id) .. ") action:", action)
        
        -- Update button text to show it was clicked
        mainWindow:setText(btn.id, btn.name .. " ✓")
        
        -- Reset button text after 2 seconds
        setTimeout(function()
            mainWindow:setText(btn.id, btn.name)
        end, 2000)
        
        -- Update status with element identification
        mainWindow:setText("device_status", "Status: " .. btn.name .. " executed")
    end)
end

-- Show the window
mainWindow:show()

print("✅ QuickApp window created and displayed!")
print("📝 Window ID:", mainWindow:getId())

-- Create a second demo window
print("\n🎯 Creating additional demo window...")

local demoWindow = nativeUI.create("Native UI Demo", 500, 400)
demoWindow:setUI(nativeUI.examples.demo)
demoWindow:show()

-- Set up callbacks for demo window
demoWindow:setCallback("primary_btn", function(data)
    print("🎯 Primary action triggered!")
end)

demoWindow:setCallback("secondary_btn", function(data)
    print("⚡ Secondary action triggered!")
end)

demoWindow:setCallback("feature_switch", function(data)
    local enabled = data.data.value
    print("🔄 Feature switch:", enabled and "ON" or "OFF")
end)

demoWindow:setCallback("volume_slider", function(data)
    local volume = data.data.value
    print("🔊 Volume changed to:", volume)
end)

demoWindow:setCallback("theme_select", function(data)
    local theme = data.data.value
    print("🎨 Theme changed to:", theme)
end)

print("✅ Demo window created!")

-- Show all windows
print("\n📋 Current native windows:")
print(nativeUI.listWindows())

print("\n🎉 Native UI Demo complete!")
print("💡 Both windows should now be visible with working controls.")
print("🔧 Interact with buttons, sliders, and dropdowns to see callbacks.")
print("🎛️ This demonstrates a complete native UI solution!")

-- Keep the script running
setInterval(function()
    -- Update time display if needed
    -- You could update UI elements here
end, 5000)
