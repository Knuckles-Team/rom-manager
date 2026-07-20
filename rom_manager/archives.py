"""Backwards-compatible shim re-exporting the archives domain module.

The real implementation now lives in :mod:`rom_manager.core.archives` (the
domain layer). This shim preserves the historical ``rom_manager.archives``
import path. CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool.
"""

from rom_manager.core.archives import (
    ARCHIVE_FORMATS,
    ArchiveSafetyError,
    cue_file_generator,
    extract_archive,
    get_files,
    is_archive,
    pad_leading_zero,
)

__all__ = [
    "ARCHIVE_FORMATS",
    "ArchiveSafetyError",
    "cue_file_generator",
    "extract_archive",
    "get_files",
    "is_archive",
    "pad_leading_zero",
]
