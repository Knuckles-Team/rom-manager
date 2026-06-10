"""Tests for the conversion command-building / runner-seam layer.

CONCEPT:ROM-001 — verifies chdman/dolphin-tool command construction and that the
injected runner seam is honoured, so the conversion logic is testable without
the real external binaries.
"""

import pytest

from rom_manager.conversion import Converter, build_convert_command
from rom_manager.rom_manager import RomManager


@pytest.mark.concept("ROM-001")
def test_build_chd_createcd_for_cue():
    """Happy path: a .cue input builds a chdman createcd command."""
    cmd = build_convert_command("game.cue", "out.chd", is_rvz=False)
    assert cmd[:2] == ["chdman", "createcd"]
    assert "-f" not in cmd


@pytest.mark.concept("ROM-001")
def test_build_chd_createdvd_for_iso():
    """Happy path: a non-cue input builds chdman createdvd."""
    cmd = build_convert_command("game.iso", "out.chd", is_rvz=False)
    assert cmd[:2] == ["chdman", "createdvd"]


@pytest.mark.concept("ROM-001")
def test_build_chd_force_appends_flag():
    """Boundary: force=True appends -f to the chdman command."""
    cmd = build_convert_command("game.iso", "out.chd", is_rvz=False, force=True)
    assert cmd[-1] == "-f"


@pytest.mark.concept("ROM-001")
def test_build_rvz_uses_dolphin_tool():
    """Happy path: an RVZ target builds a dolphin-tool convert command."""
    cmd = build_convert_command("game.wbfs", "out.rvz", is_rvz=True)
    assert cmd[:2] == ["dolphin-tool", "convert"]
    assert cmd[-2:] == ["-l", "22"]


@pytest.mark.concept("ROM-001")
def test_converter_invokes_injected_runner(tmp_path):
    """The runner seam is called when the output does not yet exist."""
    calls = []

    def fake_runner(command, verbose=False, logger=None):
        calls.append(command)

    converter = Converter(runner=fake_runner)
    out = str(tmp_path / "out.chd")
    converter.convert("game.iso", out, is_rvz=False)
    assert len(calls) == 1
    assert calls[0][0] == "chdman"


@pytest.mark.concept("ROM-001")
def test_converter_skips_when_output_exists(tmp_path):
    """Negative: an already-converted output short-circuits the runner."""
    calls = []
    existing = tmp_path / "out.chd"
    existing.write_text("done")

    converter = Converter(runner=lambda **k: calls.append(k))
    converter.convert("game.iso", str(existing), is_rvz=False)
    assert calls == []


@pytest.mark.concept("ROM-001")
def test_rom_manager_runner_seam_used(monkeypatch, tmp_path):
    """The RomManager orchestrator honours its injected ``_runner`` seam."""
    calls = []
    manager = RomManager()
    manager._runner = lambda command, verbose=False, logger=None: calls.append(command)
    manager.directory = str(tmp_path)

    iso = tmp_path / "plain.iso"
    iso.write_text("x")
    manager.process_file(
        file=str(iso),
        logger_name="t",
        logger_level=40,
        logger_format="%(message)s",
    )
    # The fake runner was used instead of the real chdman binary.
    assert calls and calls[0][0] == "chdman"
