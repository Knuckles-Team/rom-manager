"""Backwards-compatible shim re-exporting the API facade adapter.

The real implementation now lives in :mod:`rom_manager.adapters.api_client` (the
adapter layer). This shim preserves the historical ``rom_manager.api_client``
import path used by ``auth.get_client`` and the MCP tools. CONCEPT:ROM-001.
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
