"""Unified CLI dispatch tests (CONCEPT:ROM-001, ROM-003).

Confirms the legacy on-disk converter and the RomM web commands coexist in one
``rom-manager`` entry point.
"""

import importlib

import pytest

from rom_manager.romm import cli as romm_cli

# `rom_manager.rom_manager` the attribute is the re-exported CLI function (it
# shadows the submodule in the package namespace); fetch the module explicitly.
rm = importlib.import_module("rom_manager.rom_manager")


class FakeClient:
    def __init__(self):
        self.calls = []

    def list_roms(self, **kw):
        self.calls.append(("list_roms", kw))
        return [{"id": 1}]

    def get_rom(self, id):
        self.calls.append(("get_rom", {"id": id}))
        return {"id": id}

    def stats(self):
        self.calls.append(("stats", {}))
        return {"roms": 1}

    def run_task(self, task_name):
        self.calls.append(("run_task", {"task_name": task_name}))
        return {"task": task_name}


@pytest.fixture
def fake_client(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(romm_cli, "get_romm_client", lambda: client)
    return client


@pytest.mark.concept("ROM-003")
def test_cli_flags_parsed(fake_client, capsys):
    rc = romm_cli.run_romm_cli(["roms", "list", "--platform_ids", "7", "--limit", "50"])
    assert rc == 0
    assert fake_client.calls == [("list_roms", {"platform_ids": 7, "limit": 50})]


@pytest.mark.concept("ROM-003")
def test_cli_positional_bound_by_name(fake_client):
    rc = romm_cli.run_romm_cli(["roms", "get", "123"])
    assert rc == 0
    assert fake_client.calls == [("get_rom", {"id": 123})]


@pytest.mark.concept("ROM-003")
def test_cli_alias_stats(fake_client):
    rc = romm_cli.run_romm_cli(["stats"])
    assert rc == 0
    assert fake_client.calls == [("stats", {})]


@pytest.mark.concept("ROM-003")
def test_cli_tasks_run_positional(fake_client):
    rc = romm_cli.run_romm_cli(["tasks", "run", "scan"])
    assert rc == 0
    assert fake_client.calls == [("run_task", {"task_name": "scan"})]


@pytest.mark.concept("ROM-003")
def test_cli_unknown_action_returns_2(fake_client):
    rc = romm_cli.run_romm_cli(["roms", "frobnicate"])
    assert rc == 2


@pytest.mark.concept("ROM-001")
def test_unified_cli_routes_convert_to_converter(monkeypatch):
    """The 'convert' alias and legacy flags still drive the local pipeline."""
    captured = {}

    class FakeManager:
        verbose = force = clean_origin_files = False
        directory = ""
        iso_type = "chd"

        def process_parallel(self, cpu_count=None):
            captured["ran"] = True
            return []

    monkeypatch.setattr(rm, "RomManager", FakeManager)
    monkeypatch.setattr(rm, "get_directory_size", lambda directory: (0, 0, 0, 0.0))
    rm.rom_manager(["convert", "-d", "/games"])
    assert captured.get("ran") is True


@pytest.mark.concept("ROM-003")
def test_unified_cli_routes_romm_resource(monkeypatch):
    called = {}

    def fake_run(argv):
        called["argv"] = argv
        return 0

    monkeypatch.setattr("rom_manager.romm.cli.run_romm_cli", fake_run)
    with pytest.raises(SystemExit) as exc:
        rm.rom_manager(["roms", "list"])
    assert exc.value.code == 0
    assert called["argv"] == ["roms", "list"]
