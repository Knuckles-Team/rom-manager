#!/usr/bin/python
"""ROM Manager MCP server assembly.

CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool, CONCEPT:RO-OS.governance.game-codes-naming-resolves — registers the conversion and game-codes tool
domains. This server is the integration seam to agent-utilities:
``create_mcp_server`` wires the shared FastMCP middleware that implements the
cross-project bridge capabilities — CONCEPT:AU-ECO.messaging.native-backend-abstraction (Unified Toolkit Ingestion),
CONCEPT:AU-OS.config.secrets-authentication (Prompt Injection Defense), CONCEPT:AU-OS.governance.reactive-multi-axis-budget (Guardrail Engine) and
CONCEPT:AU-OS.governance.wasm-micro-agent-sandbox (Audit Logging) via the Eunomia/OTEL middleware stack.
"""

import warnings

from fastmcp import FastMCP
from fastmcp.utilities.logging import get_logger

# Filter RequestsDependencyWarning early to prevent log spam
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning

        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass

warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
warnings.filterwarnings("ignore", message=".*urllib3.*or charset_normalizer.*")

import logging
import os
import sys
from typing import Any

from agent_utilities.core.config import load_config, setting
from agent_utilities.mcp.server_factory import create_mcp_server
from agent_utilities.mcp.verbose_tools import register_tool_surface

from rom_manager import mcp as rom_tools
from rom_manager.api_client import Api
from rom_manager.auth import get_client

__version__ = "2.0.1"
print(f"ROM Manager MCP v{__version__}", file=sys.stderr)

logger = get_logger(name="mcp_server")
logger.setLevel(logging.DEBUG)

DEFAULT_ROM_DIRECTORY = setting("ROM_DIRECTORY", os.path.curdir)
DEFAULT_ROM_ISO_TYPE = setting("ROM_ISO_TYPE", "chd")


def register_prompts(mcp: FastMCP):
    """Register externalized prompt templates (CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool).

    Loads templates from ``rom_manager/prompts/`` rather than hardcoding them.
    """
    from rom_manager.prompts import load_prompt

    @mcp.prompt(name="convert_rom")
    def convert_rom(directory: str = ".", iso_type: str = "chd") -> str:
        """Guided ROM conversion workflow prompt."""
        return load_prompt("convert_rom").format(directory=directory, iso_type=iso_type)

    return None


def get_mcp_instance() -> tuple[Any, Any, Any, Any]:
    """Initialize and return the ROM Manager MCP instance, args, and middlewares.

    CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool, CONCEPT:RO-OS.governance.game-codes-naming-resolves — registers both tool domains and attaches
    the agent-utilities middleware stack (CONCEPT:AU-ECO.messaging.native-backend-abstraction).
    """
    load_config()
    os.environ["FASTMCP_LOG_LEVEL"] = "ERROR"
    os.environ["TERM"] = "dumb"
    os.environ["NO_COLOR"] = "1"

    args, mcp, middlewares = create_mcp_server(
        name="ROM Manager",
        version=__version__,
        instructions="ROM Manager MCP Server - Convert ROMs to CHD/RVZ, extract archives, generate cue sheets, and resolve game codes.",
    )

    registered_tags = register_tool_surface(
        mcp,
        client_cls=Api,
        get_client=get_client,
        service="rom-manager",
        tools_module=rom_tools,
    )

    register_prompts(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)

    return mcp, args, middlewares, registered_tags


def mcp_server() -> None:
    """Build and run the ROM Manager MCP server (CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool, CONCEPT:RO-OS.governance.game-codes-naming-resolves)."""
    mcp, args, middlewares, registered_tags = get_mcp_instance()
    print(f"{'rom-manager'} MCP v{__version__}", file=sys.stderr)
    print("\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)
    print(f"  Dynamic Tags Loaded: {len(set(registered_tags))}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error("Invalid transport", extra={"transport": args.transport})
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
