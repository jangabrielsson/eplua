-- Simple test script to check QuickApp registration
print("=== QuickApp Debug Test ===")

-- Test if fibaro is loaded
function QuickApp:onInit()
    print("Fibaro emulator is loaded")
    
    -- Get all QuickApps
    local qas = _PY.getQuickapps()
    print("getQuickapps result:", type(qas), qas)
    
    if qas then
        print("Number of QuickApps:", #qas)
        for i, qa in ipairs(qas) do
            print("QA", i, "device ID:", qa.device and qa.device.id)
        end
    end
    
    -- Try to get specific QuickApp
    print("Trying to get QuickApp 5555...")
    local qa5555 = _PY.getQuickapp(5555)
    print("getQuickapp(5555) result:", type(qa5555), qa5555)

end

setInterval(function() end, 5000)
print("=== End Debug Test ===")
