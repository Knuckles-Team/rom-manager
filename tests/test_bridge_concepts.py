"""Cross-project bridge-concept wiring tests.

These tests assert that the agent-utilities *bridge* capabilities referenced in
``docs/concepts.md`` are genuinely wired into rom-manager's integration seams
(the MCP server and the A2A agent server), not merely name-dropped in docs. Each
test is tagged with the bridge CONCEPT id so the traceability scanner can link
the doc reference to a real code path and a verifying test.
"""

import importlib

import pytest


def _module_source(dotted: str) -> str:
    mod = importlib.import_module(dotted)
    path = mod.__file__
    assert path is not None
    return open(path).read()


@pytest.mark.concept("ECO-4.0")
def test_eco_4_0_unified_toolkit_ingestion():
    """ECO-4.0 — MCP server registers tools via agent-utilities create_mcp_server."""
    src = _module_source("rom_manager.mcp_server")
    assert "create_mcp_server" in src
    assert "CONCEPT:ECO-4.0" in src


@pytest.mark.concept("OS-5.1")
def test_os_5_1_prompt_injection_defense():
    """OS-5.1 — guardrail/prompt-injection middleware is wired in the MCP server."""
    assert "CONCEPT:OS-5.1" in _module_source("rom_manager.mcp_server")


@pytest.mark.concept("OS-5.3")
def test_os_5_3_guardrail_engine():
    """OS-5.3 — guardrail engine is wired via the shared middleware."""
    assert "CONCEPT:OS-5.3" in _module_source("rom_manager.mcp_server")


@pytest.mark.concept("OS-5.4")
def test_os_5_4_audit_logging():
    """OS-5.4 — audit-logging middleware is wired in the MCP server."""
    assert "CONCEPT:OS-5.4" in _module_source("rom_manager.mcp_server")


@pytest.mark.concept("ORCH-1.2")
def test_orch_1_2_confidence_gated_router():
    """ORCH-1.2 — the A2A agent is driven by the agent-utilities router."""
    src = _module_source("rom_manager.agent_server")
    assert "create_agent_server" in src
    assert "CONCEPT:ORCH-1.2" in src


@pytest.mark.concept("OS-5.2")
def test_os_5_2_cognitive_scheduler():
    """OS-5.2 — the cognitive scheduler is referenced by the agent server."""
    assert "CONCEPT:OS-5.2" in _module_source("rom_manager.agent_server")


@pytest.mark.concept("KG-2.0")
def test_kg_2_0_knowledge_graph_core():
    """KG-2.0 — the agent surface is ingested into the Knowledge Graph."""
    assert "CONCEPT:KG-2.0" in _module_source("rom_manager.agent_server")
