"""Tests for the game-code naming / rename layer.

CONCEPT:ROM-002 — verifies game-code lookup, title sanitisation, and in-place
renaming behaviour against the embedded PSX registry.
"""

import logging
import os

import pytest

from rom_manager import naming
from rom_manager.game_codes import psx_codes

_LOG = logging.getLogger("test_naming")


@pytest.mark.concept("ROM-002")
def test_lookup_known_code():
    """Happy path: a known code resolves to its title."""
    code = next(iter(psx_codes))
    assert naming.lookup_game_code(code) == psx_codes[code]


@pytest.mark.concept("ROM-002")
def test_lookup_unknown_code_returns_none():
    """Negative: an unknown code resolves to None."""
    assert naming.lookup_game_code("NOPE-99999") is None


@pytest.mark.concept("ROM-002")
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("CLEAN TITLE", "CLEAN TITLE"),
        ('BAD:NAME/HERE', "BADNAMEHERE"),
        ("a<b>c|d?e", "abcde"),
    ],
)
def test_sanitize_title(raw, expected):
    """Boundary: filesystem-illegal characters are stripped (CONCEPT:ROM-002)."""
    assert naming.sanitize_title(raw) == expected


@pytest.mark.concept("ROM-002")
def test_map_game_code_name_renames(tmp_path):
    """Happy path: a file whose name embeds a known code is renamed to the title."""
    code = next(iter(psx_codes))
    title = naming.sanitize_title(psx_codes[code])
    src = tmp_path / f"{code}.chd"
    src.write_text("rom")

    result = naming.map_game_code_name(file=str(src), logger=_LOG)
    assert os.path.basename(result) == f"{title} - {code}.chd"
    assert os.path.exists(result)


@pytest.mark.concept("ROM-002")
def test_map_game_code_name_no_match_is_noop(tmp_path):
    """Negative: a file with no recognised code is left untouched."""
    src = tmp_path / "random-file.chd"
    src.write_text("rom")
    result = naming.map_game_code_name(file=str(src), logger=_LOG)
    assert result == str(src)


@pytest.mark.concept("ROM-002")
def test_map_game_code_name_skips_existing_target(tmp_path):
    """Boundary: an existing target name prevents an overwriting rename."""
    code = next(iter(psx_codes))
    title = naming.sanitize_title(psx_codes[code])
    src = tmp_path / f"{code}.chd"
    src.write_text("rom")
    # Pre-create the destination so the rename must be skipped.
    (tmp_path / f"{title} - {code}.chd").write_text("existing")

    result = naming.map_game_code_name(file=str(src), logger=_LOG)
    # Source path unchanged because destination already existed.
    assert result == str(src)
    assert src.exists()
