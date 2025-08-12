-- HTML Label Alignment Demo - Shows HTML alignment support
-- Demonstrates text alignment: left, center, right + all other HTML features

local nativeUI = require('native_ui')
local json = require('json')

print("📐 HTML Label Alignment Demo")

if not nativeUI.isAvailable() then
    print("❌ Native UI not available")
    return
end

print("✅ Native UI available!")

-- Create JSON UI with HTML alignment examples
print("\n📝 Creating HTML alignment examples...")

local alignmentDemo = json.encode({
    elements = {
        {
            type = "header",
            text = "HTML Alignment & Styling Demo",
            level = 1,
            id = "title"
        },
        {
            type = "label",
            text = "This demo shows text alignment and styling options",
            id = "description"
        },
        {
            type = "separator",
            id = "sep1"
        },
        
        -- Alignment examples
        {
            type = "label",
            text = "<b>Text Alignment Examples:</b>",
            html = true,
            id = "alignment_title"
        },
        
        {
            type = "label",
            text = "<left>This text is left-aligned (default)</left>",
            html = true,
            id = "left_example"
        },
        
        {
            type = "label",
            text = "<center><b>This text is centered and bold</b></center>",
            html = true,
            id = "center_example"
        },
        
        {
            type = "label",
            text = "<right><i>This text is right-aligned and italic</i></right>",
            html = true,
            id = "right_example"
        },
        
        {
            type = "separator",
            id = "sep2"
        },
        
        -- Complex alignment with colors
        {
            type = "label",
            text = "<b>Alignment + Colors:</b>",
            html = true,
            id = "color_title"
        },
        
        {
            type = "label",
            text = "<center><font color=\"red\">Centered Red Text</font></center>",
            html = true,
            id = "center_red"
        },
        
        {
            type = "label",
            text = "<right><font color=\"blue\"><big>Right-aligned Large Blue</big></font></right>",
            html = true,
            id = "right_blue"
        },
        
        {
            type = "separator",
            id = "sep3"
        },
        
        -- Multi-line alignment
        {
            type = "label",
            text = "<b>Multi-line Alignment:</b>",
            html = true,
            id = "multiline_title"
        },
        
        {
            type = "label",
            text = "<center><b>Header Text</b><br><small>Subtitle underneath</small><br><font color=\"green\">Status: OK</font></center>",
            html = true,
            id = "multiline_center"
        },
        
        {
            type = "separator",
            id = "sep4"
        },
        
        -- Control buttons for dynamic alignment
        {
            type = "row",
            id = "control_row",
            elements = {
                {
                    type = "button",
                    text = "Left Align",
                    action = "align_left",
                    id = "left_btn"
                },
                {
                    type = "button",
                    text = "Center",
                    action = "align_center",
                    id = "center_btn"
                },
                {
                    type = "button",
                    text = "Right Align",
                    action = "align_right",
                    id = "right_btn"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep5"
        },
        
        -- Dynamic label that will change alignment
        {
            type = "label",
            text = "<center><b>Dynamic Text</b><br><i>Click buttons above to change alignment</i></center>",
            html = true,
            id = "dynamic_label"
        },
        
        {
            type = "separator",
            id = "sep6"
        },
        
        -- Style controls
        {
            type = "row",
            id = "style_row",
            elements = {
                {
                    type = "button",
                    text = "Make Bold",
                    action = "make_bold",
                    id = "bold_btn"
                },
                {
                    type = "button",
                    text = "Add Color",
                    action = "add_color",
                    id = "color_btn"
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
        
        -- Status display with alignment
        {
            type = "row",
            id = "status_row",
            elements = {
                {
                    type = "label",
                    text = "<left><b>Status:</b></left>",
                    html = true,
                    id = "status_left"
                },
                {
                    type = "label",
                    text = "<center><font color=\"green\">● ACTIVE</font></center>",
                    html = true,
                    id = "status_center"
                },
                {
                    type = "label",
                    text = "<right><small>12:34:56</small></right>",
                    html = true,
                    id = "status_right"
                }
            }
        },
        
        {
            type = "separator",
            id = "sep8"
        },
        
        -- Comprehensive example
        {
            type = "label",
            text = "<center><big><b>Complete Example</b></big><br><font color=\"blue\">Centered, Large, Bold, Blue</font><br><small><i>with small italic subtitle</i></small></center>",
            html = true,
            id = "comprehensive_example"
        }
    }
})

-- Create window from JSON
local window = nativeUI.createWindow("HTML Alignment Demo", 650, 800)
local ui = nativeUI.fromJSON(alignmentDemo)
window:setUI(ui)

-- Demo state
local currentText = "Dynamic Text"
local currentAlignment = "center"

-- Set up callbacks
print("\n📞 Setting up alignment callbacks...")

-- Alignment buttons
window:setCallback("left_btn", function(data)
    print("◀️ Setting left alignment")
    currentAlignment = "left"
    local newText = "<" .. currentAlignment .. "><b>" .. currentText .. "</b><br><i>Now left-aligned</i></" .. currentAlignment .. ">"
    window:setText("dynamic_label", newText)
end)

window:setCallback("center_btn", function(data)
    print("🎯 Setting center alignment")
    currentAlignment = "center"
    local newText = "<" .. currentAlignment .. "><b>" .. currentText .. "</b><br><i>Now centered</i></" .. currentAlignment .. ">"
    window:setText("dynamic_label", newText)
end)

window:setCallback("right_btn", function(data)
    print("▶️ Setting right alignment")
    currentAlignment = "right"
    local newText = "<" .. currentAlignment .. "><b>" .. currentText .. "</b><br><i>Now right-aligned</i></" .. currentAlignment .. ">"
    window:setText("dynamic_label", newText)
end)

-- Style buttons
window:setCallback("bold_btn", function(data)
    print("🔤 Adding bold styling")
    currentText = "Bold " .. currentText
    local newText = "<" .. currentAlignment .. "><b>" .. currentText .. "</b><br><i>Bold styling added</i></" .. currentAlignment .. ">"
    window:setText("dynamic_label", newText)
end)

window:setCallback("color_btn", function(data)
    print("🎨 Adding color styling")
    local colors = {"red", "blue", "green"}
    local color = colors[math.random(#colors)]
    currentText = "Colored " .. currentText
    local newText = "<" .. currentAlignment .. "><b><font color=\"" .. color .. "\">" .. currentText .. "</font></b><br><i>Color: " .. color .. "</i></" .. currentAlignment .. ">"
    window:setText("dynamic_label", newText)
end)

window:setCallback("large_btn", function(data)
    print("📏 Adding large size styling")
    currentText = "Large " .. currentText
    local newText = "<" .. currentAlignment .. "><big><b>" .. currentText .. "</b></big><br><i>Large size added</i></" .. currentAlignment .. ">"
    window:setText("dynamic_label", newText)
end)

-- Show the window
window:show()
print("✅ HTML Alignment Demo window created!")

-- Set up real-time updates
print("\n🔄 Setting up real-time alignment updates...")

local updateCount = 0
setInterval(function()
    updateCount = updateCount + 1
    local timestamp = os.date("%H:%M:%S")
    
    -- Update the status time display (right-aligned)
    window:setText("status_right", "<right><small>" .. timestamp .. "</small></right>")
    
    -- Cycle through different status colors
    local colors = {"green", "blue", "red"}
    local statuses = {"● ACTIVE", "● PROCESSING", "● STANDBY"}
    local index = (updateCount % 3) + 1
    
    window:setText("status_center", "<center><font color=\"" .. colors[index] .. "\">" .. statuses[index] .. "</font></center>")
    
    -- Update comprehensive example with cycling alignment
    local alignments = {"left", "center", "right"}
    local align = alignments[(updateCount % 3) + 1]
    local alignText = "<" .. align .. "><big><b>Complete Example</b></big><br><font color=\"blue\">" .. align:upper() .. " aligned, Large, Bold, Blue</font><br><small><i>Update #" .. updateCount .. "</i></small></" .. align .. ">"
    
    window:setText("comprehensive_example", alignText)
    
    print("📐 Alignment animation update #" .. updateCount .. " (" .. align .. ")")
end, 3000)

print("\n🎉 HTML Alignment Demo complete!")
print("\n✨ HTML Alignment Features:")
print("   ◀️ <left>...</left> - Left-aligned text")
print("   🎯 <center>...</center> - Centered text")  
print("   ▶️ <right>...</right> - Right-aligned text")
print("   🎨 Combined with colors: <center><font color=\"red\">...</font></center>")
print("   📏 Combined with sizes: <right><big>...</big></right>")
print("   🔤 Combined with styles: <center><b><i>...</i></b></center>")
print("\n💡 All HTML features work together:")
print("   📄 <br> - Line breaks within aligned blocks")
print("   🎨 <font color=\"...\"> - Colors: red, blue, green")
print("   📐 <b>, <i>, <u>, <big>, <small> - Text formatting")
print("   📋 Nested tags: <center><b><font color=\"red\">text</font></b></center>")
print("\n🔧 To use: Set 'html: true' in your label definition!")
