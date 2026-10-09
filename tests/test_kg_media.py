"""Native epistemic-graph blob ingestion (cover art / ROM bytes) — Wire-First coverage.

Exercises ``ingest_cover`` / ``ingest_rom_file`` against a fake ``agent_connector_sdk.ingest``
transport (no engine required), asserting the stored media asset's bytes, provenance
``extra``, and that missing bytes / no reachable engine both no-op cleanly.
CONCEPT:AU-KG.ingest.list-durable-media.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import KnowledgeIngest

from rom_manager.kg_media import ingest_cover, ingest_rom_file


class _FakeTransport:
    def __init__(self) -> None:
        self.stored_blobs: list[bytes] = []
        self.requests: list[Any] = []

    async def source_status(self, _connector: str, _stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def store_blob(self, data: bytes) -> str:
        self.stored_blobs.append(data)
        return "deadbeefcafef00d"

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        media_records = [
            r for r in request.records if r.record_id == "blob:deadbeefcafef00d"
        ]
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
            raw_admissions=[
                SimpleNamespace(
                    record_id=record.record_id,
                    raw_digest="deadbeefcafef00d",
                    deduplicated=False,
                )
                for record in media_records
            ],
        )


class _UnavailableTransport:
    async def source_status(self, _connector: str, _stream: str) -> Any:
        raise RuntimeError("epistemic-graph is unreachable")

    async def submit(self, _request: Any) -> Any:
        raise RuntimeError("epistemic-graph is unreachable")

    async def store_blob(self, _data: bytes) -> str:
        raise RuntimeError("epistemic-graph is unreachable")


@pytest.fixture
def ingest() -> tuple[KnowledgeIngest, _FakeTransport]:
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


@pytest.mark.asyncio
async def test_ingest_cover_stores_image_with_provenance(ingest):
    service, transport = ingest
    res = await ingest_cover(
        b"\x89PNG...",
        rom={"id": 7, "name": "Chrono Trigger", "platform_slug": "snes"},
        ingest=service,
    )
    assert res == {
        "asset_id": "blob:deadbeefcafef00d",
        "digest": "deadbeefcafef00d",
        "size_bytes": len(b"\x89PNG..."),
        "media_type": "image",
    }
    assert transport.stored_blobs == [b"\x89PNG..."]
    request = transport.requests[0]
    media_record = next(
        r for r in request.records if r.record_id == "blob:deadbeefcafef00d"
    )
    assert media_record.payload["game_id"] == "rom:game:7"
    assert media_record.payload["platform_slug"] == "snes"
    assert "cover" in media_record.payload["name"]


@pytest.mark.asyncio
async def test_ingest_rom_file_stores_file_blob(ingest):
    service, transport = ingest
    res = await ingest_rom_file(
        b"ROMDATA",
        rom={"id": 7, "fs_name": "Chrono Trigger.sfc"},
        ingest=service,
    )
    assert res is not None
    assert res["media_type"] == "file"
    request = transport.requests[0]
    media_record = request.records[0]
    assert media_record.payload["name"] == "Chrono Trigger.sfc"
    assert media_record.payload["game_id"] == "rom:game:7"


@pytest.mark.asyncio
async def test_ingest_cover_noops_without_data(ingest):
    service, transport = ingest
    assert await ingest_cover(b"", ingest=service) is None
    assert await ingest_rom_file(b"", ingest=service) is None
    assert transport.stored_blobs == []


@pytest.mark.asyncio
async def test_no_engine_is_noop():
    # No injected store + no reachable engine -> clean no-op.
    service = KnowledgeIngest(_UnavailableTransport(), loop=None)
    assert await ingest_cover(b"data", ingest=service) is None
