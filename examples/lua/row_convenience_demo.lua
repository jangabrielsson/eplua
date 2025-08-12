-- Row Convenience Demo - Shows the convenience methods for common row patterns
-- Demonstrates labelRow, controlRow, actionRow, and the general row method

local nativeUI = require('native_ui')
local json = require('json')

print("🎛️ EPLua Row Convenience Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available on this system")
    return
end

print("✅ Native UI available!")

local mainWindow = nativeUI.createWindow("Row Convenience Demo", 650, 600)

-- Build UI using convenience methods
local ui = nativeUI.quickUI()
    :header("Row Convenience Methods", 1, "main_title")
    :label("This demo shows convenience methods for common row patterns", "description")
    :separator("sep1")
    
    -- labelRow - Multiple labels in a row (great for status displays)
    :label("Label Row (Status Display):", "label_row_title")
    :labelRow({
        "CPU:",
        {text = "45%", id = "cpu_status"},
        "Memory:",
        {text = "2.1GB", id = "memory_status"},
        "Disk:",
        {text = "67%", id = "disk_status"}
    }, "status_row")
    :separator("sep2")
    
    -- controlRow - Controls like sliders, dropdowns, switches
    :label("Control Row (Settings):", "control_row_title")
    :controlRow({
        {type = "slider", text = "Brightness", min = 0, max = 100, value = 80, id = "brightness_slider"},
        {type = "dropdown", text = "Quality", options = {"Low", "Medium", "High", "Ultra"}, value = "High", id = "quality_dropdown"},
        {type = "switch", text = "HDR", value = true, id = "hdr_switch"}
    }, "settings_row")
    :separator("sep3")
    
    -- actionRow - Mix of buttons and switches for actions
    :label("Action Row (Mixed Actions):", "action_row_title")
    :actionRow({
        {type = "button", text = "Start", action = "start", isPrimary = true, id = "start_btn"},
        {type = "switch", text = "Auto-save", value = false, id = "autosave_switch"},
        {type = "button", text = "Stop", action = "stop", id = "stop_btn"},
        {type = "button", text = "Reset", action = "reset", id = "reset_btn"}
    }, "action_controls")
    :separator("sep4")
    
    -- General row - Complete flexibility
    :label("General Row (Mixed Elements):", "general_row_title")
    :row({
        {type = "label", text = "Progress:", id = "progress_label"},
        {type = "slider", min = 0, max = 100, value = 0, id = "progress_slider"},
        {type = "label", text = "0%", id = "progress_percent"},
        {type = "button", text = "Update", action = "update_progress", id = "update_btn"}
    }, "progress_row")
    :separator("sep5")
    
    -- Another example: File operations row
    :label("File Operations Row:", "file_row_title")
    :row({
        {type = "dropdown", text = "File", options = {"document.txt", "image.png", "data.json"}, value = "document.txt", id = "file_dropdown"},
        {type = "button", text = "Open", action = "open_file", id = "open_btn"},
        {type = "button", text = "Save", action = "save_file", isPrimary = true, id = "save_btn"},
        {type = "switch", text = "Backup", value = true, id = "backup_switch"}
    }, "file_operations")
    :separator("sep6")
    
    -- Network settings row
    :label("Network Settings:", "network_title")
    :controlRow({
        {type = "switch", text = "WiFi", value = true, id = "wifi_switch"},
        {type = "dropdown", text = "Network", options = {"Home-WiFi", "Office-5G", "Mobile-Hotspot"}, value = "Home-WiFi", id = "network_dropdown"},
        {type = "slider", text = "Signal", min = 0, max = 100, value = 85, id = "signal_slider"}
    }, "network_settings")
    
    :build()

mainWindow:setUI(ui)

-- Set up interactive callbacks
print("📝 Setting up interactive callbacks...")

-- Status updates
local function updateSystemStatus()
    local cpu = math.random(20, 80)
    local memory = math.random(15, 35) / 10
    local disk = math.random(40, 90)
    
    mainWindow:setText("cpu_status", cpu .. "%")
    mainWindow:setText("memory_status", string.format("%.1fGB", memory))
    mainWindow:setText("disk_status", disk .. "%")
end

-- Settings callbacks
mainWindow:setCallback("brightness_slider", function(data)
    local brightness = data.value or 80
    print("💡 Brightness changed to:", brightness)
end)

