"""RomM API client package (CONCEPT:ROM-003).

``api_client_base`` provides the session/auth/transport; one mixin per resource
domain; ``api_client.RommApi`` combines them into a single facade.
"""

from rom_manager.romm.api.api_client import RommApi
from rom_manager.romm.api.api_client_base import RommApiBase

__all__ = ["RommApi", "RommApiBase"]
