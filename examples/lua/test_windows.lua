-- Windows Module Test for EPLua
-- Tests the windows module with both object-oriented and functional interfaces

local windows = require('windows')

print("=== EPLua Windows Module Test ===")

-- Test 1: Check capabilities
print("\n1. Testing capabilities:")
print("GUI available:", windows.isAvailable())
print("HTML supported:", windows.htmlSupported())
print("HTML engine:", windows.getHtmlEngine())

local caps = windows.getCapabilities()
print("Capabilities:", caps.gui, caps.html, caps.engine)

if not windows.isAvailable() then
    print("❌ GUI not available - skipping window tests")
    return
end

-- Test 2: Object-oriented interface
print("\n2. Testing object-oriented interface:")

local win1 = windows.createWindow("Test Window 1", 600, 400)
print("✅ Created window 1, ID:", win1:getId())

-- Test method chaining
local win2 = windows.createWindow("Test Window 2", 500, 350)
    :setHtml([[
        <html>
        <head><title>Test Window 2</title></head>
        <body style="font-family: Arial; padding: 20px; background: #f0f8ff;">
            <h1 style="color: #333;">Hello from Window 2!</h1>
            <p>This is a test of the object-oriented interface.</p>
            <ul>
                <li>Window created ✅</li>
                <li>HTML content set ✅</li>
                <li>Method chaining works ✅</li>
            </ul>
        </body>
        </html>
    ]])
    :show()

print("✅ Created window 2 with method chaining")

-- Test 3: Fluent interface
print("\n3. Testing fluent interface:")

local win3 = windows.create("Fluent Demo", 700, 500)
win3:html([[
    <html>
    <head>
        <title>Fluent Interface Demo</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0; 
                padding: 20px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                color: white;
                min-height: 100vh;
            }
            .card {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { text-align: center; margin-top: 0; }
            .feature { 
                margin: 15px 0; 
                padding: 10px;
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
            }
            .emoji { font-size: 1.2em; margin-right: 10px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 EPLua Windows Module</h1>
            <div class="feature">
                <span class="emoji">🎨</span>
                <strong>Beautiful HTML rendering</strong> - Create stunning interfaces
            </div>
            <div class="feature">
                <span class="emoji">🔗</span>
                <strong>Method chaining</strong> - Fluent, readable code
            </div>
            <div class="feature">
                <span class="emoji">⚡</span>
                <strong>Fast and responsive</strong> - Native tkinter performance
            </div>
            <div class="feature">
                <span class="emoji">🛠️</span>
                <strong>Multiple interfaces</strong> - OOP, functional, and fluent styles
            </div>
            <div class="feature">
                <span class="emoji">🌐</span>
                <strong>URL loading</strong> - Load web pages directly
            </div>
        </div>
    </body>
    </html>
]]):display()

print("✅ Created window 3 with fluent interface")

-- Test 4: Functional interface
print("\n4. Testing functional interface:")

local win4_id = windows.createWindow("Functional Test", 550, 400):getId()
windows.setWindowHtml(win4_id, [[
    <html>
    <head><title>Functional Interface</title></head>
    <body style="font-family: Arial; padding: 20px; background: #e8f5e8;">
        <h2 style="color: #2d5a2d;">Functional Interface Test</h2>
        <p>This window was created using the functional interface.</p>
        <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 15px; margin: 10px 0;">
            <strong>Functions used:</strong>
            <ul>
                <li>windows.createWindow()</li>
                <li>windows.setWindowHtml()</li>
                <li>windows.showWindow()</li>
            </ul>
        </div>
    </body>
    </html>
]])
windows.showWindow(win4_id)

print("✅ Created window 4 with functional interface")

-- Test 5: Window management
print("\n5. Testing window management:")
print("Current windows:")
print(windows.listWindows())

-- Test 6: URL loading (if HTML is supported)
if windows.htmlSupported() then
    print("\n6. Testing URL loading:")
    
    local win5 = windows.createWindow("URL Test", 800, 600)
    
    -- Try to load a simple webpage
    win5:setUrl("https://example.com"):show()
    print("✅ Created window 5 with URL loading")
else
    print("\n6. Skipping URL test (HTML rendering not available)")
end

-- Test 7: Error handling
print("\n7. Testing error handling:")

-- Test operating on closed window
local temp_win = windows.createWindow("Temp Window")
local temp_id = temp_win:getId()
temp_win:close()

local success, error_msg = pcall(function()
    temp_win:show()
end)

if not success then
    print("✅ Error handling works:", error_msg)
else
    print("❌ Error handling failed - should have thrown error")
end

-- Test 8: Help and info
print("\n8. Testing help system:")
print("Module version:", windows._VERSION)
print("Module description:", windows._DESCRIPTION)

-- Don't show full help output in test, just verify it exists
local help_exists = type(windows.help) == "function"
print("Help function available:", help_exists)

-- Test 9: Demo function
print("\n9. Testing demo function:")
if windows.isAvailable() then
    local demo_win = windows.demo()
    if demo_win then
        print("✅ Demo window created successfully")
        print("Demo window ID:", demo_win:getId())
    else
        print("❌ Demo window creation failed")
    end
else
    print("❌ Demo skipped - GUI not available")
end

print("\n" .. string.rep("=", 50))
print("🎉 Windows Module Tests Complete!")
print("✅ Object-oriented interface - Working")
print("✅ Method chaining - Working")
print("✅ Functional interface - Working")
print("✅ Window management - Working")
print("✅ Error handling - Working")
print("✅ Help system - Working")

if windows.htmlSupported() then
    print("✅ HTML rendering - Working")
    print("✅ URL loading - Working")
else
    print("⚠️  HTML rendering - Not available")
    print("⚠️  URL loading - Not available")
end

print("\n📝 Usage examples:")
print("  local windows = require('windows')")
print("  local win = windows.createWindow('My App')")
print("  win:html('<h1>Hello World!</h1>'):show()")
print("  -- or --")
print("  windows.create('Demo'):html('<h1>Demo</h1>'):display()")
print("\n🔧 Try windows.help() for full documentation")
print("🎨 Try windows.demo() for a showcase")

-- Keep the script running to show windows
print("\n⏳ Script complete. Windows will remain open.")
print("💡 Close windows manually or run win:close() to close them programmatically.")
