"""Native epistemic-graph ingestion for RomM library records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This is the record-source twin of
``kg_media`` (blob ingestion): the package natively pushes its RomM library data into
the epistemic-graph knowledge graph as **typed OWL nodes** (``:Game``, ``:GameSystem``,
``:GameCollection``, ``:GameSave``, ``:GameState``, ``:Firmware``) + links, matching the
classes federated by ``rom_manager.ontology`` (``rom.ttl``).

The write path goes through ``agent_connector_sdk.ingest`` -- the generated
``SourceIngest`` client, not a local ingestion helper. Engine failures are explicit and
partial writes are never acknowledged. Node ids follow ``rom:<class>:<externalId>``.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Entity,
    EntityRef,
    IngestBinding,
    IngestError,
    KnowledgeIngest,
    Relationship,
    current_ingest,
)

logger = logging.getLogger("rom_manager.kg")

_BINDING = IngestBinding(connector="rom-manager", stream="rom")

_ENTITY_RESERVED_KEYS = frozenset({"id", "node_type"})
_RELATIONSHIP_RESERVED_KEYS = frozenset({"source", "target", "relationship"})


def _to_entity(record: dict[str, Any]) -> Entity:
    return Entity(
        id=record.get("id"),
        node_type=record.get("node_type"),
        properties={
            key: value
            for key, value in record.items()
            if key not in _ENTITY_RESERVED_KEYS
        },
    )


def _to_relationship(record: dict[str, Any]) -> Relationship:
    properties = {
        key: value
        for key, value in record.items()
        if key not in _RELATIONSHIP_RESERVED_KEYS
    }
    return Relationship(
        source=record["source"],
        target=record["target"],
        relationship=record["relationship"],
        properties=properties or None,
    )


async def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write typed nodes (+ edges) into epistemic-graph via the SDK ingest facade.

    Nodes use ``node_type`` and relationships use ``relationship``. ``ingest`` may be
    injected for isolated validation.
    """
    if not entities:
        raise IngestError("ingest_entities needs at least one entity")
    change_set = ChangeSet(
        entities=tuple(_to_entity(entity) for entity in entities),
        relationships=tuple(
            _to_relationship(relationship) for relationship in relationships or ()
        ),
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


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
            {
                "source": game_id,
                "target": f"rom:system:{plat_id}",
                "relationship": "onSystem",
            }
        )
    return {"entities": entities, "relationships": relationships}, relationships


async def ingest_roms(
    roms: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
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
    return await ingest_entities(entities, relationships, ingest=ingest)


async def ingest_platforms(
    platforms: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
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
    return await ingest_entities(entities, None, ingest=ingest)


async def ingest_collections(
    collections: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
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
                    # The referenced :Game isn't in this change set (it was ingested
                    # separately by ingest_roms), so the source needs an explicit
                    # EntityRef carrying its node_type for the SDK's request builder.
                    "source": EntityRef(id=f"rom:game:{rid}", node_type="Game"),
                    "target": coll_id,
                    "relationship": "inCollection",
                }
            )
    return await ingest_entities(entities, relationships, ingest=ingest)
