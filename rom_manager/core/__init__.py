"""Domain (core) layer for ROM Manager.

CONCEPT:ROM-001, CONCEPT:ROM-002 — the pure pipeline responsibilities, free of
transport/CLI concerns: archive handling, conversion command construction, and
game-code naming. The top-level orchestrator (:class:`rom_manager.rom_manager.
RomManager`) composes these. Thin re-export shims at the package root
(``rom_manager.archives`` etc.) preserve the historical import paths.
"""

from rom_manager.core import archives, conversion, naming

__all__ = ["archives", "conversion", "naming"]
