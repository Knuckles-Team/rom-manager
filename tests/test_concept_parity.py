"""Concept parity tests for rom-manager.

1. Every ``CONCEPT:ROM-*`` used in the source/tool docstrings must be registered
   in ``docs/concepts.md``.
2. Any agent-utilities pillar concept (ORCH/KG/AHE/ECO/OS) referenced locally
   must exist in the master agent-utilities registry.
"""

import os
import pathlib
import re

ROOT_DIR = str(pathlib.Path(__file__).resolve().parent.parent)
WORKSPACE_DIR = "/home/apps/workspace/agent-packages"
MASTER_OVERVIEW_PATH = os.path.join(
    WORKSPACE_DIR, "agent-utilities", "docs", "overview.md"
)
CONCEPTS_DOC = os.path.join(ROOT_DIR, "docs", "concepts.md")


def _scan_concepts(directory, prefixes=None):
    found = set()
    for root, _, files in os.walk(directory):
        if any(
            skip in root
            for skip in ("node_modules", ".venv", ".git", "__pycache__")
        ):
            continue
        for file in files:
            if not file.endswith((".py", ".md", ".json")):
                continue
            try:
                content = (pathlib.Path(root) / file).read_text(encoding="utf-8")
            except Exception:
                continue
            for m in re.findall(r"CONCEPT:([A-Z]+-\d+(?:\.\d+)?)", content):
                if prefixes is None or m.startswith(prefixes):
                    found.add(m)
    return found


def _concepts_in_doc(path):
    if not os.path.exists(path):
        return set()
    content = pathlib.Path(path).read_text(encoding="utf-8")
    return set(re.findall(r"CONCEPT:([A-Z]+-\d+(?:\.\d+)?)", content))


def test_rom_concepts_registered_in_concepts_doc():
    """All ROM-* concepts used in the codebase are documented in docs/concepts.md."""
    used = _scan_concepts(os.path.join(ROOT_DIR, "rom_manager"), prefixes=("ROM-",))
    documented = {c for c in _concepts_in_doc(CONCEPTS_DOC) if c.startswith("ROM-")}
    missing = used - documented
    assert not missing, (
        f"ROM-* concepts used in code but missing from docs/concepts.md: {missing}"
    )


def test_expected_rom_concepts_present():
    """Sanity: the two canonical ROM domains are registered."""
    documented = _concepts_in_doc(CONCEPTS_DOC)
    for cid in ("ROM-001", "ROM-002"):
        assert cid in documented, f"{cid} not registered in docs/concepts.md"


def test_pillar_concept_parity():
    """agent-utilities pillar concepts used locally must exist in the master registry."""
    if not os.path.exists(MASTER_OVERVIEW_PATH):
        return  # master registry not present in this checkout; skip
    master = set()
    for line in pathlib.Path(MASTER_OVERVIEW_PATH).read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 5:
            raw_id = parts[1].replace("*", "").strip()
            if re.match(r"^[A-Z]+-\d+(?:\.\d+)?$", raw_id):
                master.add(raw_id)

    pillars = ("ORCH-", "KG-", "AHE-", "ECO-", "OS-")
    local = {c for c in _scan_concepts(ROOT_DIR, prefixes=pillars) if not c.startswith("KG-00")}
    unregistered = local - master
    assert not unregistered, (
        f"Pillar concepts used in rom-manager but NOT in master registry: {unregistered}"
    )