mainWindow:setCallback("quality_dropdown", function(data)
    local quality = data.value or "High"
    print("🎨 Quality changed to:", quality)
end)

mainWindow:setCallback("hdr_switch", function(data)
    local hdr = data.value or false
    print("🌈 HDR:", hdr and "ON" or "OFF")
end)

-- Action callbacks
mainWindow:setCallback("start_btn", function(data)
    print("▶️ Start clicked")
    mainWindow:setText("progress_label", "Progress: Running...")
    
    -- Simulate progress
    local progress = 0
    local progressTimer = setInterval(function()
        progress = progress + math.random(5, 15)
        if progress >= 100 then
            progress = 100
            clearInterval(progressTimer)
            mainWindow:setText("progress_label", "Progress: Complete!")
        end
        mainWindow:setValue("progress_slider", progress)
        mainWindow:setText("progress_percent", progress .. "%")
    end, 500)
end)

mainWindow:setCallback("stop_btn", function(data)
    print("⏹️ Stop clicked")
    mainWindow:setText("progress_label", "Progress: Stopped")
end)

mainWindow:setCallback("reset_btn", function(data)
    print("🔄 Reset clicked")
    mainWindow:setValue("progress_slider", 0)
    mainWindow:setText("progress_percent", "0%")
    mainWindow:setText("progress_label", "Progress:")
    mainWindow:setValue("brightness_slider", 80)
    mainWindow:setValue("quality_dropdown", "High")
    mainWindow:setValue("hdr_switch", true)
end)

mainWindow:setCallback("autosave_switch", function(data)
    local autosave = data.value or false
    print("💾 Auto-save:", autosave and "ENABLED" or "DISABLED")
end)

-- Progress update callback
mainWindow:setCallback("update_btn", function(data)
    local currentProgress = mainWindow:getValue("progress_slider") or 0
    local newProgress = math.min(100, currentProgress + math.random(10, 30))
    mainWindow:setValue("progress_slider", newProgress)
    mainWindow:setText("progress_percent", newProgress .. "%")
    print("📊 Progress updated to:", newProgress .. "%")
end)

-- File operations
mainWindow:setCallback("file_dropdown", function(data)
    local file = data.value or "document.txt"
    print("📄 File selected:", file)
end)

mainWindow:setCallback("open_btn", function(data)
    local file = mainWindow:getValue("file_dropdown") or "document.txt"
    print("📂 Opening file:", file)
end)

mainWindow:setCallback("save_btn", function(data)
    local file = mainWindow:getValue("file_dropdown") or "document.txt"
    local backup = mainWindow:getValue("backup_switch") or false
    print("💾 Saving file:", file, backup and "(with backup)" or "(no backup)")
end)

mainWindow:setCallback("backup_switch", function(data)
    local backup = data.value or false
    print("🗃️ Backup:", backup and "ENABLED" or "DISABLED")
end)

-- Network settings
mainWindow:setCallback("wifi_switch", function(data)
    local wifi = data.value or false
    print("📶 WiFi:", wifi and "ON" or "OFF")
    if not wifi then
        mainWindow:setValue("signal_slider", 0)
    else
        mainWindow:setValue("signal_slider", math.random(60, 100))
    end
end)

mainWindow:setCallback("network_dropdown", function(data)
    local network = data.value or "Home-WiFi"
    print("🌐 Network changed to:", network)
    -- Simulate different signal strengths for different networks
    local signal = network == "Home-WiFi" and 85 or network == "Office-5G" and 95 or 45
    mainWindow:setValue("signal_slider", signal)
end)

mainWindow:setCallback("signal_slider", function(data)
    local signal = data.value or 0
    print("📡 Signal strength:", signal .. "%")
end)

-- Show the window
mainWindow:show()

-- Start periodic status updates
setInterval(updateSystemStatus, 3000)
updateSystemStatus() -- Initial update

print("✅ Row Convenience Demo window displayed!")
print("📝 Window ID:", mainWindow:getId())

print("\n🎉 Row Convenience Demo complete!")
print("💡 This demo shows:")
print("   📊 labelRow() - For status displays with multiple labels")
print("   🎛️ controlRow() - For settings with sliders, dropdowns, switches")
print("   🎯 actionRow() - For mixed buttons and toggle switches")
print("   🔧 row() - For complete flexibility with any element types")
print("\n🔄 Try interacting with the controls to see them work together!")

-- Keep the script running
setInterval(function()
    -- Periodic updates handled above
end, 10000)
