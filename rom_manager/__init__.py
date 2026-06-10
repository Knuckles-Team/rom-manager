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
from rom_manager.version import __author__, __credits__, __version__

__all__ = [
    "psx_codes",
    "rom_manager",
    "main",
    "RomManager",
    "get_operating_system",
    "get_directory_size",
    "__version__",
    "__author__",
    "__credits__",
]
