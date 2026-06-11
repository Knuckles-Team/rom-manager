"""MCP tool registration modules for rom-manager.

Each domain has its own module with a register_*_tools function using the
action-routed dynamic tool pattern.
"""

from rom_manager.mcp.mcp_conversion import register_conversion_tools
from rom_manager.mcp.mcp_game_codes import register_game_codes_tools
from rom_manager.mcp.mcp_romm import register_romm_tools

__all__ = [
    "register_conversion_tools",
    "register_game_codes_tools",
    "register_romm_tools",
]
