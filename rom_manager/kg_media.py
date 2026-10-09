"""Native epistemic-graph blob ingestion for ROM cover art and ROM binaries.

CONCEPT:AU-KG.ingest.list-durable-media. When a live epistemic-graph engine is reachable,
a game's cover / box art (or a ROM file itself) is stored as a content-addressed **blob**
with a ``:MediaAsset`` graph node (carrying its RomM metadata) in ONE cross-modal ACID
commit, via ``agent_connector_sdk.ingest``'s ``ChangeSet(media=(MediaAsset(...),))`` +
``KnowledgeIngest.submit``. This makes the raw bytes — not just a RomM URL or filesystem
path — durable, deduped, and queryable inside the knowledge graph. The stored asset id is
``blob:<digest>``-derived (read back from the commit receipt's raw admissions), so it can
be linked to its ``:Game`` via the ``:hasCover`` property in ``rom.ttl``.

Entirely best-effort and dependency-/engine-guarded: if no KG stack or no reachable engine
is present, every entry point here **no-ops** (returns ``None``), so the connector keeps
working with zero KG infrastructure.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    IngestBinding,
    IngestError,
    KnowledgeIngest,
    MediaAsset,
    current_ingest,
)

logger = logging.getLogger("rom_manager.kg.media")

_BINDING = IngestBinding(connector="rom-manager", stream="rom")


async def _store(
    data: bytes | None,
    *,
    media_type: str,
    name: str,
    extra: dict[str, Any],
    mime_type: str,
    ingest: KnowledgeIngest | None,
) -> dict[str, Any] | None:
    if not data:
        return None
    asset = MediaAsset(data=data, mime_type=mime_type, name=name, properties=extra)
    change_set = ChangeSet(media=(asset,))
    try:
        service = ingest or current_ingest()
        receipt = await service.submit(_BINDING, change_set)
    except IngestError as exc:
        logger.warning("KG media ingest failed (exception_type=%s)", type(exc).__name__)
        return None

    admission = next(
        (a for a in receipt.raw_admissions if a.record_id.startswith("blob:")), None
    )
    if admission is None:
        return None

    logger.info(
        "KG media ingest: stored %s (%s bytes) as asset %s",
        name,
        len(data),
        admission.record_id,
    )
    return {
        "asset_id": admission.record_id,
        "digest": admission.raw_digest,
        "size_bytes": len(data),
        "media_type": media_type,
    }


async def ingest_cover(
    data: bytes | None,
    *,
    rom: dict[str, Any] | None = None,
    mime_type: str = "image/png",
    ingest: KnowledgeIngest | None = None,
) -> dict[str, Any] | None:
    """Store a game's cover / box art as a blob + ``:MediaAsset`` in the knowledge graph.

    ``rom`` is the RomM ROM record the art belongs to (used for the asset name +
    provenance ``extra`` so the asset can be linked to its ``rom:game:<id>`` node).
    Returns ``{asset_id, digest, size_bytes, media_type}`` on success, or ``None`` when
    there is no engine, no bytes, or the store failed (never raises). ``ingest`` may be
    injected (tests); otherwise the process-installed facade is used.
    """
    rom = rom or {}
    name = rom.get("name") or rom.get("fs_name") or "cover"
    extra = {
        k: rom.get(k)
        for k in ("id", "slug", "platform_slug", "platform_display_name", "url_cover")
        if rom.get(k) is not None
    }
    if rom.get("id") is not None:
        extra["game_id"] = f"rom:game:{rom['id']}"

    return await _store(
        data,
        media_type="image",
        name=f"{name} (cover)",
        extra=extra,
        mime_type=mime_type,
        ingest=ingest,
    )


async def ingest_rom_file(
    data: bytes | None,
    *,
    rom: dict[str, Any] | None = None,
    mime_type: str = "application/octet-stream",
    ingest: KnowledgeIngest | None = None,
) -> dict[str, Any] | None:
    """Store a ROM binary as a content-addressed blob + ``:MediaAsset`` in the graph.

    Same contract as :func:`ingest_cover`, but for the ROM file bytes themselves
    (``media_type="file"``). Returns the stored-asset summary or ``None``.
    """
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

    return await _store(
        data,
        media_type="file",
        name=name,
        extra=extra,
        mime_type=mime_type,
        ingest=ingest,
    )
