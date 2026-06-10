"""Tests for the archive extraction / cue-generation layer.

CONCEPT:ROM-001 — verifies archive-format detection, file discovery, track
index padding, and ``.cue`` sheet synthesis without requiring the native
``patool`` extension or the external conversion binaries.
"""

import pytest

from rom_manager import archives


@pytest.mark.concept("ROM-001")
@pytest.mark.parametrize(
    "filename,expected",
    [
        ("game.7z", True),
        ("game.ZIP", True),  # case-insensitive
        ("disc.tar.gz", True),
        ("disc.rar", True),
        ("image.iso", False),  # not an archive container
        ("track.bin", False),
        ("plain", False),  # boundary: no extension
    ],
)
def test_is_archive_detection(filename, expected):
    """Happy + negative + boundary: archive extension detection (CONCEPT:ROM-001)."""
    assert archives.is_archive(filename) is expected


@pytest.mark.concept("ROM-001")
@pytest.mark.parametrize(
    "number,expected",
    [(1, "01"), (2, "02"), (9, "09"), (10, "10"), (99, "99")],
)
def test_pad_leading_zero(number, expected):
    """Boundary: track-index zero padding rolls correctly (CONCEPT:ROM-001)."""
    assert archives.pad_leading_zero(number) == expected


@pytest.mark.concept("ROM-001")
def test_get_files_filters_by_extension(tmp_path):
    """Happy path: get_files returns only matching extensions, recursively."""
    (tmp_path / "a.bin").write_text("x")
    (tmp_path / "b.cue").write_text("x")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.bin").write_text("x")
    (sub / "d.txt").write_text("x")

    found = archives.get_files(directory=str(tmp_path), extensions=[".bin"])
    assert sorted(f.split("/")[-1] for f in found) == ["a.bin", "c.bin"]


@pytest.mark.concept("ROM-001")
def test_cue_file_generator_single_track(tmp_path):
    """Happy path: a single .bin yields a one-track MODE2/2352 cue sheet."""
    (tmp_path / "game.bin").write_text("data")
    cue_path = archives.cue_file_generator(directory=str(tmp_path))

    assert cue_path.endswith("game.cue")
    content = open(cue_path).read()
    assert 'FILE "game.bin" BINARY' in content
    assert "TRACK 01 MODE2/2352" in content
    assert "AUDIO" not in content  # only one track


@pytest.mark.concept("ROM-001")
def test_cue_file_generator_multi_track(tmp_path):
    """Happy path: extra .bin tracks become numbered AUDIO tracks."""
    (tmp_path / "game.bin").write_text("d")
    (tmp_path / "game (Track 2).bin").write_text("d")
    cue_path = archives.cue_file_generator(directory=str(tmp_path))
    content = open(cue_path).read()
    assert "TRACK 01 MODE2/2352" in content
    assert "TRACK 02 AUDIO" in content


@pytest.mark.concept("ROM-001")
def test_cue_file_generator_idempotent(tmp_path):
    """Boundary: an existing cue file is not overwritten."""
    (tmp_path / "game.bin").write_text("d")
    cue = tmp_path / "game.cue"
    cue.write_text("PRE-EXISTING")
    archives.cue_file_generator(directory=str(tmp_path))
    assert cue.read_text() == "PRE-EXISTING"


@pytest.mark.concept("ROM-001")
def test_extract_archive_missing_patool_raises(monkeypatch, tmp_path):
    """Negative: extraction without the native extra raises a helpful ImportError."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "patoolib":
            raise ImportError("no patool")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match="rom-manager\\[native\\]"):
        archives.extract_archive("a.zip", str(tmp_path))
