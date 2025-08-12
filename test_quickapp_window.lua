--%%name:TestQuickApp
--%%type:com.fibaro.binarySwitch
--%%desktop:true
--%%debug:true
--%%u:{label="lbl1",text="Hello QuickApp Desktop UI!"}
--%%u:{button="btn1",text="Click Me",onReleased="testButton"}
--%%u:{slider="slider1",text="Test Slider",min="0",max="100",value="50",onChanged="testSlider"}
--%%u:{switch="switch1",text="Test Switch",value="false",onReleased="testSwitch"}

function QuickApp:onInit()
    self:debug("QuickApp Desktop Test initialized")
    
    -- Test screen dimensions via fibaro.plua reference
    local emu = fibaro.plua
    local width, height = emu.lib.getScreenDimension()
    self:debug("Screen dimensions: " .. width .. "x" .. height)
    
    -- Manually create an additional window for testing
    local success = emu.lib.createQuickAppWindow(
        self.id, 
        "Manual Test Window", 
        600, 
        400, 
        200, 
        200
    )
    self:debug("Manual window creation: " .. tostring(success))
    
    -- Test URL reuse: try to create another window with same URL (should reuse)
    setTimeout(function()
        local success2 = emu.lib.createQuickAppWindow(
            self.id, 
            "Same URL Test Window", 
            500, 
            350, 
            300, 
            300
        )
        self:debug("Same URL window creation (should reuse): " .. tostring(success2))
    end, 2000)
    
    -- Keep the engine alive for testing
    setTimeout(function()
        self:debug("Keeping alive...")
    end, 1000*60)
end

function QuickApp:testButton()
    self:debug("Button clicked!")
    
    -- Update the label text
    self:updateView("lbl1", "text", "Button was clicked at " .. os.date("%H:%M:%S"))
end

function QuickApp:testSlider(value)
    self:debug("Slider changed to: " .. value)
    
    -- Update the label to show slider value
    self:updateView("lbl1", "text", "Slider value: " .. value)
end

function QuickApp:testSwitch(value)
    self:debug("Switch toggled to: " .. tostring(value))
    
    -- Update the label to show switch state
    self:updateView("lbl1", "text", "Switch is: " .. (value and "ON" or "OFF"))
end
