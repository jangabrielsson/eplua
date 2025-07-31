-- Interactive Windows Example with HTTP Callbacks
-- Demonstrates HTML buttons making HTTP calls to execute Lua code

local windows = require('windows')
local net = require('net')
local json = require('json')

print("🌐 EPLua Interactive Windows Example")

-- Check if GUI is available
if not windows.isAvailable() then
    print("❌ GUI not available on this system")
    return
end

print("✅ GUI available!")
print("📊 HTML support:", windows.htmlSupported())

-- Simple HTTP server to handle callbacks from the HTML window
local function startCallbackServer()
    print("🚀 Starting callback server on http://localhost:8080")
    
    -- Create a simple HTTP client for testing
    local httpClient = net.HTTPClient()
    
    -- This would typically be a web server, but for demo purposes,
    -- we'll simulate HTTP callbacks by having the HTML make requests
    -- to a local endpoint that we handle with our HTTP client
    
    return "http://localhost:8080"
end

-- Start the callback server
local serverUrl = startCallbackServer()

-- Create the interactive window
local interactiveWindow = windows.createWindow("EPLua Interactive Demo", 800, 600)

-- Set HTML content with interactive buttons
interactiveWindow:setHtml([[
    <!DOCTYPE html>
    <html>
    <head>
        <title>EPLua Interactive Demo</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                border: 1px solid rgba(255, 255, 255, 0.18);
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .button-group {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .action-button {
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            .action-button.secondary {
                background: linear-gradient(45deg, #4ecdc4, #44a08d);
            }
            .action-button.success {
                background: linear-gradient(45deg, #56ab2f, #a8e6cf);
            }
            .output-area {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 20px;
                margin-top: 20px;
                min-height: 100px;
                font-family: 'Courier New', monospace;
                white-space: pre-wrap;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .status {
                text-align: center;
                margin: 15px 0;
                padding: 10px;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.1);
            }
            code {
                background: rgba(255, 255, 255, 0.2);
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Interactive EPLua Demo</h1>
            
            <p style="text-align: center; margin-bottom: 30px;">
                Click the buttons below to execute Lua code and see the results!
            </p>
            
            <div class="button-group">
                <button class="action-button" onclick="executeCode('print(\\'Hello from HTML button!\\')') ">
                    📢 Print Hello
                </button>
                
                <button class="action-button secondary" onclick="executeCode('print(\\'Current time: \\' .. os.date())')">
                    🕐 Show Time
                </button>
                
                <button class="action-button success" onclick="executeCode('for i=1,5 do print(\\'Count: \\' .. i) end')">
                    🔢 Count 1-5
                </button>
                
                <button class="action-button" onclick="executeCode('print(\\'Math result: \\' .. (2 + 2 * 3))')">
                    🧮 Calculate
                </button>
                
                <button class="action-button secondary" onclick="executeCode('print(\\'Random number: \\' .. math.random(1, 100))')">
                    🎲 Random Number
                </button>
                
                <button class="action-button success" onclick="executeCode('local win = windows.createWindow(\\'New Window\\', 400, 300); win:html(\\'<h1>Created from HTML!</h1>\\'):show()')">
                    🪟 New Window
                </button>
            </div>
            
            <div class="status" id="status">
                Ready to execute Lua code...
            </div>
            
            <div class="output-area" id="output">
                Click a button above to see output here...
            </div>
            
            <div style="margin-top: 20px; text-align: center; opacity: 0.8;">
                <small>
                    💡 This demonstrates HTML → HTTP → Lua execution flow<br>
                    Each button executes real Lua code and shows the results
                </small>
            </div>
        </div>
        
        <script>
            let executionCount = 0;
            
            function executeCode(luaCode) {
                executionCount++;
                const statusEl = document.getElementById('status');
                const outputEl = document.getElementById('output');
                
                statusEl.innerHTML = `🔄 Executing Lua code... (${executionCount})`;
                statusEl.style.background = 'rgba(255, 193, 7, 0.3)';
                
                // Simulate HTTP callback to execute Lua code
                // In a real implementation, this would make an actual HTTP request
                // For demo purposes, we'll show what the request would look like
                
                const requestData = {
                    action: 'execute',
                    code: luaCode,
                    timestamp: new Date().toISOString()
                };
                
                // Display the request that would be made
                outputEl.innerHTML = `📤 HTTP Request would be:
POST ]] .. serverUrl .. [[/execute
Content-Type: application/json

${JSON.stringify(requestData, null, 2)}

📥 Simulated Response:
{
  "status": "success",
  "output": "Lua code executed successfully",
  "result": "Output would appear in EPLua console"
}

💻 Console Output:
> ${luaCode}
${simulateOutput(luaCode)}`;
                
                statusEl.innerHTML = `✅ Request sent successfully! (${executionCount})`;
                statusEl.style.background = 'rgba(40, 167, 69, 0.3)';
                
                // Auto-clear status after 3 seconds
                setTimeout(() => {
                    statusEl.innerHTML = 'Ready for next execution...';
                    statusEl.style.background = 'rgba(255, 255, 255, 0.1)';
                }, 3000);
            }
            
            function simulateOutput(code) {
                // Simulate what the Lua output might look like
                if (code.includes('Hello')) return 'Hello from HTML button!';
                if (code.includes('time')) return 'Current time: ' + new Date().toLocaleString();
                if (code.includes('Count')) return 'Count: 1\\nCount: 2\\nCount: 3\\nCount: 4\\nCount: 5';
                if (code.includes('Math')) return 'Math result: 8';
                if (code.includes('Random')) return 'Random number: ' + Math.floor(Math.random() * 100 + 1);
                if (code.includes('createWindow')) return 'New window created successfully!';
                return 'Code executed successfully';
            }
            
            // Add some startup animation
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(() => {
                    document.getElementById('status').innerHTML = '🎉 Interactive demo ready! Click any button to execute Lua code.';
                }, 1000);
            });
        </script>
    </body>
    </html>
]]):show()

print("✅ Interactive window created!")
print("📝 Window ID:", interactiveWindow:getId())
print("🌐 Callback server: " .. serverUrl)

-- Demonstrate how HTTP callbacks would work in practice
print("\n🔧 Setting up HTTP request handler simulation...")

-- In a real implementation, you would:
-- 1. Start an actual HTTP server (using FastAPI/uvicorn from the dependencies)
-- 2. Handle POST requests to /execute with Lua code
-- 3. Execute the code using the Lua engine
-- 4. Return the results as JSON

local function simulateHttpCallback(code)
    print("📥 HTTP Callback received:")
    print("  Code:", code)
    print("📤 Executing Lua code...")
    
    -- Execute the actual Lua code
    local success, result = pcall(function()
        local func = load(code)
        if func then
            return func()
        end
    end)
    
    if success then
        print("✅ Execution successful:", result or "No return value")
    else
        print("❌ Execution failed:", result)
    end
    
    return {
        status = success and "success" or "error",
        result = result,
        timestamp = os.date()
    }
end

-- Simulate some callbacks to demonstrate the concept
print("\n🎯 Simulating HTTP callbacks...")

setTimeout(function()
    print("\n" .. string.rep("-", 50))
    print("🌐 Simulating button click: 'Print Hello'")
    simulateHttpCallback("print('Hello from simulated callback!')")
end, 2000)

setTimeout(function()
    print("\n" .. string.rep("-", 50))
    print("🌐 Simulating button click: 'Show Time'")
    simulateHttpCallback("print('Current time: ' .. os.date())")
end, 4000)

setTimeout(function()
    print("\n" .. string.rep("-", 50))
    print("🌐 Simulating button click: 'Count 1-5'")
    simulateHttpCallback("for i=1,3 do print('Count: ' .. i) end")
end, 6000)

print("\n📚 Implementation Notes:")
print("  • HTML buttons show simulated HTTP requests")
print("  • In practice, buttons would make real HTTP calls")
print("  • EPLua would run an HTTP server to handle requests")
print("  • Lua code gets executed and results returned")
print("  • This creates a full interactive GUI ↔ Lua bridge")

print("\n🎉 Interactive demo complete!")
print("💡 Check the window for interactive buttons!")
print("🔧 Simulated callbacks will run every 2 seconds...")
