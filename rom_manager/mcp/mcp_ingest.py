"""MCP tools that natively ingest the RomM library into epistemic-graph.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Wire-First: each tool lists records
via the real :class:`RommApi` client (``get_romm_client``) and pushes them into the
knowledge graph as typed nodes (``:Game`` / ``:GameSystem`` / ``:GameCollection``) via
``rom_manager.kg_ingest``. Best-effort — when no engine is reachable the mapper no-ops
and the tool returns ``{"ingested": None}``. Registered by default via ``tools_module``
auto-discovery (toggle env ``INGESTTOOL``).
"""

from __future__ import annotations

import json
from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from rom_manager.romm.auth import get_romm_client


def _records(resp: Any) -> list[dict[str, Any]]:
    """Normalise a RomM list response into a list of plain dicts."""
    data = getattr(resp, "data", resp)
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    records = data if isinstance(data, list) else [data]
    out: list[dict[str, Any]] = []
    for r in records:
        if r is None:
            continue
        out.append(r.model_dump() if hasattr(r, "model_dump") else r)
    return out


def register_ingest_tools(mcp: FastMCP) -> None:
    """Register the RomM -> knowledge-graph ingestion tools."""

    @mcp.tool(name="rom_ingest_roms", tags={"ingest"})
    async def rom_ingest_roms(
        params_json: str = Field(
            default="{}",
            description="JSON object of list_roms filters (e.g. platform_ids, "
            "collection_id, search_term, limit, offset).",
        ),
        client=Depends(get_romm_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Natively ingest RomM ROMs into epistemic-graph as typed ``:Game`` nodes.

        Lists ROMs via the RomM API and pushes them (with their ``:GameSystem`` +
        ``:onSystem`` links) into the knowledge graph via the fast engine client.
        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from rom_manager.kg_ingest import ingest_roms

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:  # noqa: BLE001
            return {"error": "Operation failed"}
        if ctx:
            await ctx.info("RomM ingest: listing ROMs")
        roms = _records(client.list_roms(**kwargs))
        result = ingest_roms(roms)
        return {"listed": len(roms), "ingested": result}

    @mcp.tool(name="rom_ingest_platforms", tags={"ingest"})
    async def rom_ingest_platforms(
        params_json: str = Field(
            default="{}",
            description="JSON object of list_platforms filters (e.g. updated_after).",
        ),
        client=Depends(get_romm_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Natively ingest RomM platforms into epistemic-graph as ``:GameSystem`` nodes.

        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from rom_manager.kg_ingest import ingest_platforms

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:  # noqa: BLE001
            return {"error": "Operation failed"}
        if ctx:
            await ctx.info("RomM ingest: listing platforms")
        platforms = _records(client.list_platforms(**kwargs))
        result = ingest_platforms(platforms)
        return {"listed": len(platforms), "ingested": result}

    @mcp.tool(name="rom_ingest_collections", tags={"ingest"})
    async def rom_ingest_collections(
        params_json: str = Field(
            default="{}",
            description="JSON object of list_collections filters.",
        ),
        client=Depends(get_romm_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Natively ingest RomM collections into epistemic-graph as ``:GameCollection`` nodes.

        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from rom_manager.kg_ingest import ingest_collections

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:  # noqa: BLE001
            return {"error": "Operation failed"}
        if ctx:
            await ctx.info("RomM ingest: listing collections")
        collections = _records(client.list_collections(**kwargs))
        result = ingest_collections(collections)
        return {"listed": len(collections), "ingested": result}

    return None
