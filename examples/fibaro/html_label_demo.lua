-- HTML Label Styling Demo - Shows HTML support in labels
-- Demonstrates font styling, colors, and formatting options

local nativeUI = require('native_ui')
local json = require('json')

print("🎨 HTML Label Styling Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Create JSON UI with HTML-styled labels
print("\n📝 Creating HTML styled labels...")

local htmlLabelDemo = json.encode({
    elements = {
        {
            type = "header",
            text = "HTML Label Styling Demo",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "This demo shows HTML styling capabilities in labels",
            id = "description"
        },
        {
            type = "separator",
            id = "sep1"
        },
        
        -- Row 1: Basic HTML formatting
        {
            type = "row",
            id = "basic_html_row",
            elements = {
                {
                    type = "label",
                    text = "<b>Bold</b> and <i>italic</i> text",
                    html = true,
                    id = "basic_html_label"
                },
                {
                    type = "label",
                    text = "<u>Underlined</u> text",
                    html = true,
                    id = "underline_label"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep2"
        },
        
        -- Row 2: Font sizes
        {
            type = "row",
            id = "font_size_row",
            elements = {
                {
                    type = "label",
                    text = "<big>Large Text</big>",
                    html = true,
                    id = "large_text"
                },
                {
                    type = "label",
                    text = "Normal Text",
                    id = "normal_text"
                },
                {
                    type = "label",
                    text = "<small>Small Text</small>",
                    html = true,
                    id = "small_text"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep3"
        },
        
        -- Row 3: Colors
        {
            type = "row",
            id = "color_row",
            elements = {
                {
                    type = "label",
                    text = "<font color=\"red\">Red Text</font>",
                    html = true,
                    id = "red_label"
                },
                {
                    type = "label",
                    text = "<font color=\"blue\">Blue Text</font>",
                    html = true,
                    id = "blue_label"
                },
                {
                    type = "label",
                    text = "<font color=\"green\">Green Text</font>",
                    html = true,
                    id = "green_label"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep4"
        },
        
        -- Row 4: Combined formatting
        {
            type = "label",
            text = "<b><font color=\"blue\">Bold Blue</font></b> and <i><font color=\"red\">Italic Red</font></i>",
            html = true,
            id = "combined_label"
        },
        
        {
            type = "separator",
            id = "sep5"
        },
        
        -- Row 5: Multi-line with breaks
        {
            type = "label",
            text = "<b>Status Report:</b><br><font color=\"green\">✓ System Online</font><br><font color=\"blue\">ℹ Processing...</font>",
            html = true,
            id = "multiline_label"
        },
        
        {
            type = "separator",
            id = "sep6"
        },
        
        -- Row 6: Control buttons to change HTML content
        {
            type = "row",
            id = "control_row",
            elements = {
                {
                    type = "button",
                    text = "Make Bold",
                    action = "make_bold",
                    id = "bold_btn"
                },
                {
                    type = "button",
                    text = "Make Red",
                    action = "make_red",
                    id = "red_btn"
                },
                {
                    type = "button",
                    text = "Make Large",
                    action = "make_large",
                    id = "large_btn"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep7"
        },
        
        -- Dynamic HTML label that will be updated
        {
            type = "label",
            text = "<i>Click buttons above to change this text</i>",
            html = true,
            id = "dynamic_label"
        },
        
        {
            type = "separator",
            id = "sep8"
        },
        
        -- Row 7: Complex example with status display
        {
            type = "row",
            id = "status_row",
            elements = {
                {
                    type = "label",
                    text = "<b>Device Status:</b>",
                    html = true,
                    id = "status_title"
                },
                {
                    type = "label",
                    text = "<font color=\"green\">● ONLINE</font>",
                    html = true,
                    id = "status_indicator"
                }
            }
        },
        
        -- Control to toggle status
        {
            type = "row",
            id = "toggle_row",
            elements = {
                {
                    type = "switch",
                    text = "Device Online",
                    value = true,
                    id = "online_switch"
                },
                {
                    type = "button",
                    text = "Refresh Status",
                    action = "refresh",
                    id = "refresh_btn"
                }
            }
        }
    }
})

-- Create window from JSON
local window = nativeUI.createWindow("HTML Label Demo", 600, 700)
local ui = nativeUI.fromJSON(htmlLabelDemo)
window:setUI(ui)

-- Demo state
local dynamicText = "Dynamic HTML Text"

-- Set up callbacks
print("\n📞 Setting up HTML styling callbacks...")

-- Bold button
window:setCallback("bold_btn", function(data)
    print("🔤 Making text bold")
    dynamicText = "<b>" .. dynamicText .. "</b>"
    window:setText("dynamic_label", dynamicText)
end)

-- Red button
window:setCallback("red_btn", function(data)
    print("🔴 Making text red")
    dynamicText = "<font color=\"red\">" .. dynamicText .. "</font>"
    window:setText("dynamic_label", dynamicText)
end)

-- Large button
window:setCallback("large_btn", function(data)
    print("📏 Making text large")
    dynamicText = "<big>" .. dynamicText .. "</big>"
    window:setText("dynamic_label", dynamicText)
end)

-- Online switch
window:setCallback("online_switch", function(data)
    local isOnline = data.value
    print("🔘 Device online:", isOnline and "YES" or "NO")
    
    if isOnline then
        window:setText("status_indicator", "<font color=\"green\">● ONLINE</font>")
        window:setText("multiline_label", "<b>Status Report:</b><br><font color=\"green\">✓ System Online</font><br><font color=\"blue\">ℹ All systems operational</font>")
    else
        window:setText("status_indicator", "<font color=\"red\">● OFFLINE</font>")
        window:setText("multiline_label", "<b>Status Report:</b><br><font color=\"red\">✗ System Offline</font><br><font color=\"blue\">ℹ Please check connection</font>")
    end
end)

-- Refresh button
window:setCallback("refresh_btn", function(data)
    print("🔄 Refreshing status")
    local isOnline = window:getValue("online_switch")
    local timestamp = os.date("%H:%M:%S")
    
    -- Update with timestamp
    local statusText = isOnline and 
        "<b>Status Report:</b><br><font color=\"green\">✓ System Online</font><br><font color=\"blue\">ℹ Last updated: " .. timestamp .. "</font>" or
        "<b>Status Report:</b><br><font color=\"red\">✗ System Offline</font><br><font color=\"blue\">ℹ Last checked: " .. timestamp .. "</font>"
    
    window:setText("multiline_label", statusText)
end)

-- Show the window
window:show()
print("✅ HTML Label Demo window created!")

-- Set up real-time updates to demonstrate dynamic HTML
print("\n🔄 Setting up real-time HTML updates...")

local updateCount = 0
setInterval(function()
    updateCount = updateCount + 1
    
    -- Update the combined label with animated content
    local colors = {"red", "blue", "green"}
    local color = colors[(updateCount % 3) + 1]
    local animatedText = "<b><font color=\"" .. color .. "\">Animated " .. updateCount .. "</font></b> and <i>regular text</i>"
    
    window:setText("combined_label", animatedText)
    
    -- Flash the title color
    if updateCount % 2 == 0 then
        window:setText("basic_html_label", "<b><font color=\"blue\">Bold</font></b> and <i><font color=\"red\">italic</font></i> text")
    else
        window:setText("basic_html_label", "<b>Bold</b> and <i>italic</i> text")
    end
    
    print("🎨 HTML animation update #" .. updateCount)
end, 2000)

print("\n🎉 HTML Label Demo complete!")
print("\n✨ HTML Features demonstrated:")
print("   🔤 <b>, <strong> - Bold text")
print("   📐 <i>, <em> - Italic text") 
print("   📏 <u> - Underlined text")
print("   📊 <big>, <small> - Font sizes")
print("   🎨 <font color=\"...\"> - Text colors (red, blue, green)")
print("   📄 <br> - Line breaks")
print("   🔄 Dynamic HTML content updates")
print("   🎛️ Mixed HTML and regular labels in rows")
print("\n💡 To enable HTML: Set 'html: true' in label definition!")
print("📋 Supported colors: red, blue, green")
print("📐 Supported tags: b, i, u, strong, em, big, small, font, br")
