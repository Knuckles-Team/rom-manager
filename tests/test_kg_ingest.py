"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_roms`` / ``ingest_platforms`` /
``ingest_collections`` seam with a fake engine client (no engine required), asserting the
single-transaction node/edge staging and commit and the RomM record -> :Game/:GameSystem mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.security.brain_context import ActorContext, use_actor
from agent_utilities.models.company_brain import ActorType
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session

from rom_manager.kg_ingest import (
    ingest_collections,
    ingest_entities,
    ingest_platforms,
    ingest_roms,
)


@pytest.fixture(autouse=True)
def _governed_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "Game", "name": "g"},
            {"id": "b", "node_type": "GameSystem"},
        ],
        [{"source": "a", "target": "b", "relationship": "onSystem"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "rom-manager"
    assert c.nodes.values["a"]["domain"] == "rom"
    assert c.changes.edges == [("a", "b", {"relationship": "onSystem"})]


def test_ingest_roms_maps_game_and_system():
    c = _FakeClient()
    res = ingest_roms(
        [
            {
                "id": 7,
                "name": "Chrono Trigger",
                "slug": "chrono-trigger",
                "fs_name": "Chrono Trigger.sfc",
                "fs_size_bytes": 4194304,
                "regions": ["USA", "Japan"],
                "platform_id": 3,
                "platform_display_name": "Super Nintendo",
                "platform_slug": "snes",
            }
        ],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    game = c.nodes.values["rom:game:7"]
    assert game["node_type"] == "Game"
    assert game["name"] == "Chrono Trigger"
    assert game["fsName"] == "Chrono Trigger.sfc"
    assert game["regions"] == "USA, Japan"
    assert game["externalToolId"] == "7"
    assert c.nodes.values["rom:system:3"]["node_type"] == "GameSystem"
    assert c.nodes.values["rom:system:3"]["slug"] == "snes"
    assert c.changes.edges == [("rom:game:7", "rom:system:3", {"relationship": "onSystem"})]


def test_ingest_roms_dedups_shared_system():
    c = _FakeClient()
    res = ingest_roms(
        [
            {"id": 1, "name": "A", "platform_id": 3, "platform_slug": "snes"},
            {"id": 2, "name": "B", "platform_id": 3, "platform_slug": "snes"},
        ],
        client=c,
    )
    # 2 games + 1 shared system node, 2 onSystem edges
    assert res == {"nodes": 3, "edges": 2}
    assert "rom:system:3" in c.nodes.values


def test_ingest_platforms_maps_system():
    c = _FakeClient()
    res = ingest_platforms(
        [
            {
                "id": 3,
                "name": "snes",
                "display_name": "Super Nintendo",
                "slug": "snes",
                "rom_count": 42,
            }
        ],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    sys = c.nodes.values["rom:system:3"]
    assert sys["node_type"] == "GameSystem"
    assert sys["name"] == "Super Nintendo"
    assert sys["romCount"] == 42
    assert sys["externalToolId"] == "3"


def test_ingest_collections_maps_collection_and_membership():
    c = _FakeClient()
    res = ingest_collections(
        [
            {
                "id": 9,
                "name": "Favourites",
                "rom_count": 2,
                "roms": [{"id": 1}, {"id": 2}],
            }
        ],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 2}
    assert c.nodes.values["rom:collection:9"]["node_type"] == "GameCollection"
    assert ("rom:game:1", "rom:collection:9", {"relationship": "inCollection"}) in c.changes.edges
    assert ("rom:game:2", "rom:collection:9", {"relationship": "inCollection"}) in c.changes.edges


def test_retired_structural_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "a", "type": "Game"}], client=_FakeClient())


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
