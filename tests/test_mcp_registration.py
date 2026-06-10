"""Verify MCP tool registration wiring.

CONCEPT:ROM-001, CONCEPT:ROM-002 — both tool domains register on the server.
"""

import importlib

import pytest


@pytest.mark.concept("ROM-001")
def test_register_functions_exported():
    mcp_pkg = importlib.import_module("rom_manager.mcp")
    assert hasattr(mcp_pkg, "register_conversion_tools")
    assert hasattr(mcp_pkg, "register_game_codes_tools")


@pytest.mark.concept("ROM-002")
def test_registration_invokes_tool_decorator():
    """Calling register_*_tools should register a tool on a FastMCP instance."""
    from rom_manager.mcp import (
        register_conversion_tools,
        register_game_codes_tools,
    )

    registered_tags = []

    class FakeMCP:
        def tool(self, *args, **kwargs):
            registered_tags.append(kwargs.get("tags"))

            def decorator(fn):
                return fn

            return decorator

    mcp = FakeMCP()
    register_conversion_tools(mcp)
    register_game_codes_tools(mcp)

    flat = {t for tags in registered_tags if tags for t in tags}
    assert "conversion" in flat
    assert "game-codes" in flat


@pytest.mark.concept("ROM-001")
def test_get_mcp_instance_smoke():
    """The full server assembly should build without raising."""
    from rom_manager.mcp_server import get_mcp_instance

    mcp, args, middlewares, registered_tags = get_mcp_instance()
    assert mcp is not None
