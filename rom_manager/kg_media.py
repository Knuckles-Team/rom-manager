"""Native epistemic-graph blob ingestion for ROM cover art and ROM binaries.

CONCEPT:AU-KG.ingest.list-durable-media. When a live epistemic-graph engine is reachable,
a game's cover / box art (or a ROM file itself) is stored as a content-addressed **blob**
with a ``:AssetOccurrence`` graph node (carrying its RomM metadata) in ONE cross-modal ACID
commit, via the agent-utilities ``MediaStore``. This makes the raw bytes — not just a
RomM URL or filesystem path — durable, deduped, and queryable inside the knowledge graph.
The stored asset links back to its ``:Game`` via the ``:hasCover`` property in ``rom.ttl``.

Entirely best-effort and dependency-guarded: if agent-utilities' KG stack or a live engine
is not present, every entry point here **no-ops** (returns ``None``), so the connector keeps
working with zero KG infrastructure.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("rom_manager.kg.media")

_SOURCE = "rom-manager"


def _media_store() -> Any | None:
    """Return a ``MediaStore`` over a live engine, or ``None`` when unavailable.

    Prefers the shared ``native_ingest.media_store`` primitive; falls back to building a
    ``MediaStore`` directly over the lightweight engine client when it is not installed.
    """
    try:
        from agent_utilities.knowledge_graph.memory.native_ingest import (
            media_store as _shared_media_store,
        )

        store = _shared_media_store()
        if store is not None:
            return store
    except Exception as e:  # noqa: BLE001 — primitive absent -> direct build
        logger.debug("Operation failed: error_type=%s", type(e).__name__)

    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
        from agent_utilities.knowledge_graph.memory.media_store import MediaStore
    except Exception as e:  # noqa: BLE001 — agent-utilities KG stack absent
        logger.debug("Operation failed: error_type=%s", type(e).__name__)
        return None
    try:
        engine = GraphComputeEngine()
        if getattr(engine, "_client", None) is None:
            logger.debug("KG media ingest: no live engine client")
            return None
        return MediaStore(engine)
    except Exception as e:  # noqa: BLE001 — no reachable engine
        logger.debug("Operation failed: error_type=%s", type(e).__name__)
        return None


def ingest_cover(
    data: bytes | None,
    *,
    rom: dict[str, Any] | None = None,
    mime_type: str = "image/png",
    source: str = _SOURCE,
    media_store: Any | None = None,
) -> dict[str, Any] | None:
    """Store a game's cover / box art as a blob + ``:AssetOccurrence`` in the knowledge graph.

    ``rom`` is the RomM ROM record the art belongs to (used for the asset name +
    provenance ``extra`` so the asset can be linked to its ``rom:game:<id>`` node).
    Returns ``{asset_id, digest, size_bytes, media_type}`` on success, or ``None`` when
    there is no engine, no bytes, or the store failed (never raises). ``media_store`` may
    be injected (tests); otherwise one is built on demand.
    """
    if not data:
        return None
    store = media_store if media_store is not None else _media_store()
    if store is None:
        return None

    rom = rom or {}
    name = rom.get("name") or rom.get("fs_name") or "cover"
    extra = {
        k: rom.get(k)
        for k in ("id", "slug", "platform_slug", "platform_display_name", "url_cover")
        if rom.get(k) is not None
    }
    if rom.get("id") is not None:
        extra["game_id"] = f"rom:game:{rom['id']}"

    try:
        stored = store.store_media(
            data,
            media_type="image",
            mime_type=mime_type,
            source=source,
            name=f"{name} (cover)",
            extra=extra,
        )
    except Exception as e:  # noqa: BLE001 — engine/store failure is non-fatal
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None
    if stored is None:
        return None

    logger.info(
        "KG media ingest: stored cover for %s (%s bytes) as asset %s",
        name,
        len(data),
        getattr(stored, "asset_id", "?"),
    )
    return {
        "asset_id": stored.asset_id,
        "digest": stored.digest,
        "size_bytes": len(data),
        "media_type": "image",
    }


def ingest_rom_file(
    data: bytes | None,
    *,
    rom: dict[str, Any] | None = None,
    mime_type: str = "application/octet-stream",
    source: str = _SOURCE,
    media_store: Any | None = None,
) -> dict[str, Any] | None:
    """Store a ROM binary as a content-addressed blob + ``:AssetOccurrence`` in the graph.

    Same contract as :func:`ingest_cover`, but for the ROM file bytes themselves
    (``media_type="file"``). Returns the stored-asset summary or ``None``.
    """
    if not data:
        return None
    store = media_store if media_store is not None else _media_store()
    if store is None:
        return None

    rom = rom or {}
    name = rom.get("fs_name") or rom.get("name") or "rom"
    extra = {
        k: rom.get(k)
        for k in (
            "id",
            "slug",
            "platform_slug",
            "fs_size_bytes",
            "crc_hash",
            "md5_hash",
        )
        if rom.get(k) is not None
    }
    if rom.get("id") is not None:
        extra["game_id"] = f"rom:game:{rom['id']}"

    try:
        stored = store.store_media(
            data,
            media_type="file",
            mime_type=mime_type,
            source=source,
            name=name,
            extra=extra,
        )
    except Exception as e:  # noqa: BLE001 — engine/store failure is non-fatal
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None
    if stored is None:
        return None

    logger.info(
        "KG media ingest: stored ROM %s (%s bytes) as asset %s",
        name,
        len(data),
        getattr(stored, "asset_id", "?"),
    )
    return {
        "asset_id": stored.asset_id,
        "digest": stored.digest,
        "size_bytes": len(data),
        "media_type": "file",
    }
