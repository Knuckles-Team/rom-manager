"""MCP tools that natively ingest the RomM library into medulla.

CONCEPT:AU-KG.ingest.enterprise-source-extractor. Wire-First: each tool lists records
via the real :class:`RommApi` client (``get_romm_client``) and pushes them into the
knowledge graph as typed nodes (``:Game`` / ``:GameSystem`` / ``:GameCollection``) via
``rom_manager.kg_ingest``. Best-effort — when no engine is reachable the mapper no-ops
and the tool returns ``{"ingested": None}``. Registered by default via ``tools_module``
auto-discovery (toggle env ``INGESTTOOL``).
"""

from __future__ import annotations

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
        search_term: str | None = Field(default=None, description="Filter by name."),
        platform_ids: list[int] | None = Field(
            default=None, description="Only ROMs on these platform ids."
        ),
        collection_id: int | None = Field(
            default=None, description="Only ROMs in this collection id."
        ),
        limit: int | None = Field(default=None, description="Page size."),
        offset: int | None = Field(default=None, description="Page offset."),
        client=Depends(get_romm_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Natively ingest RomM ROMs into medulla as typed ``:Game`` nodes.

        Lists ROMs via the RomM API and pushes them (with their ``:GameSystem`` +
        ``:onSystem`` links) into the knowledge graph via the fast engine client.
        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from rom_manager.kg_ingest import ingest_roms

        kwargs = {
            k: v
            for k, v in {
                "search_term": search_term,
                "platform_ids": platform_ids,
                "collection_id": collection_id,
                "limit": limit,
                "offset": offset,
            }.items()
            if v is not None
        }
        if ctx:
            await ctx.info("RomM ingest: listing ROMs")
        roms = _records(client.list_roms(**kwargs))
        result = await ingest_roms(roms)
        return {"listed": len(roms), "ingested": result}

    @mcp.tool(name="rom_ingest_platforms", tags={"ingest"})
    async def rom_ingest_platforms(
        updated_after: str | None = Field(
            default=None, description="Only records updated after this ISO timestamp."
        ),
        client=Depends(get_romm_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Natively ingest RomM platforms into medulla as ``:GameSystem`` nodes.

        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from rom_manager.kg_ingest import ingest_platforms

        kwargs = {"updated_after": updated_after} if updated_after else {}
        if ctx:
            await ctx.info("RomM ingest: listing platforms")
        platforms = _records(client.list_platforms(**kwargs))
        result = await ingest_platforms(platforms)
        return {"listed": len(platforms), "ingested": result}

    @mcp.tool(name="rom_ingest_collections", tags={"ingest"})
    async def rom_ingest_collections(
        updated_after: str | None = Field(
            default=None, description="Only records updated after this ISO timestamp."
        ),
        client=Depends(get_romm_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Natively ingest RomM collections into medulla as ``:GameCollection`` nodes.

        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        from rom_manager.kg_ingest import ingest_collections

        kwargs = {"updated_after": updated_after} if updated_after else {}
        if ctx:
            await ctx.info("RomM ingest: listing collections")
        collections = _records(client.list_collections(**kwargs))
        result = await ingest_collections(collections)
        return {"listed": len(collections), "ingested": result}

    return None
