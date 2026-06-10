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

from agent_utilities.base_utilities import get_logger, to_boolean

from rom_manager.api_client import Api

logger = get_logger(__name__)


def get_client(
    directory: str | None = None,
    iso_type: str = os.getenv("ROM_ISO_TYPE", "chd"),
    verbose: bool = to_boolean(string=os.getenv("ROM_VERBOSE", "False")),
    force: bool = to_boolean(string=os.getenv("ROM_FORCE", "False")),
    config: dict | None = None,
) -> Api:
    """Factory returning the local ROM Manager :class:`Api` facade (CONCEPT:ROM-001).

    No credentials are required. ``directory`` defaults to ``ROM_DIRECTORY`` (or
    the current working directory). ``iso_type`` selects the conversion target
    (``chd`` or ``rvz``).
    """
    resolved_directory = directory or os.getenv("ROM_DIRECTORY") or os.path.curdir
    logger.info(
        "Creating local ROM Manager client",
        extra={"directory": resolved_directory, "iso_type": iso_type},
    )
    return Api(
        directory=resolved_directory,
        iso_type=iso_type if iso_type in ("chd", "rvz") else "chd",
        verbose=verbose,
        force=force,
    )
