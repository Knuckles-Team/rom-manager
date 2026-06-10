"""Externalized prompt templates for ROM Manager.

CONCEPT:ROM-001, CONCEPT:ROM-002 — prompt templates are kept as files here
(rather than hardcoded in source) so they can be versioned and registered as MCP
prompts. See :func:`load_prompt`.
"""

from pathlib import Path

_PROMPT_DIR = Path(__file__).resolve().parent


def load_prompt(name: str) -> str:
    """Load an externalized prompt template by file stem (e.g. ``convert_rom``)."""
    path = _PROMPT_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8")


__all__ = ["load_prompt"]
