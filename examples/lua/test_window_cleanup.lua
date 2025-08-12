-- Test script for window cleanup
-- This script creates a window but doesn't have an infinite loop

local nativeUI = require('native_ui')

print("🧪 Testing window cleanup...")

-- Check if native UI is available
if not nativeUI.isAvailable() then
    print("❌ Native UI not available on this system")
    return
end

print("✅ Native UI available!")

-- Create the main window
print("📝 Creating test window...")

local mainWindow = nativeUI.createWindow("Test Window Cleanup", 400, 300)

-- Build simple UI
local ui = nativeUI.quickUI()
    :label("Test Window", "title")
    :label("This window should close when the script finishes", "description")
    :button("Close Window", "close_btn", false, "close_button")
    :build()

-- Set the UI
mainWindow:setUI(ui)

-- Setup callback
mainWindow:setCallback("close_button", function(data)
    print("🔘 Close button pressed!")
    mainWindow:close()
end)

-- Show the window
mainWindow:show()

print("✅ Test window created and displayed!")
print("📝 Window ID:", mainWindow:getId())

-- Wait a bit to show the window
print("⏳ Waiting 3 seconds...")
setTimeout(function()
    print("✅ Test completed - window should close automatically")
    mainWindow:close()
end, 3000)

print("🎉 Test script finished!") 