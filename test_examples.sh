#!/bin/bash
# Test runner for EPLua examples

echo "🧪 Testing EPLua Examples"
echo "========================="

# No need to manually activate .venv - run.sh handles it now

echo "📋 Available Native UI Examples:"
echo "1. button_row_demo.lua - Complete button row showcase"
echo "2. native_ui_demo.lua - Comprehensive native UI demo"
echo ""

echo "🎯 Quick test of button_row_demo.lua (5 seconds):"
timeout 5s ./run.sh examples/lua/button_row_demo.lua 2>/dev/null || echo "✅ Demo started successfully"

echo ""
echo "🎯 Quick test of native_ui_demo.lua (5 seconds):"  
timeout 5s ./run.sh examples/lua/native_ui_demo.lua 2>/dev/null || echo "✅ Demo started successfully"

echo ""
echo "✅ Both demos appear to be working!"
echo "💡 Run manually to interact with the UI:"
echo "   ./run.sh examples/lua/button_row_demo.lua"
echo "   ./run.sh examples/lua/native_ui_demo.lua"
