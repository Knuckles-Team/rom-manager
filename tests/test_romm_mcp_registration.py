"""RomM MCP tool registration tests (CONCEPT:RO-OS.state.api-base-one-mixin)."""

import asyncio

import pytest

from rom_manager.romm.tool_table import ROMM_TOOLS


@pytest.mark.concept("RO-OS.state.api-base-one-mixin")
def test_every_romm_operation_is_a_typed_tool(monkeypatch):
    from fastmcp import Client

    monkeypatch.setenv("ROMMTOOL", "True")
    from rom_manager.mcp_server import get_mcp_instance

    mcp, _, _, _ = get_mcp_instance()

    async def names():
        async with Client(mcp) as client:
            return {t.name for t in await client.list_tools()}

    served = asyncio.run(names())
    methods = {m for _n, _t, _s, actions in ROMM_TOOLS for m in actions.values()}
    missing = sorted(m for m in methods if f"romm_{m}" not in served)
    assert not missing, missing


@pytest.mark.concept("RO-OS.state.api-base-one-mixin")
def test_get_mcp_instance_builds_with_romm(monkeypatch):
    monkeypatch.setenv("ROMMTOOL", "True")
    from rom_manager.mcp_server import get_mcp_instance

    mcp, args, middlewares, registered_tags = get_mcp_instance()
    assert mcp is not None
