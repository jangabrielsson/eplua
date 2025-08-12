--%%name:WindowTestMaster
--%%type:com.fibaro.device
--%%debug:true

function QuickApp:onInit()
    self:debug("Window Test Master initialized")
    
    local emu = fibaro.plua
    
    -- Test 1: Create window for QA 1111
    local success1 = emu.lib.createQuickAppWindow(
        1111, 
        "QuickApp 1111 Window", 
        400, 
        300, 
        100, 
        100
    )
    self:debug("Window for QA 1111: " .. tostring(success1))
    
    -- Test 2: Create window for QA 2222 (different QA, should create new window)
    setTimeout(function()
        local success2 = emu.lib.createQuickAppWindow(
            2222, 
            "QuickApp 2222 Window", 
            400, 
            300, 
            200, 
            200
        )
        self:debug("Window for QA 2222: " .. tostring(success2))
    end, 2000)
    
    -- Test 3: Create another window for QA 1111 (same URL, should reuse)
    setTimeout(function()
        local success3 = emu.lib.createQuickAppWindow(
            1111, 
            "QuickApp 1111 Reuse Test", 
            500, 
            400, 
            300, 
            300
        )
        self:debug("Window for QA 1111 reuse: " .. tostring(success3))
    end, 4000)
    
    -- Keep alive
    setTimeout(function()
        self:debug("Test completed")
    end, 8000)
end
