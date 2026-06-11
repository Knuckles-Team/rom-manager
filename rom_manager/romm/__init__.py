"""RomM (romm.app) remote-library integration for rom-manager (CONCEPT:ROM-003).

While the rest of ``rom_manager`` operates on ROM files already on disk
(extract/convert/rename), this subpackage talks to a running RomM *library
server* over its REST API: the full ``RommApi`` client, the ``get_romm_client``
factory, and the RomM CLI handlers. Together they let one ``rom-manager`` tool
manage both local files and the RomM web library.
"""

from rom_manager.romm.api import RommApi
from rom_manager.romm.auth import get_romm_client

__all__ = ["RommApi", "get_romm_client"]
