-- Fixed HTML Label Sizing Demo
-- Tests the corrected auto-sizing functionality

local nativeUI = require('native_ui')
local json = require('json')

print("🔧 Fixed HTML Label Sizing Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Create JSON UI demonstrating FIXED sizing
print("\n📝 Creating labels to test FIXED sizing...")

local fixedSizingDemo = json.encode({
    elements = {
        {
            type = "header",
            text = "Fixed HTML Label Sizing Test",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "Testing the corrected auto-sizing HTML labels (no more hardcoded height=1, width=30)",
            id = "description"
        },
        {
            type = "separator",
            id = "sep1"
        },
        
        -- Test 1: Large text should NOT be clipped anymore
        {
            type = "label",
            text = "Test 1: Large text (should be fully visible now)",
            id = "test1_title"
        },
        {
            type = "label",
            text = "<big><b>This large bold text should be fully visible and not cut in half!</b></big>",
            html = true,
            id = "large_text_fixed"
        },
        
        {
            type = "separator",
            id = "sep2"
        },
        
        -- Test 2: Multi-line text should work properly
        {
            type = "label",
            text = "Test 2: Multi-line text (all lines should be visible)",
            id = "test2_title"
        },
        {
            type = "label",
            text = "<b>Line 1: Title</b><br><i>Line 2: Subtitle in italic</i><br><font color=\"red\">Line 3: Red warning text</font><br><small>Line 4: Small details text</small>",
            html = true,
            id = "multiline_text_fixed"
        },
        
        {
            type = "separator",
            id = "sep3"
        },
        
        -- Test 3: Long text should wrap properly without fixed width constraints
        {
            type = "label",
            text = "Test 3: Long text wrapping (should wrap naturally)",
            id = "test3_title"
        },
        {
            type = "label",
            text = "<b>This is a very long line of text that should wrap naturally without being constrained by a hardcoded width of 30 characters, allowing for proper text flow and readability.</b>",
            html = true,
            id = "long_text_fixed"
        },
        
        {
            type = "separator",
            id = "sep4"
        },
        
        -- Test 4: Mixed font sizes in a row
        {
            type = "label",
            text = "Test 4: Mixed font sizes (all should be properly sized)",
            id = "test4_title"
        },
        {
            type = "row",
            id = "font_size_row_fixed",
            elements = {
                {
                    type = "label",
                    text = "<small>Small text</small>",
                    html = true,
                    id = "small_text_fixed"
                },
                {
                    type = "label",
                    text = "Normal text",
                    id = "normal_text_fixed"
                },
                {
                    type = "label",
                    text = "<big>Big text (not clipped!)</big>",
                    html = true,
                    id = "big_text_fixed"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep5"
        },
        
        -- Test 5: Complex multi-line content with centering
        {
            type = "label",
            text = "Test 5: Complex content (all formatting should be visible)",
            id = "test5_title"
        },
        {
            type = "label",
            text = "<center><big><b>Centered Large Title</b></big></center><br><font color=\"blue\">Blue subtitle line</font><br><small>Small details line</small><br><font color=\"red\">Red error message line</font><br><i>Italic conclusion line</i>",
            html = true,
            id = "complex_multiline_fixed"
        },
        
        {
            type = "separator",
            id = "sep6"
        },
        
        -- Test 6: Dynamic content updates
        {
            type = "label",
            text = "Test 6: Dynamic content updates (should resize properly)",
            id = "test6_title"
        },
        {
            type = "button",
            text = "Update Dynamic Content",
            action = "update_dynamic",
            id = "update_btn"
        },
        {
            type = "label",
            text = "<b>Initial content</b>",
            html = true,
            id = "dynamic_content_fixed"
        },
        
        {
            type = "separator",
            id = "sep7"
        },
        
        -- Test 7: Color variety
        {
            type = "label",
            text = "Test 7: Color support",
            id = "test7_title"
        },
        {
            type = "label",
            text = "<font color=\"red\">Red</font> <font color=\"blue\">Blue</font> <font color=\"green\">Green</font> text with colors",
            html = true,
            id = "color_text"
        }
    }
})

-- Create window from JSON
local window = nativeUI.createWindow("Fixed Sizing Demo", 800, 700)
local ui = nativeUI.fromJSON(fixedSizingDemo)
window:setUI(ui)

-- Set up callback for dynamic content updates
window:setCallback("update_btn", function(data)
    print("🔄 Testing dynamic content updates with auto-sizing")
    
    local updateCount = (window._updateCount or 0) + 1
    window._updateCount = updateCount
    
    if updateCount == 1 then
        window:setText("dynamic_content_fixed", "<big><b>Updated with large content</b></big><br><font color=\"green\">✓ This should auto-size properly</font>")
    elseif updateCount == 2 then
        window:setText("dynamic_content_fixed", "<center><big><b>Multi-line Update</b></big></center><br><font color=\"blue\">Line 2</font><br><font color=\"red\">Line 3</font><br><small>Line 4</small><br><i>Line 5 - All lines should be visible!</i>")
    elseif updateCount == 3 then
        window:setText("dynamic_content_fixed", "<b>Complex status report:</b><br><font color=\"green\">✓ System online and running</font><br><font color=\"blue\">ℹ Processing data successfully</font><br><font color=\"red\">⚠ Warning: High memory usage detected</font><br><small>📊 Performance metrics: CPU 45%, RAM 78%</small><br><i>Last updated: " .. os.date("%H:%M:%S") .. "</i>")
    else
        window:setText("dynamic_content_fixed", "<b>Reset to simple content</b><br><small>Click again to cycle through tests</small>")
        window._updateCount = 0
    end
end)

-- Show the window
window:show()
print("✅ Fixed Sizing Demo window created!")

print("\n🎯 Expected results (if fixes work correctly):")
print("   ✅ Large text should be fully visible (not clipped)")
print("   ✅ All lines in multi-line text should be shown")
print("   ✅ Long text should wrap naturally")
print("   ✅ Font size variations should display properly")
print("   ✅ Complex content should be fully rendered")
print("   ✅ Dynamic updates should resize correctly")

print("\n🔧 Fixed issues:")
print("   📏 Removed hardcoded height=1, width=30")
print("   🎯 Added auto-sizing based on content")
print("   📐 Proper line counting and width calculation")
print("   🔄 Dynamic resize on content updates")

-- Keep the script running so GUI stays open
print("\n⏰ GUI will stay open - Press Ctrl+C to exit")
setInterval(function()
    -- Keep the script alive so GUI stays open
end, 1000)
