#!/usr/bin/python
"""Local facade over the real ROM conversion pipeline.

``rom-manager`` is not a REST API; this module is an **honest local facade**. It
re-exports the real callables from :mod:`rom_manager.rom_manager` and exposes a
thin :class:`Api` class that the MCP tools and the local ``auth.get_client``
factory depend on. Every method delegates to the genuine :class:`RomManager`
pipeline so behaviour is preserved exactly.
"""

import logging
import os
from typing import Any

from agent_utilities.base_utilities import get_logger

from rom_manager.game_codes import psx_codes
from rom_manager.rom_manager import (
    RomManager,
    get_directory_size,
    get_operating_system,
)

logger = get_logger(__name__)

__all__ = [
    "Api",
    "RomManager",
    "psx_codes",
    "get_operating_system",
    "get_directory_size",
]


class Api:
    """Thin facade wrapping :class:`RomManager` for tool/agent consumption."""

    __slots__ = ("directory", "iso_type", "verbose", "force")

    def __init__(
        self,
        directory: str = os.path.curdir,
        iso_type: str = "chd",
        verbose: bool = False,
        force: bool = False,
    ) -> None:
        """Hold conversion defaults for the facade (CONCEPT:ROM-001)."""
        self.directory = directory
        self.iso_type = iso_type
        self.verbose = verbose
        self.force = force

    def _build_manager(
        self,
        directory: str | None = None,
        iso_type: str | None = None,
        verbose: bool | None = None,
        force: bool | None = None,
        clean_origin_files: bool = False,
    ) -> RomManager:
        manager = RomManager()
        manager.directory = directory if directory is not None else self.directory
        manager.iso_type = iso_type if iso_type is not None else self.iso_type
        manager.verbose = verbose if verbose is not None else self.verbose
        manager.force = force if force is not None else self.force
        manager.clean_origin_files = clean_origin_files
        return manager

    # --- Conversion domain -------------------------------------------------
    def convert(
        self,
        directory: str | None = None,
        cpu_count: int | None = None,
        iso_type: str | None = None,
        verbose: bool | None = None,
        force: bool | None = None,
        clean_origin_files: bool = False,
    ) -> dict[str, Any]:
        """Run the full parallel conversion pipeline over a directory (CONCEPT:ROM-001)."""
        manager = self._build_manager(
            directory=directory,
            iso_type=iso_type,
            verbose=verbose,
            force=force,
            clean_origin_files=clean_origin_files,
        )
        before = get_directory_size(directory=manager.directory)
        results = manager.process_parallel(cpu_count=cpu_count)
        after = get_directory_size(directory=manager.directory)
        return {
            "directory": manager.directory,
            "iso_type": manager.iso_type,
            "files_processed": len(results) if results else 0,
            "size_before_gb": round(before[3], 4),
            "size_after_gb": round(after[3], 4),
            "storage_delta_gb": round(before[3] - after[3], 4),
        }

    # alias — convert an entire directory tree
    process_directory = convert

    def process_file(
        self,
        file: str,
        iso_type: str | None = None,
        verbose: bool | None = None,
        force: bool | None = None,
    ) -> dict[str, Any]:
        """Process a single ROM file through the conversion pipeline (CONCEPT:ROM-001)."""
        manager = self._build_manager(iso_type=iso_type, verbose=verbose, force=force)
        manager.process_file(
            file=file,
            logger_name=manager.logger_name,
            logger_level=logging.WARNING,
            logger_format=manager.logger_format,
        )
        return {"file": file, "status": "processed"}

    def generate_cue(self, directory: str) -> dict[str, Any]:
        """Generate a missing ``.cue`` sheet for ``.bin`` tracks in a directory."""
        manager = self._build_manager(directory=directory)
        cue_path = manager.cue_file_generator(directory=directory)
        return {"directory": directory, "cue_file": cue_path}

    def list_files(self, directory: str, extensions: list[str] | None = None):
        """List ROM/archive files under a directory matching extensions."""
        manager = self._build_manager(directory=directory)
        exts = tuple(extensions) if extensions else manager.supported_extensions
        return manager.get_files(directory=directory, extensions=exts)

    # --- Game codes domain -------------------------------------------------
    @staticmethod
    def lookup_game_code(code: str) -> dict[str, Any]:
        """Look up a single game code -> name in the PSX code registry."""
        return {"code": code, "name": psx_codes.get(code)}

    @staticmethod
    def list_game_codes(prefix: str | None = None) -> dict[str, str]:
        """List known game codes, optionally filtered by a code prefix."""
        if prefix:
            return {k: v for k, v in psx_codes.items() if k.startswith(prefix)}
        return dict(psx_codes)

    def rename_by_game_code(self, file: str) -> dict[str, Any]:
        """Rename a file in-place using the embedded game code, if recognised."""
        renamed = RomManager.map_game_code_name(file=file, logger=logger)
        return {"original": file, "renamed": renamed, "changed": renamed != file}
