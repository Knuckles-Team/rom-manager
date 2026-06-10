#!/usr/bin/python
"""Pydantic models for ROM Manager MCP tool inputs/outputs.

CONCEPT:ROM-001, CONCEPT:ROM-002 — the model layer: request/response schemas for
the conversion and game-codes tool domains.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    """Parameters for a directory/file ROM conversion."""

    directory: str | None = Field(
        default=None,
        description="Directory of ROMs to process. Defaults to ROM_DIRECTORY/cwd.",
    )
    file: str | None = Field(
        default=None,
        description="A single ROM/archive file to process (overrides directory).",
    )
    cpu_count: int | None = Field(
        default=None,
        description="Max CPUs for parallel processing. Defaults to a derived value.",
    )
    iso_type: Literal["chd", "rvz"] = Field(
        default="chd",
        description="Conversion target: 'chd' (chdman) or 'rvz' (dolphin-tool).",
    )
    verbose: bool = Field(default=False, description="Emit verbose conversion output.")
    force: bool = Field(
        default=False, description="Force overwrite of existing converted files."
    )
    clean_origin_files: bool = Field(
        default=False,
        description="Delete original source files after a successful conversion.",
    )


class ConvertResult(BaseModel):
    """Result of a conversion run."""

    directory: str
    iso_type: str
    files_processed: int = 0
    size_before_gb: float = 0.0
    size_after_gb: float = 0.0
    storage_delta_gb: float = 0.0


class GenerateCueRequest(BaseModel):
    """Parameters for generating a .cue sheet from .bin tracks."""

    directory: str = Field(description="Directory containing .bin track files.")


class GenerateCueResult(BaseModel):
    directory: str
    cue_file: str


class GameCodeLookup(BaseModel):
    """A single game code -> name mapping result."""

    code: str = Field(description="The game/serial code, e.g. 'SLUS-00594'.")
    name: str | None = Field(
        default=None, description="The resolved game name, if known."
    )


class RenameResult(BaseModel):
    """Result of renaming a file by its embedded game code."""

    original: str
    renamed: str
    changed: bool
