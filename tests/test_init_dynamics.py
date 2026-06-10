"""Verify package initialization and version metadata."""

import importlib
import pathlib

import pytest


def _get_pkg_name():
    test_dir = pathlib.Path(__file__).resolve().parent
    project_dir = test_dir.parent
    return project_dir.name.replace("-", "_")


@pytest.fixture
def pkg_name():
    return _get_pkg_name()


@pytest.mark.concept("ROM-001")
def test_package_importable(pkg_name):
    mod = importlib.import_module(pkg_name)
    assert mod is not None


@pytest.mark.concept("ROM-001")
def test_version_exists(pkg_name):
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    if version is None:
        from importlib.metadata import version as get_version

        version = get_version(pkg_name.replace("_", "-"))
    assert version is not None, f"{pkg_name} has no __version__"


@pytest.mark.concept("ROM-001")
def test_version_format(pkg_name):
    mod = importlib.import_module(pkg_name)
    version = getattr(mod, "__version__", None)
    if version is None:
        from importlib.metadata import version as get_version

        version = get_version(pkg_name.replace("_", "-"))
    parts = version.split(".")
    assert len(parts) >= 2, f"Version {version} should have at least major.minor"


@pytest.mark.concept("ROM-001")
def test_core_exports(pkg_name):
    """The real pipeline callables must remain importable from the package."""
    mod = importlib.import_module(pkg_name)
    for name in ("RomManager", "rom_manager", "psx_codes"):
        assert hasattr(mod, name), f"{pkg_name} should export {name}"
