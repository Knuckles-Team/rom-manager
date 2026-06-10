"""Backwards-compatible shim re-exporting the conversion domain module.

The real implementation now lives in :mod:`rom_manager.core.conversion` (the
domain layer). This shim preserves the historical ``rom_manager.conversion``
import path. CONCEPT:ROM-001.
"""

from rom_manager.core.conversion import (
    Converter,
    Runner,
    build_convert_command,
    run_command,
)

__all__ = ["Converter", "Runner", "build_convert_command", "run_command"]
