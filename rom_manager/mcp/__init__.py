"""MCP tool registration for rom-manager.

The conversion, game-code and RomM operations are served as one typed tool per client
method by the SDK tool surface; only the knowledge-graph ingest tools register here.
"""

from rom_manager.mcp.mcp_ingest import register_ingest_tools

__all__ = ["register_ingest_tools"]
