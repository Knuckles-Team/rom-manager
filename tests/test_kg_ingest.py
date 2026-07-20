"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_roms`` / ``ingest_platforms`` /
``ingest_collections`` seam with a fake engine client (no engine required), asserting the
single-transaction node/edge staging and commit and the RomM record -> :Game/:GameSystem mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError

from rom_manager.kg_ingest import (
    ingest_collections,
    ingest_entities,
    ingest_platforms,
    ingest_roms,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def add_edge(self, txn, source, target, props):
        self.edges.append((source, target, props))

    def commit(self, txn):
        self.committed = True
        return True


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "Game", "name": "g"},
            {"id": "b", "node_type": "GameSystem"},
        ],
        [{"source": "a", "target": "b", "relationship": "onSystem"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "rom-manager"
    assert c.txn.nodes["a"]["domain"] == "rom"
    assert c.txn.edges == [("a", "b", {"relationship": "onSystem"})]


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
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    game = c.txn.nodes["rom:game:7"]
    assert game["node_type"] == "Game"
    assert game["name"] == "Chrono Trigger"
    assert game["fsName"] == "Chrono Trigger.sfc"
    assert game["regions"] == "USA, Japan"
    assert game["externalToolId"] == "7"
    assert c.txn.nodes["rom:system:3"]["node_type"] == "GameSystem"
    assert c.txn.nodes["rom:system:3"]["slug"] == "snes"
    assert c.txn.edges == [("rom:game:7", "rom:system:3", {"relationship": "onSystem"})]


def test_ingest_roms_dedups_shared_system():
    c = _FakeClient()
    res = ingest_roms(
        [
            {"id": 1, "name": "A", "platform_id": 3, "platform_slug": "snes"},
            {"id": 2, "name": "B", "platform_id": 3, "platform_slug": "snes"},
        ],
        client=c,
        graph="__commons__",
    )
    # 2 games + 1 shared system node, 2 onSystem edges
    assert res == {"nodes": 3, "edges": 2}
    assert "rom:system:3" in c.txn.nodes


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
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    sys = c.txn.nodes["rom:system:3"]
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
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 2}
    assert c.txn.nodes["rom:collection:9"]["node_type"] == "GameCollection"
    assert ("rom:game:1", "rom:collection:9", {"relationship": "inCollection"}) in c.txn.edges
    assert ("rom:game:2", "rom:collection:9", {"relationship": "inCollection"}) in c.txn.edges


def test_retired_structural_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "a", "type": "Game"}], client=_FakeClient())


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
