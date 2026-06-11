"""Unified RomM API client (CONCEPT:ROM-003).

Combines every resource mixin into a single :class:`RommApi` facade — the object
the RomM MCP tools and CLI depend on.
"""

from rom_manager.romm.api.api_client_collections import RommApiCollections
from rom_manager.romm.api.api_client_config import RommApiConfig
from rom_manager.romm.api.api_client_devices import RommApiDevices
from rom_manager.romm.api.api_client_feeds import RommApiFeeds
from rom_manager.romm.api.api_client_firmware import RommApiFirmware
from rom_manager.romm.api.api_client_platforms import RommApiPlatforms
from rom_manager.romm.api.api_client_roms import RommApiRoms
from rom_manager.romm.api.api_client_saves import RommApiSaves
from rom_manager.romm.api.api_client_screenshots import RommApiScreenshots
from rom_manager.romm.api.api_client_search import RommApiSearch
from rom_manager.romm.api.api_client_states import RommApiStates
from rom_manager.romm.api.api_client_system import RommApiSystem
from rom_manager.romm.api.api_client_tasks import RommApiTasks
from rom_manager.romm.api.api_client_users import RommApiUsers


class RommApi(
    RommApiRoms,
    RommApiPlatforms,
    RommApiCollections,
    RommApiSaves,
    RommApiStates,
    RommApiScreenshots,
    RommApiFirmware,
    RommApiUsers,
    RommApiTasks,
    RommApiSearch,
    RommApiConfig,
    RommApiFeeds,
    RommApiDevices,
    RommApiSystem,
):
    """Full RomM REST API client (all resource domains)."""


__all__ = ["RommApi"]
