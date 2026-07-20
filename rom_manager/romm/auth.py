"""RomM client factory (CONCEPT:RO-OS.state.api-base-one-mixin).

Mirrors the ecosystem ``auth.py`` shape (``get_romm_client`` is the factory the
RomM MCP tools depend on via ``Depends``). Unlike the local converter's
``rom_manager.auth.get_client`` — which needs no credentials — RomM is a remote
service, so this reads connection + auth settings from the environment:

- ``ROMM_URL`` (required) — base URL of the RomM instance (e.g. ``http://host:3000``).
- ``ROMM_USERNAME`` / ``ROMM_PASSWORD`` — Basic or OAuth password-grant credentials.
- ``ROMM_TOKEN`` — a pre-minted OAuth2 bearer access token (takes precedence).
- ``ROMM_AUTH_MODE`` — ``basic`` (default) or ``oauth``.
- ``ROMM_SCOPES`` — space-separated OAuth scopes (defaults to RomM's full set).
- ``ROMM_TLS_PROFILE`` / ``ROMM_TLS_PROFILE_REF`` — runtime TLS policy.

An optional OIDC-delegation branch lets the client slot into the fleet SSO later;
Basic/token is the default path.
"""

import os

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.transport_security import (
    ResolvedTLSProfile,
    resolve_configured_tls_profile,
)

from rom_manager.romm.api import RommApi

logger = get_logger(__name__)


def get_romm_client(
    url: str | None = None,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    auth_mode: str | None = None,
    scopes: str | None = None,
    tls_profile: ResolvedTLSProfile | None = None,
) -> RommApi:
    """Build a :class:`RommApi` from arguments or ``ROMM_*`` environment (CONCEPT:RO-OS.state.api-base-one-mixin)."""
    url = url or os.getenv("ROMM_URL") or os.getenv("ROMM_HOST")
    if not url:
        raise RuntimeError("ROMM_URL is not set (base URL of the RomM instance)")
    username = username if username is not None else os.getenv("ROMM_USERNAME")
    password = password if password is not None else os.getenv("ROMM_PASSWORD")
    token = token if token is not None else os.getenv("ROMM_TOKEN")
    auth_mode = auth_mode or os.getenv("ROMM_AUTH_MODE", "basic")
    scopes = scopes if scopes is not None else os.getenv("ROMM_SCOPES")
    profile = tls_profile or resolve_configured_tls_profile("romm")

    # --- optional OIDC delegation (RFC 8693 token exchange) ---------------
    try:
        from agent_utilities.mcp.delegated_auth import (
            get_delegated_token,
            is_delegation_enabled,
        )

        if not token and is_delegation_enabled():
            token = get_delegated_token(
                audience=os.environ.get("AUDIENCE", url),
                scopes=os.environ.get("DELEGATED_SCOPES", "roms.read"),
            )
            logger.info("Using OIDC delegated token for RomM API")
    except Exception:  # delegation is best-effort; fall back to basic/token
        logger.debug("RomM OIDC delegation unavailable", extra={"error": "Operation failed"})

    logger.info(
        "Creating RomM client",
        extra={"auth_mode": "token" if token else auth_mode},
    )
    return RommApi(
        url=url,
        username=username,
        password=password,
        token=token,
        auth_mode=auth_mode,
        scopes=scopes,
        tls_profile=profile,
    )
