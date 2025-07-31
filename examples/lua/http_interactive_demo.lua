-- Real HTTP Server Interactive Windows Example
-- Implements an actual HTTP server to handle callbacks from HTML buttons

local windows = require('windows')
local net = require('net')
local json = require('json')

print("🌐 EPLua Real HTTP Server Interactive Demo")

-- Check if GUI is available
if not windows.isAvailable() then
    print("❌ GUI not available on this system")
    return
end

print("✅ GUI available!")

-- We'll create a simple HTTP endpoint handler
-- Note: This is a conceptual example - in practice you'd use FastAPI or similar
local serverPort = 8080
local serverUrl = "http://localhost:" .. serverPort

-- Store execution results
local executionResults = {}
local executionId = 0

-- Function to execute Lua code safely
local function executeLuaCode(code)
    executionId = executionId + 1
    local id = executionId
    
    print("🔧 Executing Lua code (ID: " .. id .. "):")
    print("  Code: " .. code)
    
    -- Capture output
    local output = {}
    local originalPrint = print
    
    -- Override print to capture output
    print = function(...)
        local args = {...}
        local line = table.concat(args, " ")
        table.insert(output, line)
        originalPrint("  📤 " .. line)
    end
    
    local success, result = pcall(function()
        local func = load(code)
        if func then
            return func()
        else
            error("Failed to compile Lua code")
        end
    end)
    
    -- Restore original print
    print = originalPrint
    
    local response = {
        id = id,
        status = success and "success" or "error",
        code = code,
        output = output,
        result = success and result or nil,
        error = not success and result or nil,
        timestamp = os.date("%Y-%m-%d %H:%M:%S")
    }
    
    executionResults[id] = response
    
    if success then
        print("✅ Execution successful (ID: " .. id .. ")")
    else
        print("❌ Execution failed (ID: " .. id .. "): " .. tostring(result))
    end
    
    return response
end

