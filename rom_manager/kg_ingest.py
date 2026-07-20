"""Native epistemic-graph ingestion for RomM library records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This is the record-source twin of
``kg_media`` (blob ingestion): the package natively pushes its RomM library data into
the epistemic-graph knowledge graph as **typed OWL nodes** (``:Game``, ``:GameSystem``,
``:GameCollection``, ``:GameSave``, ``:GameState``, ``:Firmware``) + links, matching the
classes federated by ``rom_manager.ontology`` (``rom.ttl``).

The write path is the required shared connector transaction primitive
``agent_utilities.knowledge_graph.memory.native_ingest``. Engine failures are explicit and
partial writes are never acknowledged. Node ids follow ``rom:<class>:<externalId>``.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)

logger = logging.getLogger("rom_manager.kg")

_SOURCE = "rom-manager"
_DOMAIN = "rom"
def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write typed nodes (+ edges) into epistemic-graph.

    Nodes use ``node_type`` and relationships use ``relationship``. ``client``/``graph``
    may be injected for isolated validation.
    """
    return _native_ingest_entities(
        entities,
        relationships,
        source=_SOURCE,
        domain=_DOMAIN,
        client=client,
        graph=graph,
    )


def _rom_record(rom: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Map one RomM ROM record → a ``:Game`` node (+ :GameSystem/:GameCollection edges)."""
    rid = rom.get("id")
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    game_id = f"rom:game:{rid}"
    regions = rom.get("regions")
    entities.append(
        {
            "id": game_id,
            "node_type": "Game",
            "name": rom.get("name") or rom.get("fs_name"),
            "slug": rom.get("slug"),
            "summary": rom.get("summary"),
            "fsName": rom.get("fs_name"),
            "fsSizeBytes": rom.get("fs_size_bytes"),
            "regions": ", ".join(regions) if isinstance(regions, list) else regions,
            "revision": rom.get("revision"),
            "igdb_id": rom.get("igdb_id"),
            "moby_id": rom.get("moby_id"),
            "ss_id": rom.get("ss_id"),
            "ra_id": rom.get("ra_id"),
            "externalToolId": str(rid),
        }
    )
    plat_id = rom.get("platform_id")
    if plat_id is not None:
        entities.append(
            {
                "id": f"rom:system:{plat_id}",
                "node_type": "GameSystem",
                "name": rom.get("platform_display_name")
                or rom.get("platform_custom_name"),
                "slug": rom.get("platform_slug"),
                "externalToolId": str(plat_id),
            }
        )
        relationships.append(
            {"source": game_id, "target": f"rom:system:{plat_id}", "relationship": "onSystem"}
        )
    return {"entities": entities, "relationships": relationships}, relationships


def ingest_roms(
    roms: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map RomM ROM records → ``:Game`` (+ ``:GameSystem``) nodes and ingest."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rom in roms or []:
        if rom.get("id") is None:
            continue
        mapped, _ = _rom_record(rom)
        for ent in mapped["entities"]:
            if ent["id"] in seen:
                continue
            seen.add(ent["id"])
            entities.append(ent)
        relationships.extend(mapped["relationships"])
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_platforms(
    platforms: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map RomM platform records → ``:GameSystem`` nodes and ingest."""
    entities: list[dict[str, Any]] = []
    for plat in platforms or []:
        pid = plat.get("id")
        if pid is None:
            continue
        entities.append(
            {
                "id": f"rom:system:{pid}",
                "node_type": "GameSystem",
                "name": plat.get("display_name")
                or plat.get("custom_name")
                or plat.get("name"),
                "slug": plat.get("slug"),
                "romCount": plat.get("rom_count"),
                "fsSizeBytes": plat.get("fs_size_bytes"),
                "family_name": plat.get("family_name"),
                "generation": plat.get("generation"),
                "externalToolId": str(pid),
            }
        )
    return ingest_entities(entities, None, client=client, graph=graph)


def ingest_collections(
    collections: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Map RomM collection records → ``:GameCollection`` nodes (+ ``:inCollection`` edges)."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for coll in collections or []:
        cid = coll.get("id")
        if cid is None:
            continue
        coll_id = f"rom:collection:{cid}"
        entities.append(
            {
                "id": coll_id,
                "node_type": "GameCollection",
                "name": coll.get("name"),
                "description": coll.get("description"),
                "rom_count": coll.get("rom_count"),
                "externalToolId": str(cid),
            }
        )
        for rom_ref in coll.get("roms") or coll.get("rom_ids") or []:
            rid = rom_ref.get("id") if isinstance(rom_ref, dict) else rom_ref
            if rid is None:
                continue
            relationships.append(
                {
                    "source": f"rom:game:{rid}",
                    "target": coll_id,
                    "relationship": "inCollection",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)
