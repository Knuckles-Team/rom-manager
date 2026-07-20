"""Tests for the archive extraction / cue-generation layer.

CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool — verifies archive-format detection, file discovery, track
index padding, and ``.cue`` sheet synthesis without requiring the native
``patool`` extension or the external conversion binaries.
"""

import io
import stat
import tarfile
import zipfile

import pytest

from rom_manager import archives


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
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
    """Happy + negative + boundary: archive extension detection (CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool)."""
    assert archives.is_archive(filename) is expected


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
@pytest.mark.parametrize(
    "number,expected",
    [(1, "01"), (2, "02"), (9, "09"), (10, "10"), (99, "99")],
)
def test_pad_leading_zero(number, expected):
    """Boundary: track-index zero padding rolls correctly (CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool)."""
    assert archives.pad_leading_zero(number) == expected


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
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


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
def test_cue_file_generator_single_track(tmp_path):
    """Happy path: a single .bin yields a one-track MODE2/2352 cue sheet."""
    (tmp_path / "game.bin").write_text("data")
    cue_path = archives.cue_file_generator(directory=str(tmp_path))

    assert cue_path.endswith("game.cue")
    content = open(cue_path).read()
    assert 'FILE "game.bin" BINARY' in content
    assert "TRACK 01 MODE2/2352" in content
    assert "AUDIO" not in content  # only one track


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
def test_cue_file_generator_multi_track(tmp_path):
    """Happy path: extra .bin tracks become numbered AUDIO tracks."""
    (tmp_path / "game.bin").write_text("d")
    (tmp_path / "game (Track 2).bin").write_text("d")
    cue_path = archives.cue_file_generator(directory=str(tmp_path))
    content = open(cue_path).read()
    assert "TRACK 01 MODE2/2352" in content
    assert "TRACK 02 AUDIO" in content


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
def test_cue_file_generator_idempotent(tmp_path):
    """Boundary: an existing cue file is not overwritten."""
    (tmp_path / "game.bin").write_text("d")
    cue = tmp_path / "game.cue"
    cue.write_text("PRE-EXISTING")
    archives.cue_file_generator(directory=str(tmp_path))
    assert cue.read_text() == "PRE-EXISTING"


@pytest.mark.concept("RO-OS.identity.verifies-chdman-dolphin-tool")
def test_extract_archive_rejects_parent_traversal(tmp_path):
    archive = tmp_path / "malicious.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../outside.txt", "owned")
    output = tmp_path / "output"
    with pytest.raises(archives.ArchiveSafetyError, match="extraction root"):
        archives.extract_archive(str(archive), str(output))
    assert not (tmp_path / "outside.txt").exists()


def test_extract_archive_rejects_zip_symlink(tmp_path):
    archive = tmp_path / "link.zip"
    member = zipfile.ZipInfo("link")
    member.create_system = 3
    member.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(member, "../../outside")
    with pytest.raises(archives.ArchiveSafetyError, match="links"):
        archives.extract_archive(str(archive), str(tmp_path / "output"))


def test_extract_archive_rejects_tar_link(tmp_path):
    archive = tmp_path / "link.tar"
    with tarfile.open(archive, "w") as tf:
        member = tarfile.TarInfo("link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        tf.addfile(member)
    with pytest.raises(archives.ArchiveSafetyError, match="links"):
        archives.extract_archive(str(archive), str(tmp_path / "output"))


def test_extract_archive_enforces_total_size_before_writing(monkeypatch, tmp_path):
    archive = tmp_path / "large.tar"
    payload = b"12345"
    with tarfile.open(archive, "w") as tf:
        member = tarfile.TarInfo("file.bin")
        member.size = len(payload)
        tf.addfile(member, io.BytesIO(payload))
    monkeypatch.setenv("ROM_MANAGER_ARCHIVE_MAX_UNCOMPRESSED_BYTES", "4")
    with pytest.raises(archives.ArchiveSafetyError, match="size limit"):
        archives.extract_archive(str(archive), str(tmp_path / "output"))


def test_extract_archive_rejects_opaque_external_formats(tmp_path):
    archive = tmp_path / "game.7z"
    archive.write_bytes(b"not relevant")
    with pytest.raises(archives.ArchiveSafetyError, match="prevalidated"):
        archives.extract_archive(str(archive), str(tmp_path / "output"))
