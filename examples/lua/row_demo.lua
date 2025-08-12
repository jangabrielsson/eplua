-- Row Demo - Demonstrates the new generalized row functionality
-- Shows how to create horizontal rows of mixed UI elements

local nativeUI = require('native_ui')
local json = require('json')

print("🎛️ EPLua Row Demo")

-- Check if native UI is available
if not nativeUI.isAvailable() then
    print("❌ Native UI not available on this system")
    return
end

print("✅ Native UI available!")

-- Create the main window
print("\n📝 Creating Row Demo window...")

local mainWindow = nativeUI.createWindow("Row Demo", 600, 700)

-- Build UI demonstrating various row configurations
local ui = nativeUI.quickUI()
    :header("Row Demo", 1, "main_title")
    :label("This demo shows different types of horizontal rows", "description")
    :separator("sep1")
    
    -- Traditional button row (backward compatibility)
    :label("Traditional Button Row:", "button_row_label")
    :buttonRow({
        {text = "Save", action = "save", isPrimary = true},
        {text = "Cancel", action = "cancel"},
        {text = "Help", action = "help"},
    }, "traditional_button_row")
    :separator("sep2")
    
    -- Mixed row with buttons and labels
    :label("Mixed Row (Buttons + Labels):", "mixed_row_label")
    :row({
        {type = "button", text = "Action", action = "action1", isPrimary = true, id = "action_btn"},
        {type = "label", text = "Status: Ready", id = "status_label"},
        {type = "button", text = "Reset", action = "reset", id = "reset_btn"}
    }, "mixed_row")
    :separator("sep3")
    
    -- Control row with slider and dropdown
    :label("Control Row (Slider + Dropdown):", "control_row_label")
    :row({
        {type = "slider", text = "Volume", min = 0, max = 100, value = 75, id = "volume_slider"},
        {type = "dropdown", text = "Mode", options = {"Auto", "Manual", "Custom"}, value = "Auto", id = "mode_dropdown"}
    }, "control_row")
    :separator("sep4")
    
    -- Switch and button row
    :label("Switch + Button Row:", "switch_row_label")
    :row({
        {type = "switch", text = "Enable", value = true, id = "enable_switch"},
        {type = "button", text = "Configure", action = "configure", id = "config_btn"},
        {type = "button", text = "Test", action = "test", id = "test_btn"}
    }, "switch_row")
    :separator("sep5")
    
    -- Complex row with multiple element types
    :label("Complex Mixed Row:", "complex_row_label")
    :row({
        {type = "label", text = "Level:", id = "level_label"},
        {type = "slider", min = 1, max = 10, value = 5, id = "level_slider"},
        {type = "dropdown", options = {"Low", "Medium", "High"}, value = "Medium", id = "priority_dropdown"},
        {type = "switch", text = "Auto", value = false, id = "auto_switch"}
    }, "complex_row")
    :separator("sep6")
    
    -- Multiselect in a row (demonstrates height control)
    :label("Row with Multiselect:", "multiselect_row_label")
    :row({
        {type = "multiselect", text = "Features", 
         options = {"Feature A", "Feature B", "Feature C", "Feature D"}, 
         values = {"Feature A"}, height = 3, id = "features_multiselect"},
        {type = "button", text = "Apply", action = "apply_features", isPrimary = true, id = "apply_btn"}
    }, "multiselect_row")
    :separator("sep7")
    
    -- Status display row
    :label("Status Display Row:", "status_row_label")
    :row({
        {type = "label", text = "Connection:", id = "conn_label"},
        {type = "label", text = "✅ Connected", id = "conn_status"},
        {type = "button", text = "Refresh", action = "refresh", id = "refresh_btn"}
    }, "status_row")
    
    :build()

-- Set the UI
mainWindow:setUI(ui)

print("✅ Row Demo window created!")

-- Set up callbacks to demonstrate functionality
print("📝 Setting up callbacks...")

-- Traditional button row callbacks
mainWindow:setCallback("save", function(data)
    print("💾 Save clicked")
    mainWindow:setText("conn_status", "💾 Saved")
end)

mainWindow:setCallback("cancel", function(data)
    print("❌ Cancel clicked")
    mainWindow:setText("conn_status", "❌ Cancelled")
end)

