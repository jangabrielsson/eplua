-- Simple Windows Module Example
-- Demonstrates basic usage of the windows module

local windows = require('windows')

print("🪟 EPLua Windows Example")

-- Check if GUI is available
if not windows.isAvailable() then
    print("❌ GUI not available on this system")
    return
end

print("✅ GUI available!")
print("📊 HTML support:", windows.htmlSupported())
print("🔧 HTML engine:", windows.getHtmlEngine())

-- Create a simple window
print("\n📝 Creating a simple window...")

local myWindow = windows.createWindow("My First Window", 600, 400)

-- Set some HTML content
myWindow:setHtml([[
    <!DOCTYPE html>
    <html>
    <head>
        <title>My First EPLua Window</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            p {
                font-size: 1.2em;
                line-height: 1.6;
                opacity: 0.9;
            }
            .badge {
                display: inline-block;
                background: rgba(255, 255, 255, 0.2);
                padding: 5px 15px;
                border-radius: 15px;
                margin: 5px;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Hello, EPLua!</h1>
            <p>Welcome to your first EPLua window!</p>
            <p>This beautiful interface was created using:</p>
            <div>
                <span class="badge">🔧 Lua</span>
                <span class="badge">🐍 Python</span>
                <span class="badge">🌐 HTML/CSS</span>
                <span class="badge">⚡ tkinter</span>
            </div>
            <p style="margin-top: 30px; font-size: 1em; opacity: 0.7;">
                Window ID: ]] .. myWindow:getId() .. [[
            </p>
        </div>
    </body>
    </html>
]])

-- Show the window
myWindow:show()

print("✅ Window created and displayed!")
print("📝 Window ID:", myWindow:getId())

-- Demonstrate method chaining
print("\n🔗 Creating another window with method chaining...")

local quickWindow = windows.create("Quick Demo", 500, 300)
    :html([[
        <html>
        <body style="font-family: Arial; padding: 20px; background: #f0f8ff; text-align: center;">
            <h2 style="color: #2c3e50;">⚡ Method Chaining Demo</h2>
            <p>This window was created using method chaining!</p>
            <div style="background: #ecf0f1; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <code>windows.create("Quick Demo")<br>
                :html("...")<br>
                :show()</code>
            </div>
            <p style="color: #7f8c8d;">Clean, readable, and powerful! 🎉</p>
        </body>
        </html>
    ]])
    :show()

print("✅ Quick window created with method chaining!")

-- Show all windows
print("\n📋 Current windows:")
print(windows.listWindows())

print("\n🎯 Example complete!")
print("💡 Both windows should now be visible.")
print("🔧 You can interact with them or close them manually.")
print("\n📚 For more features, try:")
print("  - windows.help()  -- Show full documentation")
print("  - windows.demo()  -- Show feature showcase")
print("  - myWindow:close() -- Close a window programmatically")

---setInterval(function() end, 5000)