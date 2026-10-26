#!/usr/bin/env python
"""rom-manager — ROM converter/organizer + MCP Server + A2A Agent.

Convert game ROMs to Compressed Hunks of Data (CHD) or RVZ, extract archives,
auto-rename via known game codes, and generate cue sheets. The core
:class:`RomManager` pipeline is wrapped by an MCP server and a Pydantic-AI agent.
"""

from rom_manager.game_codes import psx_codes
from rom_manager.rom_manager import (
    RomManager,
    get_directory_size,
    get_operating_system,
    main,
    rom_manager,
)
from rom_manager.romm import RommApi, get_romm_client
from rom_manager.version import __author__, __credits__, __version__

__all__ = [
    "psx_codes",
    "rom_manager",
    "main",
    "RomManager",
    "get_operating_system",
    "get_directory_size",
    "RommApi",
    "get_romm_client",
    "__version__",
    "__author__",
    "__credits__",
]


from agent_connector_sdk.connector import Connector
from agent_connector_sdk.connector_hooks import RegistrationContext


def _register_legacy_surface(context: RegistrationContext) -> None:
    from rom_manager.mcp_server import register_server_surface

    vars(context.server)["_rom_registered_tags"] = register_server_surface(
        context.server
    )


connector = Connector(
    instructions="ROM Manager MCP Server - Convert ROMs to CHD/RVZ, extract archives, generate cue sheets, and resolve game codes.",
    extra_registrations=(_register_legacy_surface,),
)
