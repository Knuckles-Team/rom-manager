"""Native epistemic-graph ingestion for RomM library records (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This is the record-source twin of
``kg_media`` (blob ingestion): the package natively pushes its RomM library data into
the epistemic-graph knowledge graph as **typed OWL nodes** (``:Game``, ``:GameSystem``,
``:GameCollection``, ``:GameSave``, ``:GameState``, ``:Firmware``) + links, matching the
classes federated by ``rom_manager.ontology`` (``rom.ttl``).

The write path is the shared connector primitive
``agent_utilities.knowledge_graph.memory.native_ingest`` when it is installed; when it is
not (the primitive is newer than the pinned agent-utilities), this module falls back to a
**self-contained** txn write over the same lightweight engine client
(``GraphComputeEngine()._client`` + ``txn``) — the same fast client the blob ``MediaStore``
uses, NOT the heavy in-process ingestion engine.

Everything is dependency-/engine-guarded: with no agent-utilities KG stack or no reachable
engine, every entry point **no-ops** (returns ``None``), so the connector keeps working with
zero KG infrastructure. Node ids follow ``rom:<class>:<externalId>``.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("rom_manager.kg")

_SOURCE = "rom-manager"
_DOMAIN = "rom"
_DEFAULT_GRAPH = "__commons__"


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        graph = getattr(engine, "graph_name", None) or _DEFAULT_GRAPH
        return client, graph
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed nodes (+ edges) into epistemic-graph.

    Prefers the shared ``native_ingest`` primitive; falls back to a self-contained txn
    write when it is not installed. ``entities``: ``[{"id":..., "type":..., ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "type":rel}]``. Returns
    ``{"nodes":n, "edges":m}`` or ``None`` (no engine / failure; never raises).
    ``client``/``graph`` may be injected (tests); otherwise resolved on demand.
    """
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None

    # Preferred path: the shared fleet primitive (only when an explicit client is not
    # injected, so tests exercise the self-contained path deterministically).
    if client is None:
        try:
            from agent_utilities.knowledge_graph.memory.native_ingest import (
                ingest_entities as _shared_ingest,
            )

            return _shared_ingest(
                entities,
                relationships,
                source=_SOURCE,
                domain=_DOMAIN,
                graph=graph,
            )
        except Exception as e:  # noqa: BLE001 — primitive absent -> self-contained
            logger.debug("KG ingest: shared primitive unavailable: %s", e)

    if client is None:
        client, graph = _client()
    if client is None:
        return None
    graph = graph or _DEFAULT_GRAPH

    try:
        txn = client.txn.begin(graph=graph)
        for ent in entities:
            props = {k: v for k, v in ent.items() if k != "id" and v is not None}
            props.setdefault("source", _SOURCE)
            props.setdefault("domain", _DOMAIN)
            client.txn.add_node(txn, ent["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)

    logger.info("KG ingest: wrote %d nodes, %d edges", len(entities), edges)
    return {"nodes": len(entities), "edges": edges}


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
            "type": "Game",
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
                "type": "GameSystem",
                "name": rom.get("platform_display_name")
                or rom.get("platform_custom_name"),
                "slug": rom.get("platform_slug"),
                "externalToolId": str(plat_id),
            }
        )
        relationships.append(
            {"source": game_id, "target": f"rom:system:{plat_id}", "type": "onSystem"}
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
                "type": "GameSystem",
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
                "type": "GameCollection",
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
                    "type": "inCollection",
                }
            )
    return ingest_entities(entities, relationships, client=client, graph=graph)
