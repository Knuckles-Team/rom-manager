"""ROM Manager local configuration / client factory.

Unlike network-backed connectors (e.g. ``gitlab-api``), ``rom-manager`` is a
**local CLI tool**: it extracts archives, renames ROMs via known game codes, and
converts ISO/WBFS images to CHD/RVZ using locally-installed binaries
(``chdman`` / ``dolphin-tool``). There is therefore **no service URL and no
required credentials**.

This module mirrors the ecosystem ``auth.py`` shape (a ``get_client`` factory
the MCP tools depend on) but degrades to a no-op/local configuration. The only
recognised setting is the optional ``ROM_DIRECTORY`` environment variable, used
as the default working directory when none is supplied.
"""

import os

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.config import setting

from rom_manager.api_client import Api

logger = get_logger(__name__)


def get_client(
    directory: str | None = None,
    iso_type: str | None = None,
    verbose: bool | None = None,
    force: bool | None = None,
    config: dict | None = None,
) -> Api:
    """Factory returning the local ROM Manager :class:`Api` facade (CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool).

    No credentials are required. ``directory`` defaults to ``ROM_DIRECTORY`` (or
    the current working directory). ``iso_type`` selects the conversion target
    (``chd`` or ``rvz``).
    """
    resolved_iso_type = (
        iso_type if iso_type is not None else setting("ROM_ISO_TYPE", "chd")
    )
    resolved_verbose = verbose if verbose is not None else setting("ROM_VERBOSE", False)
    resolved_force = force if force is not None else setting("ROM_FORCE", False)
    resolved_directory = directory or setting("ROM_DIRECTORY", os.path.curdir)
    logger.info(
        "Creating local ROM Manager client",
        extra={"directory": resolved_directory, "iso_type": resolved_iso_type},
    )
    return Api(
        directory=resolved_directory,
        iso_type=resolved_iso_type if resolved_iso_type in ("chd", "rvz") else "chd",
        verbose=resolved_verbose,
        force=resolved_force,
    )
