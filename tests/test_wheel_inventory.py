"""The published wheel preserves tracked resources and excludes bytecode."""

import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile


def _clean_build_source(root, destination):
    paths = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
        .decode()
        .split("\0")
    )
    for name in filter(None, paths):
        source = root / name
        if source.is_file():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    cache = destination / "rom_manager/prompts/__pycache__/unshipped.pyc"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(b"bytecode must not enter a wheel")


def test_wheel_matches_the_full_tracked_package_inventory(tmp_path):
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", "--", "rom_manager/"],
        cwd=root,
        text=True,
    ).splitlines()
    source = tmp_path / "source"
    _clean_build_source(root, source)
    output = tmp_path / "dist"
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(output)], cwd=source, check=True
    )
    with ZipFile(next(output.glob("*.whl"))) as wheel:
        payload = {
            name
            for name in wheel.namelist()
            if name.startswith("rom_manager/") and not name.endswith("/")
        }
        assert payload == set(tracked)
        for name in payload:
            assert wheel.read(name) == (root / name).read_bytes(), name
