"""MCP tools for the RomM remote library API (CONCEPT:ROM-003).

One action-routed tool per RomM resource group, mirroring the conversion tool's
``action`` + ``params_json`` shape. Each action maps 1:1 to a :class:`RommApi`
method, giving full coverage of the RomM REST API. The tool/action map is
declared once in :data:`ROMM_TOOLS`; :func:`register_romm_tools` builds and
registers every tool from it.
"""

import json
from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from rom_manager.romm.auth import get_romm_client

# Each entry: (tool_name, tag, summary, {action: RommApi method name}). Every RomM
# operation is reachable through exactly one (tool, action) pair.
ROMM_TOOLS: list[tuple[str, str, str, dict[str, str]]] = [
    (
        "romm_roms",
        "romm-roms",
        "Manage RomM ROMs: list/search/get, upload/update/delete, download "
        "content, manuals, notes, and per-user properties.",
        {
            "list": "list_roms",
            "get": "get_rom",
            "by_hash": "get_rom_by_hash",
            "by_metadata_provider": "get_rom_by_metadata_provider",
            "filters": "get_rom_filters",
            "identifiers": "get_rom_identifiers",
            "get_romfile": "get_romfile",
            "add": "add_rom",
            "update": "update_rom",
            "delete": "delete_roms",
            "download": "download_roms",
            "content": "get_rom_content",
            "head_content": "head_rom_content",
            "add_manuals": "add_rom_manuals",
            "delete_manuals": "delete_rom_manuals",
            "list_notes": "list_rom_notes",
            "note_identifiers": "get_rom_note_identifiers",
            "create_note": "create_rom_note",
            "update_note": "update_rom_note",
            "delete_note": "delete_rom_note",
            "update_props": "update_rom_user",
        },
    ),
    (
        "romm_platforms",
        "romm-platforms",
        "Manage RomM platforms: list/get/add/update/delete and list supported.",
        {
            "list": "list_platforms",
            "supported": "get_supported_platforms",
            "identifiers": "get_platform_identifiers",
            "get": "get_platform",
            "add": "add_platform",
            "update": "update_platform",
            "delete": "delete_platform",
        },
    ),
    (
        "romm_collections",
        "romm-collections",
        "Manage RomM collections, smart collections, and virtual collections.",
        {
            "list": "list_collections",
            "identifiers": "get_collection_identifiers",
            "get": "get_collection",
            "add": "add_collection",
            "update": "update_collection",
            "delete": "delete_collection",
            "smart_list": "list_smart_collections",
            "smart_identifiers": "get_smart_collection_identifiers",
            "smart_get": "get_smart_collection",
            "smart_add": "add_smart_collection",
            "smart_update": "update_smart_collection",
            "smart_delete": "delete_smart_collection",
            "virtual_list": "list_virtual_collections",
            "virtual_identifiers": "get_virtual_collection_identifiers",
            "virtual_get": "get_virtual_collection",
        },
    ),
    (
        "romm_saves",
        "romm-saves",
        "Manage RomM save files: list/get/upload/update/delete, download, "
        "track/untrack, and per-ROM summary.",
        {
            "list": "list_saves",
            "identifiers": "get_save_identifiers",
            "summary": "get_saves_summary",
            "get": "get_save",
            "add": "add_save",
            "update": "update_save",
            "delete": "delete_saves",
            "download": "download_save",
            "confirm_download": "confirm_save_download",
            "track": "track_save",
            "untrack": "untrack_save",
        },
    ),
    (
        "romm_states",
        "romm-states",
        "Manage RomM emulator save-states: list/get/upload/update/delete.",
        {
            "list": "list_states",
            "identifiers": "get_state_identifiers",
            "get": "get_state",
            "add": "add_state",
            "update": "update_state",
            "delete": "delete_states",
        },
    ),
    (
        "romm_screenshots",
        "romm-screenshots",
        "Upload RomM screenshots for a ROM.",
        {"add": "add_screenshot"},
    ),
    (
        "romm_firmware",
        "romm-firmware",
        "Manage RomM firmware: list/get/upload/delete and download content.",
        {
            "list": "list_firmware",
            "identifiers": "get_firmware_identifiers",
            "get": "get_firmware",
            "add": "add_firmware",
            "delete": "delete_firmware",
            "content": "get_firmware_content",
            "head_content": "head_firmware_content",
        },
    ),
    (
        "romm_users",
        "romm-users",
        "Manage RomM users: list/get/add/update/delete, current profile, "
        "invite links, registration, and RetroAchievements refresh.",
        {
            "list": "list_users",
            "identifiers": "get_user_identifiers",
            "me": "get_current_user",
            "get": "get_user",
            "add": "add_user",
            "update": "update_user",
            "delete": "delete_user",
            "invite_link": "create_invite_link",
            "register": "register_user_from_invite",
            "ra_refresh": "refresh_retro_achievements",
        },
    ),
    (
        "romm_tasks",
        "romm-tasks",
        "Manage RomM background tasks: list/status/get and run all or one.",
        {
            "list": "list_tasks",
            "status": "get_tasks_status",
            "get": "get_task",
            "run_all": "run_all_tasks",
            "run": "run_task",
        },
    ),
    (
        "romm_search",
        "romm-search",
        "Search RomM metadata providers for ROM matches and cover art.",
        {"roms": "search_roms", "cover": "search_cover"},
    ),
    (
        "romm_config",
        "romm-config",
        "Manage RomM system config: exclusions, platform bindings/versions, "
        "and first-run setup.",
        {
            "get": "get_config",
            "add_exclusion": "add_exclusion",
            "delete_exclusion": "delete_exclusion",
            "add_platform_binding": "add_platform_binding",
            "delete_platform_binding": "delete_platform_binding",
            "add_platform_version": "add_platform_version",
            "delete_platform_version": "delete_platform_version",
            "setup_library": "get_setup_library",
            "setup_platforms": "create_setup_platforms",
        },
    ),
    (
        "romm_feeds",
        "romm-feeds",
        "Read RomM integration feeds: WebRcade, Tinfoil, PKGi, PKGj, fpkgi, Kekatsu.",
        {
            "webrcade": "webrcade_feed",
            "tinfoil": "tinfoil_feed",
            "fpkgi": "fpkgi_feed",
            "kekatsu": "kekatsu_feed",
            "pkgi_ps3": "pkgi_ps3_feed",
            "pkgi_psp": "pkgi_psp_feed",
            "pkgi_psvita": "pkgi_psvita_feed",
            "pkgj_psp_dlc": "pkgj_psp_dlc_feed",
            "pkgj_psp_games": "pkgj_psp_games_feed",
            "pkgj_psvita_dlc": "pkgj_psvita_dlc_feed",
            "pkgj_psvita_games": "pkgj_psvita_games_feed",
            "pkgj_psx_games": "pkgj_psx_games_feed",
        },
    ),
    (
        "romm_devices",
        "romm-devices",
        "Manage RomM devices: list/get/register/update/delete.",
        {
            "list": "list_devices",
            "get": "get_device",
            "register": "register_device",
            "update": "update_device",
            "delete": "delete_device",
        },
    ),
    (
        "romm_system",
        "romm-system",
        "RomM system/auth/misc: heartbeat, stats, netplay, gamelist export, raw "
        "assets, session login/logout, OAuth token, OpenID, password reset.",
        {
            "heartbeat": "heartbeat",
            "metadata_heartbeat": "metadata_heartbeat",
            "stats": "stats",
            "netplay_list": "list_netplay_rooms",
            "gamelist_export": "export_gamelist",
            "raw_asset": "get_raw_asset",
            "head_raw_asset": "head_raw_asset",
            "romfile_content": "get_romfile_content",
            "login": "login",
            "login_openid": "login_via_openid",
            "logout": "logout",
            "token": "create_token",
            "oauth_openid": "oauth_openid",
            "forgot_password": "forgot_password",
            "reset_password": "reset_password",
        },
    ),
]


