"""Adapter layer for ROM Manager.

CONCEPT:ROM-001, CONCEPT:ROM-002 — adapts the core pipeline for tool/agent
consumption. Houses the :class:`~rom_manager.adapters.api_client.Api` facade that
the MCP tools and the ``auth.get_client`` factory depend on.
"""

from rom_manager.adapters.api_client import (
    Api,
    RomManager,
    get_directory_size,
    get_operating_system,
    psx_codes,
)

__all__ = [
    "Api",
    "RomManager",
    "psx_codes",
    "get_operating_system",
    "get_directory_size",
]
