"""MCP tools for ROM conversion operations.

CONCEPT:ROM-001 — ROM Conversion. Action-routed dynamic tool registration that
wraps the real ``RomManager`` conversion pipeline (extract -> rename -> convert
ISO/WBFS to CHD/RVZ -> cleanup).
"""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from rom_manager.auth import get_client


def register_conversion_tools(mcp: FastMCP):
    @mcp.tool(tags={"conversion"})
    async def rom_conversion(
        action: str = Field(
            description="Action to perform. Must be one of: 'convert', 'process_directory', 'process_file', 'generate_cue', 'list_files'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Manage ROM conversion operations (CONCEPT:ROM-001).

        Convert game ROMs to CHD (chdman) or RVZ (dolphin-tool), extract
        archives, generate cue sheets, and list candidate files. Requires the
        external ``chdman``/``dolphin-tool`` binaries to be installed for
        conversion actions.
        """
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action in ("convert", "process_directory"):
            return client.convert(**kwargs)
        if action == "process_file":
            return client.process_file(**kwargs)
        if action == "generate_cue":
            return client.generate_cue(**kwargs)
        if action == "list_files":
            return client.list_files(**kwargs)
        raise ValueError(f"Unknown action: {action}")
