-- Hybrid UI Demo - Better Labels + Native Widgets
-- Tests the hybrid approach: improved label rendering with native interactive elements

local nativeUI = require('native_ui')
local json = require('json')

print("🔧 Hybrid UI Approach Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Create JSON UI definition that tests the problematic cases
print("\n📝 Creating Hybrid UI from JSON...")

local hybridUIJSON = json.encode({
    elements = {
        {
            type = "header",
            text = "🔧 Hybrid UI Approach Test",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "<big><b>This large bold text should be fully visible and not cut in half!</b></big>",
            id = "big_text_test"
        },
        {
            type = "separator",
            id = "sep1"
        },
        {
            type = "label",
            text = "<b>Line 1: Title</b><br><i>Line 2: Subtitle in italic</i><br><font color='red'>Line 3: Red warning text</font><br><small>Line 4: Small details text</small>",
            id = "multiline_test"
        },
        {
            type = "separator",
            id = "sep2"
        },
        {
            type = "label",
            text = "This is a very long line of text that should wrap naturally without being constrained by hardcoded width limits, allowing for proper text flow and readability across multiple lines.",
            id = "long_text_test"
        },
        {
            type = "separator",
            id = "sep3"
        },
        -- Row with mixed font sizes (the problematic Test 4 from our previous demo)
        {
            type = "row",
            elements = {
                {
                    type = "label",
                    text = "<small>Small text</small>",
                    id = "small_in_row"
                },
                {
                    type = "label",
                    text = "Normal text",
                    id = "normal_in_row"
                },
                {
                    type = "label",
                    text = "<big><b>Big text (not clipped!)</b></big>",
                    id = "big_in_row"
                }
              }
        },
        {
            type = "separator",
            id = "sep4"
        },
        -- Interactive elements - these should work perfectly with native widgets
        {
            type = "label",
            text = "<b>Interactive Elements (Native Widgets):</b>",
            id = "interactive_header"
        },
        {
            type = "button",
            text = "Test Button",
            action = "test_button",
            style = { primary = true },
            id = "test_btn"
        },
        {
            type = "dropdown",
            text = "Mode Selection",
            options = {"Auto", "Manual", "Off", "Debug"},
            value = "Auto",
            id = "mode_dropdown"
        },
        {
            type = "slider",
            text = "Volume Level",
            min = 0,
            max = 100,
            value = 75,
            id = "volume_slider"
        },
        {
            type = "multiselect",
            text = "Feature Options",
            options = {"Feature A", "Feature B", "Feature C", "Debug Mode", "Advanced Settings"},
            values = {"Feature A", "Feature C"},
            height = 4,
            id = "features_multi"
        },
        {
            type = "separator",
            id = "sep5"
        },
        -- Status area with complex formatting
        {
            type = "label",
            text = "<center><big><b>Hybrid Approach Results</b></big></center><br><font color='green'>✅ Better label rendering</font><br><font color='blue'>✅ Native interactive widgets</font><br>✅ No JavaScript required<br>✅ Cross-platform compatible",
            id = "status_area"
        },
        -- Dynamic update test
        {
            type = "label",
            text = "<b>Dynamic Updates:</b> Ready",
            id = "dynamic_status"
        }
    }
})

-- Create window from JSON
local hybridWindow = nativeUI.createWindow("Hybrid UI Demo", 500, 700)
local ui = nativeUI.fromJSON(hybridUIJSON)
hybridWindow:setUI(ui)

-- Set up interactivity to test that all functionality still works
print("🎛️ Setting up interactive callbacks...")

-- Button callback
hybridWindow:setCallback("test_btn", function(data)
    print("🔘 Test button clicked!")
    
    -- Update button text to show it was clicked
    hybridWindow:setText("test_btn", "Clicked! ✓")
    
    -- Update status with complex formatting
    hybridWindow:setText("dynamic_status", "<b>Dynamic Updates:</b> <font color='green'>Button clicked at " .. os.date("%H:%M:%S") .. "</font>")
    
    -- Reset button text after 2 seconds
    setTimeout(function()
        hybridWindow:setText("test_btn", "Test Button")
    end, 2000)
end)

-- Dropdown callback
hybridWindow:setCallback("mode_dropdown", function(data)
    local mode = data.value or "Unknown"
    print("⚙️ Mode changed to:", mode)
    
    -- Update status with the selected mode
    hybridWindow:setText("dynamic_status", "<b>Dynamic Updates:</b> <font color='blue'>Mode set to " .. mode .. "</font>")
end)

-- Slider callback
hybridWindow:setCallback("volume_slider", function(data)
    local volume = data.value or 0
    print("🎚️ Volume changed to:", volume)
    
    -- Update status with volume level
    local color = volume > 80 and "red" or (volume > 50 and "orange" or "green")
    hybridWindow:setText("dynamic_status", "<b>Dynamic Updates:</b> <font color='" .. color .. "'>Volume: " .. volume .. "%</font>")
end)

-- Multiselect callback
hybridWindow:setCallback("features_multi", function(data)
    local selected = data.values or {}
    print("☑️ Features selected:", json.encode(selected))
    
    local count = #selected
    local color = count > 3 and "orange" or "green"
    hybridWindow:setText("dynamic_status", "<b>Dynamic Updates:</b> <font color='" .. color .. "'>" .. count .. " features selected</font>")
end)

hybridWindow:show()
print("✅ Hybrid UI Demo created!")

-- Set up real-time updates to test dynamic text rendering
print("\n🔄 Setting up real-time updates...")

local updateCount = 0
setInterval(function()
    updateCount = updateCount + 1
    local timestamp = os.date("%H:%M:%S")
    
    -- Update the title with a counter
    hybridWindow:setText("title", "🔧 Hybrid UI Test (Updates: " .. updateCount .. ")")
    
    -- Cycle through different text examples every few updates
    if updateCount % 4 == 1 then
        hybridWindow:setText("big_text_test", "<big><b>Large text update #" .. updateCount .. " - fully visible!</b></big>")
    elseif updateCount % 4 == 2 then
        hybridWindow:setText("multiline_test", "<b>Dynamic Line 1: " .. timestamp .. "</b><br><i>Dynamic Line 2: Update " .. updateCount .. "</i><br><font color='green'>Dynamic Line 3: Success!</font><br><small>Dynamic Line 4: All working</small>")
    elseif updateCount % 4 == 3 then
        hybridWindow:setText("long_text_test", "This is update #" .. updateCount .. " with a very long line of text that should wrap naturally and demonstrate that our hybrid approach handles dynamic text updates without clipping or layout issues, even with lengthy content that spans multiple lines.")
    else
        -- Test the row elements
        hybridWindow:setText("small_in_row", "<small>Small #" .. updateCount .. "</small>")
        hybridWindow:setText("normal_in_row", "Normal #" .. updateCount)
        hybridWindow:setText("big_in_row", "<big><b>Big #" .. updateCount .. "</b></big>")
    end
    
    print("🔄 Update #" .. updateCount .. " at " .. timestamp)
end, 3000)

print("\n📋 Window created with ID:", hybridWindow:getId())
print("🎉 Hybrid UI Demo complete!")
print("\n✨ Key Features Being Tested:")
print("   📝 Better label rendering (no clipping)")
print("   🔤 HTML formatting: <big>, <small>, <b>, <i>, <font color=''>")
print("   📐 Multi-line text with <br> tags")
print("   📏 Long text wrapping")
print("   🎛️ Native interactive widgets (dropdown, multiselect, slider, button)")
print("   📞 Full callback functionality")
print("   🔄 Dynamic text updates")
print("   🎯 Mixed font sizes in rows")
print("\n💡 This hybrid approach should solve all the clipping issues!")
print("⏰ Watch for real-time updates every 3 seconds...")

-- Keep the demo alive
setInterval(function() end, 60000)
