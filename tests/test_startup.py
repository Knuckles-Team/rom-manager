import pytest


@pytest.mark.concept("ROM-001")
def test_server_startup():
    """Validates that the server modules import without side effects breaking."""
    import importlib

    # mcp_server and agent_server must be importable
    importlib.import_module("rom_manager.mcp_server")
    importlib.import_module("rom_manager.agent_server")
    print("Startup tests handled correctly.")
