"""Native epistemic-graph typed-node ingestion -- Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_roms`` / ``ingest_platforms`` /
``ingest_collections`` seam against a fake ``agent_connector_sdk.ingest`` transport (no
engine required). The real SDK request builder (``agent_connector_sdk.ingest.request
.build_request``) still runs, so a malformed change set is still caught by the SDK's own
contract, not re-derived here; only the final network commit is faked.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest
from epistemic_graph.generated.source_ingestion import SourceIngestionRequest

from rom_manager.kg_ingest import (
    ingest_collections,
    ingest_entities,
    ingest_platforms,
    ingest_roms,
)


class _FakeTransport:
    """Records every submitted request; no epistemic-graph engine required."""

    def __init__(self) -> None:
        self.requests: list[SourceIngestionRequest] = []

    async def source_status(self, _connector: str, _stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: SourceIngestionRequest) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, _data: bytes) -> str:
        raise AssertionError("rom-manager typed-node ingestion carries no media")


@pytest.fixture
def ingest() -> tuple[KnowledgeIngest, _FakeTransport]:
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


@pytest.mark.asyncio
async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "Game", "name": "A"},
            {"id": "b", "node_type": "GameSystem"},
        ],
        [{"source": "a", "target": "b", "relationship": "onSystem"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    request = transport.requests[0]
    record_ids = {record.record_id for record in request.records}
    assert record_ids == {"a", "b"}
    a_record = next(r for r in request.records if r.record_id == "a")
    assert a_record.payload["name"] == "A"
    assert request.relationships[0].relation_reference.endswith(
        "resources/Game/relations/onSystem"
    )


@pytest.mark.asyncio
async def test_ingest_roms_maps_game_and_system(ingest):
    service, transport = ingest
    res = await ingest_roms(
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
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    request = transport.requests[0]
    game = next(r for r in request.records if r.record_id == "rom:game:7")
    assert game.payload["name"] == "Chrono Trigger"
    assert game.payload["fsName"] == "Chrono Trigger.sfc"
    assert game.payload["regions"] == "USA, Japan"
    assert game.payload["externalToolId"] == "7"
    system = next(r for r in request.records if r.record_id == "rom:system:3")
    assert system.payload["slug"] == "snes"
    assert request.relationships[0].relation_reference.endswith(
        "resources/Game/relations/onSystem"
    )


@pytest.mark.asyncio
async def test_ingest_roms_dedups_shared_system(ingest):
    service, transport = ingest
    res = await ingest_roms(
        [
            {"id": 1, "name": "A", "platform_id": 3, "platform_slug": "snes"},
            {"id": 2, "name": "B", "platform_id": 3, "platform_slug": "snes"},
        ],
        ingest=service,
    )
    # 2 games + 1 shared system node, 2 onSystem edges
    assert res == {"nodes": 3, "edges": 2}
    request = transport.requests[0]
    assert any(r.record_id == "rom:system:3" for r in request.records)
    assert sum(1 for r in request.records if r.record_id == "rom:system:3") == 1


@pytest.mark.asyncio
async def test_ingest_platforms_maps_system(ingest):
    service, transport = ingest
    res = await ingest_platforms(
        [
            {
                "id": 3,
                "name": "snes",
                "display_name": "Super Nintendo",
                "slug": "snes",
                "rom_count": 42,
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    request = transport.requests[0]
    system = next(r for r in request.records if r.record_id == "rom:system:3")
    assert system.payload["name"] == "Super Nintendo"
    assert system.payload["romCount"] == 42
    assert system.payload["externalToolId"] == "3"


@pytest.mark.asyncio
async def test_ingest_collections_maps_collection_and_membership(ingest):
    service, transport = ingest
    res = await ingest_collections(
        [
            {
                "id": 9,
                "name": "Favourites",
                "rom_count": 2,
                "roms": [{"id": 1}, {"id": 2}],
            }
        ],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 2}
    request = transport.requests[0]
    assert next(r for r in request.records if r.record_id == "rom:collection:9")
    relation_pairs = {
        (rel.source.record_id, rel.target.record_id) for rel in request.relationships
    }
    assert ("rom:game:1", "rom:collection:9") in relation_pairs
    assert ("rom:game:2", "rom:collection:9") in relation_pairs


@pytest.mark.asyncio
async def test_retired_structural_alias_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="node_type"):
        await ingest_entities([{"id": "a", "type": "Game"}], ingest=service)


@pytest.mark.asyncio
async def test_empty_native_ingest_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)