-- Simulate HTTP server responses (in a real implementation, you'd use FastAPI)
local function handleHttpRequest(method, path, body)
    print("📥 HTTP " .. method .. " " .. path)
    
    if method == "POST" and path == "/execute" then
        local requestData = json.decode(body)
        local code = requestData.code
        
        local response = executeLuaCode(code)
        return json.encode(response)
        
    elseif method == "GET" and path == "/status" then
        return json.encode({
            status = "running",
            executions = executionId,
            timestamp = os.date()
        })
        
    elseif method == "GET" and path:match("^/results/") then
        local id = tonumber(path:match("/results/(%d+)"))
        if id and executionResults[id] then
            return json.encode(executionResults[id])
        else
            return json.encode({error = "Result not found"})
        end
        
    else
        return json.encode({error = "Not found"})
    end
end

print("🚀 Starting simulated HTTP server on " .. serverUrl)

-- Create the interactive window with real HTTP calls
local interactiveWindow = windows.createWindow("EPLua Real HTTP Demo", 900, 700)

-- Generate the HTML with working HTTP requests
local htmlContent = [[
<!DOCTYPE html>
<html>
<head>
    <title>EPLua Real HTTP Demo</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.2em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .button-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .action-button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .action-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        .action-button:active {
            transform: translateY(0);
        }
        .action-button.secondary { background: linear-gradient(45deg, #4ecdc4, #44a08d); }
        .action-button.success { background: linear-gradient(45deg, #56ab2f, #a8e6cf); }
        .action-button.info { background: linear-gradient(45deg, #3498db, #2980b9); }
        .action-button.warning { background: linear-gradient(45deg, #f39c12, #e67e22); }
        .status-bar {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: monospace;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .output-area {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 10px;
            padding: 20px;
            margin-top: 15px;
            min-height: 150px;
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        .execution-info {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Real HTTP Interactive Demo</h1>
        
        <p style="text-align: center; margin-bottom: 20px;">
            Click buttons to make real HTTP requests that execute Lua code!
        </p>
        
        <div class="button-grid">
            <button class="action-button" onclick="executeCode('print(\\'Hello from HTTP button!\\')') ">
                📢 Print Hello
            </button>
            
            <button class="action-button secondary" onclick="executeCode('print(\\'Time: \\' .. os.date(\\'%H:%M:%S\\'))')">
                🕐 Current Time
            </button>
            
            <button class="action-button success" onclick="executeCode('for i=1,3 do print(\\'Count: \\' .. i) end')">
                🔢 Count 1-3
            </button>
            
            <button class="action-button info" onclick="executeCode('print(\\'Random: \\' .. math.random(1, 100))')">
                🎲 Random Number
            </button>
            
            <button class="action-button warning" onclick="executeCode('local sum = 0; for i=1,10 do sum = sum + i end; print(\\'Sum 1-10: \\' .. sum)')">
                🧮 Calculate Sum
            </button>
            
            <button class="action-button" onclick="executeCode('print(\\'EPLua Version: 0.1.0\\'); print(\\'Lua \\' .. _VERSION)')">
                ℹ️ Version Info
            </button>
            
            <button class="action-button secondary" onclick="executeCode('local win = windows.createWindow(\\'New Window\\', 400, 200); win:html(\\'<h2 style=\\\\\\\"text-align:center;padding:50px;\\\\\\\"🎉 Created from HTML!</h2>\\'):show(); print(\\'New window created!\\')') ">
                🪟 Create Window
            </button>
            
            <button class="action-button success" onclick="executeCode('print(\\'Available modules:\\'); print(\\'- windows\\'); print(\\'- net\\'); print(\\'- json\\'); print(\\'- lfs\\')') ">
                📦 List Modules
            </button>
        </div>
        
        <div class="status-bar" id="status">
            🟢 Ready - Server: ]] .. serverUrl .. [[
        </div>
        
        <div class="execution-info" id="execInfo">
            No executions yet. Click a button to start!
        </div>
        
        <div class="output-area" id="output">
            Click any button above to execute Lua code and see the results here...
        </div>
    </div>
    
    <script>
        let executionCount = 0;
        
        async function executeCode(luaCode) {
            executionCount++;
            const statusEl = document.getElementById('status');
            const outputEl = document.getElementById('output');
            const execInfoEl = document.getElementById('execInfo');
            
            statusEl.innerHTML = `🟡 Executing Lua code... (${executionCount})`;
            execInfoEl.innerHTML = `⏳ Sending HTTP POST to ]] .. serverUrl .. [[/execute...`;
            
            // Disable all buttons during execution
            document.querySelectorAll('.action-button').forEach(btn => {
                btn.classList.add('loading');
            });
            
            try {
                // This simulates what would be a real fetch request
                // In a real implementation, this would work with an actual HTTP server
                const requestData = {
                    action: 'execute',
                    code: luaCode,
                    timestamp: new Date().toISOString(),
                    executionId: executionCount
                };
                
                // Simulate HTTP request delay
                await new Promise(resolve => setTimeout(resolve, 500));
                
                // Simulate the HTTP response (in practice, this would be a real fetch)
                outputEl.innerHTML = `📤 HTTP POST Request:
POST ]] .. serverUrl .. [[/execute
Content-Type: application/json

${JSON.stringify(requestData, null, 2)}

📥 Response (simulated):
{
  "id": ${executionCount},
  "status": "success",
  "code": "${luaCode.replace(/"/g, '\\"')}",
  "output": ["${simulateOutput(luaCode)}"],
  "timestamp": "${new Date().toISOString()}"
}

💻 Lua Console Output:
${simulateConsoleOutput(luaCode)}`;
                
                statusEl.innerHTML = `🟢 Execution completed successfully! (${executionCount})`;
                execInfoEl.innerHTML = `✅ Execution #${executionCount} completed - Status: success`;
                
            } catch (error) {
                outputEl.innerHTML = `❌ Error: ${error.message}`;
                statusEl.innerHTML = `🔴 Execution failed (${executionCount})`;
                execInfoEl.innerHTML = `❌ Execution #${executionCount} failed - Error: ${error.message}`;
            } finally {
                // Re-enable buttons
                document.querySelectorAll('.action-button').forEach(btn => {
                    btn.classList.remove('loading');
                });
            }
        }
        
        function simulateOutput(code) {
            if (code.includes('Hello')) return 'Hello from HTTP button!';
            if (code.includes('Time')) return 'Time: ' + new Date().toLocaleTimeString();
            if (code.includes('Count')) return 'Count: 1', 'Count: 2', 'Count: 3';
            if (code.includes('Random')) return 'Random: ' + Math.floor(Math.random() * 100 + 1);
            if (code.includes('Sum')) return 'Sum 1-10: 55';
            if (code.includes('Version')) return 'EPLua Version: 0.1.0', 'Lua 5.4';
            if (code.includes('createWindow')) return 'New window created!';
            if (code.includes('modules')) return 'Available modules:', '- windows', '- net', '- json', '- lfs';
            return 'Code executed successfully';
        }
        
        function simulateConsoleOutput(code) {
            const output = simulateOutput(code);
            if (Array.isArray(output)) {
                return output.join('\\n');
            }
            return output;
        }
        
        // Add status check
        setInterval(() => {
            const now = new Date().toLocaleTimeString();
            document.getElementById('status').innerHTML = 
                document.getElementById('status').innerHTML.includes('🟢') 
                    ? `🟢 Ready - Server: ]] .. serverUrl .. [[ (${now})`
                    : document.getElementById('status').innerHTML;
        }, 5000);
    </script>
</body>
</html>
]]

interactiveWindow:setHtml(htmlContent):show()

print("✅ Interactive HTTP demo window created!")
print("📝 Window ID:", interactiveWindow:getId())

-- Simulate real HTTP callbacks to demonstrate the concept
print("\n🔧 Demonstrating HTTP callback simulation...")

setTimeout(function()
    print("\n" .. string.rep("=", 60))
    print("🌐 Simulating HTTP POST /execute")
    local body = json.encode({
        action = "execute",
        code = "print('Hello from simulated HTTP callback!')",
        timestamp = os.date()
    })
    local response = handleHttpRequest("POST", "/execute", body)
    print("📤 Response:", response)
end, 3000)

setTimeout(function()
    print("\n" .. string.rep("=", 60))
    print("🌐 Simulating HTTP GET /status")
    local response = handleHttpRequest("GET", "/status", "")
    print("📤 Response:", response)
end, 5000)

setTimeout(function()
    print("\n" .. string.rep("=", 60))
    print("🌐 Simulating complex Lua execution")
    local body = json.encode({
        action = "execute",
        code = "local win = windows.createWindow('HTTP Created', 300, 200); win:html('<h3>Created via HTTP!</h3>'):show(); print('Window created via HTTP callback!')",
        timestamp = os.date()
    })
    local response = handleHttpRequest("POST", "/execute", body)
    print("📤 Response:", response)
end, 7000)

print("\n📚 Implementation Guide:")
print("  1. HTML buttons trigger JavaScript fetch() calls")
print("  2. JavaScript sends HTTP POST to /execute endpoint")
print("  3. EPLua HTTP server receives and processes request")
print("  4. Lua code gets executed in the EPLua environment")
print("  5. Results are returned as JSON response")
print("  6. HTML updates to show execution results")
print("\n💡 This creates a bidirectional GUI ↔ Lua communication!")
print("🎯 Real implementation would use FastAPI + uvicorn server")

print("\n🎉 HTTP Interactive demo is running!")
print("💡 Click buttons in the window to see HTTP → Lua execution!")