mainWindow:setCallback("help", function(data)
    print("❓ Help clicked")
    mainWindow:setText("conn_status", "❓ Help shown")
end)

-- Mixed row callbacks
mainWindow:setCallback("action_btn", function(data)
    print("🎯 Action button clicked")
    mainWindow:setText("status_label", "Status: Action executed")
end)

mainWindow:setCallback("reset_btn", function(data)
    print("🔄 Reset button clicked")
    mainWindow:setText("status_label", "Status: Reset")
    mainWindow:setValue("volume_slider", 50)
    mainWindow:setValue("level_slider", 5)
    mainWindow:setValue("enable_switch", false)
end)

-- Control row callbacks
mainWindow:setCallback("volume_slider", function(data)
    local value = data.value or 50
    print("🔊 Volume changed to:", value)
    mainWindow:setText("conn_status", "🔊 Volume: " .. value)
end)

mainWindow:setCallback("mode_dropdown", function(data)
    local mode = data.value or "Auto"
    print("⚙️ Mode changed to:", mode)
    mainWindow:setText("conn_status", "⚙️ Mode: " .. mode)
end)

-- Switch row callbacks
mainWindow:setCallback("enable_switch", function(data)
    local enabled = data.value or false
    print("🔄 Enable switch:", enabled and "ON" or "OFF")
    mainWindow:setText("conn_status", enabled and "✅ Enabled" or "❌ Disabled")
end)

mainWindow:setCallback("config_btn", function(data)
    print("⚙️ Configure clicked")
    mainWindow:setText("conn_status", "⚙️ Configuring...")
end)

mainWindow:setCallback("test_btn", function(data)
    print("🧪 Test clicked")
    mainWindow:setText("conn_status", "🧪 Testing...")
end)

-- Complex row callbacks
mainWindow:setCallback("level_slider", function(data)
    local level = data.value or 5
    print("📊 Level changed to:", level)
    -- Update priority dropdown based on level
    local priority = level <= 3 and "Low" or level <= 7 and "Medium" or "High"
    mainWindow:setValue("priority_dropdown", priority)
end)

mainWindow:setCallback("priority_dropdown", function(data)
    local priority = data.value or "Medium"
    print("🎯 Priority changed to:", priority)
end)

mainWindow:setCallback("auto_switch", function(data)
    local auto = data.value or false
    print("🤖 Auto mode:", auto and "ON" or "OFF")
    if auto then
        -- Auto-adjust level based on priority
        local priority = mainWindow:getValue("priority_dropdown") or "Medium"
        local level = priority == "Low" and 2 or priority == "Medium" and 5 or 8
        mainWindow:setValue("level_slider", level)
    end
end)

-- Multiselect row callbacks
mainWindow:setCallback("features_multiselect", function(data)
    local selected = data.values or {}
    print("☑️ Features selected:", json.encode(selected))
    mainWindow:setText("conn_status", "☑️ " .. #selected .. " features selected")
end)

mainWindow:setCallback("apply_btn", function(data)
    local features = mainWindow:getValue("features_multiselect") or {}
    print("✅ Applying features:", json.encode(features))
    mainWindow:setText("conn_status", "✅ Applied " .. #features .. " features")
end)

-- Status row callbacks
mainWindow:setCallback("refresh_btn", function(data)
    print("🔄 Refresh clicked")
    mainWindow:setText("conn_status", "🔄 Refreshing...")
    
    -- Simulate refresh delay
    setTimeout(function()
        mainWindow:setText("conn_status", "✅ Connected")
    end, 1500)
end)

-- Show the window
mainWindow:show()

print("✅ Row Demo window displayed!")
print("📝 Window ID:", mainWindow:getId())

print("\n🎉 Row Demo complete!")
print("💡 Try interacting with the different row types:")
print("   🔘 Button rows for actions")
print("   🎚️ Mixed rows with controls and labels")
print("   🔄 Interactive elements that update each other")
print("   ☑️ Multiselect with apply button")
print("   📊 Status displays that show current state")

-- Keep the script running
setInterval(function()
    -- Could add periodic updates here
end, 5000)
