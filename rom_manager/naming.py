"""Backwards-compatible shim re-exporting the naming domain module.

The real implementation now lives in :mod:`rom_manager.core.naming` (the domain
layer). This shim preserves the historical ``rom_manager.naming`` import path.
CONCEPT:ROM-002.
"""

from rom_manager.core.naming import (
    lookup_game_code,
    map_game_code_name,
    sanitize_title,
)

__all__ = ["lookup_game_code", "map_game_code_name", "sanitize_title"]
