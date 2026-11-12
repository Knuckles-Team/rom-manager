"""Verify MCP tool registration wiring.

CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool, CONCEPT:RO-OS.governance.game-codes-naming-resolves - the conversion, game-code and RomM operations are served as typed tools.
"""

import asyncio
import importlib

import pytest


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
def test_only_the_ingest_registrar_is_exported():
    mcp_pkg = importlib.import_module("rom_manager.mcp")
    assert hasattr(mcp_pkg, "register_ingest_tools")
    assert not hasattr(mcp_pkg, "register_conversion_tools")
    assert not hasattr(mcp_pkg, "register_game_codes_tools")


@pytest.mark.concept("RO-OS.governance.game-codes-naming-resolves")
def test_conversion_and_game_code_tools_are_typed():
    from fastmcp import Client

    from rom_manager.mcp_server import get_mcp_instance

    mcp, _, _, _ = get_mcp_instance()

    async def names():
        async with Client(mcp) as client:
            return {t.name for t in await client.list_tools()}

    served = asyncio.run(names())
    for name in (
        "rom_manager_convert",
        "rom_manager_process_file",
        "rom_manager_generate_cue",
        "rom_manager_list_files",
        "rom_manager_lookup_game_code",
        "rom_manager_list_game_codes",
    ):
        assert name in served
    assert "rom_conversion" not in served
    assert "rom_game_codes" not in served


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
def test_get_mcp_instance_smoke():
    """The full server assembly should build without raising."""
    from rom_manager.mcp_server import get_mcp_instance

    mcp, args, middlewares, registered_tags = get_mcp_instance()
    assert mcp is not None
