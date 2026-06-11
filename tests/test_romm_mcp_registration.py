"""RomM MCP tool registration tests (CONCEPT:ROM-003)."""

import pytest

from rom_manager.mcp import register_romm_tools
from rom_manager.mcp.mcp_romm import ROMM_TOOLS


class FakeMCP:
    def __init__(self):
        self.names = []
        self.tags = []

    def tool(self, *args, **kwargs):
        self.names.append(kwargs.get("name"))
        self.tags.append(kwargs.get("tags"))

        def decorator(fn):
            return fn

        return decorator


@pytest.mark.concept("ROM-003")
def test_register_romm_tools_registers_every_resource():
    mcp = FakeMCP()
    register_romm_tools(mcp)
    expected_names = {name for name, _t, _s, _a in ROMM_TOOLS}
    assert set(mcp.names) == expected_names
    flat_tags = {t for tags in mcp.tags if tags for t in tags}
    assert "romm-roms" in flat_tags
    assert "romm-system" in flat_tags
    assert len(mcp.names) == 14


@pytest.mark.concept("ROM-003")
def test_get_mcp_instance_builds_with_romm(monkeypatch):
    monkeypatch.setenv("ROMMTOOL", "True")
    from rom_manager.mcp_server import get_mcp_instance

    mcp, args, middlewares, registered_tags = get_mcp_instance()
    assert mcp is not None
