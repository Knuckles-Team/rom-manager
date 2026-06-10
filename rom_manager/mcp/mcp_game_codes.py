"""MCP tools for game code / naming operations.

CONCEPT:ROM-002 — Game Codes / Naming. Action-routed dynamic tool registration
that wraps the embedded PSX game-code registry and the ``RomManager`` rename
logic used to normalise ROM filenames.
"""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from rom_manager.auth import get_client


def register_game_codes_tools(mcp: FastMCP):
    @mcp.tool(tags={"game-codes"})
    async def rom_game_codes(
        action: str = Field(
            description="Action to perform. Must be one of: 'lookup', 'list', 'rename'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        """Manage ROM game code lookup and naming operations (CONCEPT:ROM-002).

        Resolve a game/serial code to its title, list the known code registry,
        or rename a ROM file in-place using its embedded code.
        """
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "lookup":
            return client.lookup_game_code(**kwargs)
        if action == "list":
            return client.list_game_codes(**kwargs)
        if action == "rename":
            return client.rename_by_game_code(**kwargs)
        raise ValueError(f"Unknown action: {action}")
