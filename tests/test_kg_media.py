"""Native epistemic-graph blob ingestion (cover art / ROM bytes) — Wire-First coverage.

Exercises ``ingest_cover`` / ``ingest_rom_file`` with a fake ``MediaStore`` (no engine),
asserting the ``store_media`` call shape + provenance ``extra``. CONCEPT:AU-KG.ingest.list-durable-media.
"""

from __future__ import annotations

from rom_manager.kg_media import ingest_cover, ingest_rom_file


class _Stored:
    def __init__(self):
        self.asset_id = "asset-1"
        self.digest = "deadbeefcafef00d"


class _FakeStore:
    def __init__(self):
        self.calls = []

    def store_media(self, data, **kwargs):
        self.calls.append((data, kwargs))
        return _Stored()


def test_ingest_cover_stores_image_with_provenance():
    store = _FakeStore()
    res = ingest_cover(
        b"\x89PNG...",
        rom={"id": 7, "name": "Chrono Trigger", "platform_slug": "snes"},
        media_store=store,
    )
    assert res == {
        "asset_id": "asset-1",
        "digest": "deadbeefcafef00d",
        "size_bytes": len(b"\x89PNG..."),
        "media_type": "image",
    }
    data, kwargs = store.calls[0]
    assert kwargs["media_type"] == "image"
    assert kwargs["source"] == "rom-manager"
    assert kwargs["extra"]["game_id"] == "rom:game:7"
    assert kwargs["extra"]["platform_slug"] == "snes"
    assert "cover" in kwargs["name"]


def test_ingest_rom_file_stores_file_blob():
    store = _FakeStore()
    res = ingest_rom_file(
        b"ROMDATA",
        rom={"id": 7, "fs_name": "Chrono Trigger.sfc"},
        media_store=store,
    )
    assert res["media_type"] == "file"
    _, kwargs = store.calls[0]
    assert kwargs["media_type"] == "file"
    assert kwargs["name"] == "Chrono Trigger.sfc"
    assert kwargs["extra"]["game_id"] == "rom:game:7"


def test_ingest_cover_noops_without_data_or_store():
    assert ingest_cover(b"", media_store=_FakeStore()) is None
    assert ingest_rom_file(b"", media_store=_FakeStore()) is None
    # No injected store + no reachable engine -> clean no-op.
    assert ingest_cover(b"data") is None
