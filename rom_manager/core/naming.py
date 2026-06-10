#!/usr/bin/env python
"""ROM filename normalization via the embedded game-code registry.

CONCEPT:ROM-002 — Game Codes / Naming. Resolves a serial/game code embedded in a
ROM filename to its canonical title and renames the file in-place. Split out of
the former ``rom_manager`` god-module so the naming responsibility (lookup +
rename) is isolated, independently testable, and free of conversion/archive
concerns.
"""

import logging
import os
import re

from rom_manager.game_codes import psx_codes

# Characters that are illegal in filenames on common filesystems.
_ILLEGAL_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

_NULL_LOGGER = logging.getLogger("rom_manager.naming")
_NULL_LOGGER.addHandler(logging.NullHandler())


def sanitize_title(title: str) -> str:
    """Strip filesystem-illegal characters from a resolved game title.

    CONCEPT:ROM-002 — keeps generated filenames portable across POSIX/Windows.
    """
    return _ILLEGAL_FILENAME_CHARS.sub("", title)


def lookup_game_code(code: str) -> str | None:
    """Resolve a single game/serial ``code`` to its title, or ``None``."""
    return psx_codes.get(code)


def map_game_code_name(file, logger=None) -> str:
    """Rename ``file`` using the first known game code found in its basename.

    CONCEPT:ROM-002 — scans the filename against the PSX code registry; when a
    code is matched, renames the file to ``"<Title> - <CODE><ext>"``. Returns
    the (possibly updated) path. Behaviour is preserved exactly from the
    original ``RomManager.map_game_code_name``.
    """
    log = logger or _NULL_LOGGER
    log.info("Scanning the filename for known ROM codes")
    for key, value in psx_codes.items():
        if key in os.path.basename(file):
            file_path = os.path.dirname(file)
            file_extension = os.path.splitext(file)[1]
            cleaned_value = sanitize_title(value)
            new_file = os.path.join(
                file_path, f"{cleaned_value} - {key}{file_extension}"
            )
            if file != new_file and not os.path.exists(new_file):
                os.rename(file, new_file)
                file = new_file
            log.info(f"The string contains the key: {key}")
    return file
