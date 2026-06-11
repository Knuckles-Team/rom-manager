"""RomM API parity guard (CONCEPT:ROM-003).

Asserts the client + MCP tool map covers every operation in the vendored RomM
OpenAPI spec, and that every mapped action resolves to a real RommApi method.
"""

import json
from pathlib import Path

import pytest

from rom_manager.mcp.mcp_romm import ROMM_TOOLS
from rom_manager.romm.api import RommApi

SPEC_PATH = (
    Path(__file__).resolve().parents[1] / "rom_manager" / "romm" / "openapi.json"
)
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head"}


def _operation_count() -> int:
    spec = json.loads(SPEC_PATH.read_text())
    return sum(
        1
        for item in spec["paths"].values()
        for method in item
        if method in HTTP_METHODS
    )


@pytest.mark.concept("ROM-003")
def test_vendored_spec_present():
    assert SPEC_PATH.exists(), "RomM openapi.json must be vendored for parity checks"
    assert _operation_count() == 126


@pytest.mark.concept("ROM-003")
def test_every_action_maps_to_a_real_method():
    for _name, _tag, _summary, actions in ROMM_TOOLS:
        for action, method in actions.items():
            assert callable(getattr(RommApi, method, None)), (
                f"action '{action}' -> missing RommApi.{method}"
            )


@pytest.mark.concept("ROM-003")
def test_action_count_matches_spec_operations():
    """Full parity: one (tool, action) per RomM operation, no duplicates."""
    methods = [m for _n, _t, _s, actions in ROMM_TOOLS for m in actions.values()]
    assert len(methods) == len(set(methods)), "duplicate method mapping detected"
    assert len(methods) == _operation_count() == 126


@pytest.mark.concept("ROM-003")
def test_resource_groups_have_tools():
    expected = {
        "romm-roms",
        "romm-platforms",
        "romm-collections",
        "romm-saves",
        "romm-states",
        "romm-screenshots",
        "romm-firmware",
        "romm-users",
        "romm-tasks",
        "romm-search",
        "romm-config",
        "romm-feeds",
        "romm-devices",
        "romm-system",
    }
    tags = {tag for _n, tag, _s, _a in ROMM_TOOLS}
    assert expected == tags
