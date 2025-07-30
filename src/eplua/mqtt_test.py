"""
Simple test for MQTT return type debugging
"""
from .lua_bindings import export_to_lua

@export_to_lua("test_mqtt_return")
def test_mqtt_return() -> str:
    """Test function that returns a simple string"""
    return "test_string_result"