def _make_romm_tool(
    mcp: FastMCP, tool_name: str, tag: str, summary: str, actions: dict[str, str]
) -> None:
    """Register one action-routed RomM tool (CONCEPT:ROM-003)."""
    action_list = ", ".join(f"'{a}'" for a in actions)

    @mcp.tool(name=tool_name, tags={tag})
    async def _romm_tool(
        action: str = Field(description=f"Action to perform. One of: {action_list}."),
        params_json: str = Field(
            default="{}",
            description="JSON object of keyword arguments for the action.",
        ),
        client=Depends(get_romm_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> Any:
        if ctx:
            await ctx.info(f"RomM {tool_name}: {action}")
        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}
        if not isinstance(kwargs, dict):
            return {"error": "params_json must be a JSON object"}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        method = actions.get(action)
        if method is None:
            return {"error": f"Unknown action '{action}'. Valid actions: {action_list}"}
        return getattr(client, method)(**kwargs)

    _romm_tool.__doc__ = f"{summary}\n\nActions: {action_list}. (CONCEPT:ROM-003)"


def register_romm_tools(mcp: FastMCP) -> None:
    """Register every RomM resource tool on the given FastMCP server (CONCEPT:ROM-003)."""
    for tool_name, tag, summary, actions in ROMM_TOOLS:
        _make_romm_tool(mcp, tool_name, tag, summary, actions)
