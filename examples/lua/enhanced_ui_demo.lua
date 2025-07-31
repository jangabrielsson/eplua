-- Enhanced Native UI Demo with JSON format and ID management
-- Demonstrates dynamic UI building with proper ID handling and element updates

local nativeUI = require('native_ui')
local json = require('json')

print("🎛️ Enhanced Native UI Demo - JSON & ID Management")

-- Check if native UI is available
if not nativeUI.isAvailable() then
    print("❌ Native UI not available on this system")
    return
end

print("✅ Native UI available!")

-- Example 1: JSON format specification
print("\n📝 Example 1: Creating window from JSON format...")

local jsonUI = [[{
    "elements": [
        {
            "type": "header",
            "text": "JSON-Defined QuickApp",
            "level": 1,
            "id": "main_title"
        },
        {
            "type": "label", 
            "text": "Status: Initializing...",
            "id": "status_label"
        },
        {
            "type": "separator",
            "id": "sep1"
        },
        {
            "type": "label",
            "text": "Counter: 0",
            "id": "counter_display"
        },
        {
            "type": "button",
            "text": "Increment",
            "action": "increment",
            "style": {"primary": true},
            "id": "increment_btn"
        },
        {
            "type": "button",
            "text": "Reset",
            "action": "reset",
            "id": "reset_btn"
        },
        {
            "type": "slider",
            "text": "Value",
            "min": 0,
            "max": 100,
            "value": 25,
            "id": "value_slider"
        }
    ]
}]]

local jsonWindow = nativeUI.createWindow("JSON UI Demo", 400, 300)
local ui = nativeUI.fromJSON(jsonUI)
jsonWindow:setUI(ui)

-- Set up interactivity with proper ID references
local counter = 0

-- Update status after window is ready
jsonWindow:setText("status_label", "Status: Ready ✅")

-- Increment button callback
jsonWindow:setCallback("increment_btn", function(data)
    counter = counter + 1
    jsonWindow:setText("counter_display", "Counter: " .. counter)
    print("📈 Counter incremented to:", counter)
end)

-- Reset button callback
jsonWindow:setCallback("reset_btn", function(data)
    counter = 0
    jsonWindow:setText("counter_display", "Counter: " .. counter)
    jsonWindow:setValue("value_slider", 0)
    print("🔄 Counter reset to 0")
end)

-- Slider callback
jsonWindow:setCallback("value_slider", function(data)
    local value = data.value or 0
    print("🎚️ Slider value changed to:", value)
    -- Update some other element based on slider
    jsonWindow:setText("status_label", "Status: Value = " .. value)
end)

jsonWindow:show()

print("✅ JSON window created with ID management!")
print("📝 Window ID:", jsonWindow:getId())

-- Example 2: Builder with custom IDs
print("\n📝 Example 2: Builder with custom IDs...")

local builderWindow = nativeUI.createWindow("Builder with IDs", 450, 350)

local ui2 = nativeUI.quickUI()
    :header("Smart Control Panel", 1, "control_title")
    :label("Device: Offline", "device_status")
    :separator("sep_main")
    :button("Connect", "connect", true, "connect_btn")
    :button("Disconnect", "disconnect", false, "disconnect_btn")
    :separator("sep_controls")
    :slider("Brightness", 0, 100, 50, "brightness_slider")
    :switch("Auto Mode", false, "auto_switch")
    :dropdown("Profile", {"Home", "Away", "Sleep"}, "Home", "profile_select")
    :build()

builderWindow:setUI(ui2)

-- Device connection simulation
local isConnected = false

builderWindow:setCallback("connect_btn", function(data)
    if not isConnected then
        isConnected = true
        builderWindow:setText("device_status", "Device: Connected ✅")
        builderWindow:setText("connect_btn", "Connecting...")
        
        -- Simulate connection delay
        setTimeout(function()
            builderWindow:setText("connect_btn", "Connected")
            builderWindow:updateElement("connect_btn", "enabled", false)
            builderWindow:updateElement("disconnect_btn", "enabled", true)
            print("🔗 Device connected successfully")
        end, 1500)
    end
end)

builderWindow:setCallback("disconnect_btn", function(data)
    if isConnected then
        isConnected = false
        builderWindow:setText("device_status", "Device: Offline ❌")
        builderWindow:setText("connect_btn", "Connect")
        builderWindow:updateElement("connect_btn", "enabled", true)
        builderWindow:updateElement("disconnect_btn", "enabled", false)
        print("🔌 Device disconnected")
    end
end)

builderWindow:setCallback("brightness_slider", function(data)
    local brightness = data.value or 0
    if isConnected then
        print("💡 Brightness set to:", brightness .. "%")
        builderWindow:setText("device_status", "Device: Connected ✅ (Brightness: " .. brightness .. "%)")
    else
        print("⚠️ Cannot set brightness - device not connected")
    end
end)

builderWindow:setCallback("auto_switch", function(data)
    local enabled = data.value
    print("🤖 Auto mode:", enabled and "ON" or "OFF")
    if enabled then
        builderWindow:setText("device_status", "Device: Auto Mode 🤖")
    end
end)

builderWindow:setCallback("profile_select", function(data)
    local profile = data.value
    print("👤 Profile changed to:", profile)
    -- Update other elements based on profile
    if profile == "Sleep" then
        builderWindow:setValue("brightness_slider", 10)
        builderWindow:setValue("auto_switch", true)
    elseif profile == "Away" then
        builderWindow:setValue("brightness_slider", 0)
        builderWindow:setValue("auto_switch", false)
    else -- Home
        builderWindow:setValue("brightness_slider", 75)
        builderWindow:setValue("auto_switch", true)
    end
end)

builderWindow:show()

print("✅ Builder window created with custom IDs!")

-- Example 3: Dynamic UI updates
print("\n📝 Example 3: Real-time updates...")

-- Update displays every 2 seconds
local updateCounter = 0
setInterval(function()
    updateCounter = updateCounter + 1
    
    -- Update JSON window
    local timestamp = os.date("%H:%M:%S")
    jsonWindow:setText("status_label", "Status: Updated at " .. timestamp)
    
    -- Update builder window if connected
    if isConnected then
        builderWindow:setText("device_status", "Device: Connected ✅ (Updates: " .. updateCounter .. ")")
    end
    
    print("🔄 UI updated #" .. updateCounter .. " at " .. timestamp)
end, 2000)

-- Show all windows
print("\n📋 Current windows:")
print(nativeUI.listWindows())

print("\n🎉 Enhanced Native UI Demo complete!")
print("✨ Features demonstrated:")
print("   🎯 JSON format UI specification")
print("   🏷️ Custom element IDs")
print("   🔄 Real-time element updates")
print("   📞 Callback handling with element identification")
print("   🎛️ Dynamic UI interaction")
print("\n💡 Try interacting with the windows to see callbacks and updates!")
