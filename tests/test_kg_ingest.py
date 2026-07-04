"""Native epistemic-graph typed-node ingestion — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_roms`` / ``ingest_platforms`` /
``ingest_collections`` seam with a fake engine client (no engine required), asserting the
txn add_node/commit + edge calls and the RomM record -> :Game/:GameSystem mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from rom_manager.kg_ingest import (
    ingest_collections,
    ingest_entities,
    ingest_platforms,
    ingest_roms,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def commit(self, txn):
        self.committed = True
        return True


class _FakeEdges:
    def __init__(self):
        self.edges = []

    def add(self, src, dst, props):
        self.edges.append((src, dst, props))


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()
        self.edges = _FakeEdges()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "type": "Game", "name": "g"},
            {"id": "b", "type": "GameSystem"},
        ],
        [{"source": "a", "target": "b", "type": "onSystem"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "rom-manager"
    assert c.txn.nodes["a"]["domain"] == "rom"
    assert c.edges.edges == [("a", "b", {"type": "onSystem"})]


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
    assert game["type"] == "Game"
    assert game["name"] == "Chrono Trigger"
    assert game["fsName"] == "Chrono Trigger.sfc"
    assert game["regions"] == "USA, Japan"
    assert game["externalToolId"] == "7"
    assert c.txn.nodes["rom:system:3"]["type"] == "GameSystem"
    assert c.txn.nodes["rom:system:3"]["slug"] == "snes"
    assert c.edges.edges == [("rom:game:7", "rom:system:3", {"type": "onSystem"})]


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
    assert sys["type"] == "GameSystem"
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
    assert c.txn.nodes["rom:collection:9"]["type"] == "GameCollection"
    assert ("rom:game:1", "rom:collection:9", {"type": "inCollection"}) in c.edges.edges
    assert ("rom:game:2", "rom:collection:9", {"type": "inCollection"}) in c.edges.edges


def test_ingest_noops_without_engine():
    # No injected client + no reachable engine -> clean no-op.
    assert ingest_entities([{"id": "a", "type": "Game"}]) is None


def test_ingest_empty_is_noop():
    assert ingest_entities([], client=_FakeClient()) is None
    assert ingest_roms([], client=_FakeClient()) is None
    assert ingest_platforms([], client=_FakeClient()) is None
    assert ingest_collections([], client=_FakeClient()) is None
