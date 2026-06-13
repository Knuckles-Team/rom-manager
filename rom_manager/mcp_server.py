#!/usr/bin/python
"""ROM Manager MCP server assembly.

CONCEPT:ROM-001, CONCEPT:ROM-002 — registers the conversion and game-codes tool
domains. This server is the integration seam to agent-utilities:
``create_mcp_server`` wires the shared FastMCP middleware that implements the
cross-project bridge capabilities — CONCEPT:ECO-4.0 (Unified Toolkit Ingestion),
CONCEPT:OS-5.1 (Prompt Injection Defense), CONCEPT:OS-5.3 (Guardrail Engine) and
CONCEPT:OS-5.4 (Audit Logging) via the Eunomia/OTEL middleware stack.
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

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server
from dotenv import find_dotenv, load_dotenv

from rom_manager.mcp import (
    register_conversion_tools,
    register_game_codes_tools,
    register_romm_tools,
)

__version__ = "1.2.0"
print(f"ROM Manager MCP v{__version__}", file=sys.stderr)

logger = get_logger(name="mcp_server")
logger.setLevel(logging.DEBUG)

DEFAULT_ROM_DIRECTORY = os.getenv("ROM_DIRECTORY", os.path.curdir)
DEFAULT_ROM_ISO_TYPE = os.getenv("ROM_ISO_TYPE", "chd")


def register_prompts(mcp: FastMCP):
    """Register externalized prompt templates (CONCEPT:ROM-001).

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

    CONCEPT:ROM-001, CONCEPT:ROM-002 — registers both tool domains and attaches
    the agent-utilities middleware stack (CONCEPT:ECO-4.0).
    """
    load_dotenv(find_dotenv())
    os.environ["FASTMCP_LOG_LEVEL"] = "ERROR"
    os.environ["TERM"] = "dumb"
    os.environ["NO_COLOR"] = "1"

    args, mcp, middlewares = create_mcp_server(
        name="ROM Manager",
        version=__version__,
        instructions="ROM Manager MCP Server - Convert ROMs to CHD/RVZ, extract archives, generate cue sheets, and resolve game codes.",
    )

    DEFAULT_CONVERSIONTOOL = to_boolean(os.getenv("CONVERSIONTOOL", "True"))
    if DEFAULT_CONVERSIONTOOL:
        register_conversion_tools(mcp)

    DEFAULT_GAMECODESTOOL = to_boolean(os.getenv("GAMECODESTOOL", "True"))
    if DEFAULT_GAMECODESTOOL:
        register_game_codes_tools(mcp)

    # CONCEPT:ROM-003 — RomM remote-library API tools (one per resource group).
    DEFAULT_ROMMTOOL = to_boolean(os.getenv("ROMMTOOL", "True"))
    if DEFAULT_ROMMTOOL:
        register_romm_tools(mcp)

    register_prompts(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)

    registered_tags: list[str] = []
    return mcp, args, middlewares, registered_tags


def mcp_server() -> None:
    """Build and run the ROM Manager MCP server (CONCEPT:ROM-001, CONCEPT:ROM-002)."""
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
