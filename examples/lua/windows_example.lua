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
                max-width: 500px;
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
            .action-button {
                background: linear-gradient(45deg, #ff6b6b, #ee5a52);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                margin: 8px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                background: linear-gradient(45deg, #ff5252, #d32f2f);
            }
            .action-button.success {
                background: linear-gradient(45deg, #56ab2f, #a8e6cf);
            }
            .action-button.success:hover {
                background: linear-gradient(45deg, #4caf50, #81c784);
            }
            .action-button.info {
                background: linear-gradient(45deg, #667eea, #764ba2);
            }
            .action-button.info:hover {
                background: linear-gradient(45deg, #5c6bc0, #673ab7);
            }
            .output-area {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                min-height: 100px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                text-align: left;
            }
            .status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
            #output {
                margin-top: 10px;
                font-family: 'Courier New', monospace;
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
                <span class="badge">⚡ CEF</span>
            </div>
            
            <div style="margin: 30px 0;">
                <h3>🎯 Interactive Demo</h3>
                <p>Click the buttons below to see JavaScript in action!</p>
                
                <button class="action-button" onclick="printHello()">
                    🖨️ Print Hello
                </button>
                
                <button class="action-button success" onclick="showTime()">
                    🕐 Show Time
                </button>
                
                <button class="action-button info" onclick="countNumbers()">
                    🔢 Count 1-3
                </button>
                
                <button class="action-button" onclick="randomNumber()">
                    🎲 Random Number
                </button>
                
                <div class="output-area">
                    <div id="status" class="status">Ready to execute JavaScript...</div>
                    <div id="output">Click a button above to see output here...</div>
                </div>
            </div>
            
            <p style="margin-top: 30px; font-size: 1em; opacity: 0.7;">
                Window ID: ]] .. myWindow:getId() .. [[
            </p>
        </div>
        
        <script>
            let executionCount = 0;
            
            function updateStatus(message) {
                document.getElementById('status').innerHTML = message;
            }
            
            function updateOutput(message) {
                document.getElementById('output').innerHTML = message;
            }
            
            function printHello() {
                executionCount++;
                updateStatus('🌐 Executing: Print Hello (' + executionCount + ')');
                updateOutput('<strong style="color: #4caf50;">Hello from JavaScript button!</strong><br>This demonstrates working JavaScript in CEF (Chromium Embedded Framework).');
            }
            
            function showTime() {
                executionCount++;
                updateStatus('🌐 Executing: Show Time (' + executionCount + ')');
                const now = new Date().toLocaleString();
                updateOutput('<strong style="color: #2196f3;">Current time:</strong> ' + now + '<br><em>JavaScript Date object working perfectly!</em>');
            }
            
            function countNumbers() {
                executionCount++;
                updateStatus('🌐 Executing: Count Numbers (' + executionCount + ')');
                let output = '<strong style="color: #ff9800;">Counting with JavaScript:</strong><br>';
                for (let i = 1; i <= 5; i++) {
                    output += '→ Count: ' + i + '<br>';
                }
                output += '<em>JavaScript loops working in CEF!</em>';
                updateOutput(output);
            }
            
            function randomNumber() {
                executionCount++;
                updateStatus('🌐 Executing: Random Number (' + executionCount + ')');
                const random = Math.floor(Math.random() * 100) + 1;
                updateOutput('<strong style="color: #e91e63;">Random number:</strong> ' + random + '<br><em>Math.random() working perfectly!</em>');
            }
            
            // Auto-test to show JavaScript is working
            setTimeout(function() {
                updateStatus('✅ JavaScript is fully functional in CEF!');
            }, 1000);
        </script>
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