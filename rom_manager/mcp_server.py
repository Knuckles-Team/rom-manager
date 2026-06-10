#!/usr/bin/python
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
)

__version__ = "1.0.0"
print(f"ROM Manager MCP v{__version__}", file=sys.stderr)

logger = get_logger(name="mcp_server")
logger.setLevel(logging.DEBUG)

DEFAULT_ROM_DIRECTORY = os.getenv("ROM_DIRECTORY", os.path.curdir)
DEFAULT_ROM_ISO_TYPE = os.getenv("ROM_ISO_TYPE", "chd")


def register_prompts(mcp: FastMCP):
    return None


def get_mcp_instance() -> tuple[Any, Any, Any, Any]:
    """Initialize and return the ROM Manager MCP instance, args, and middlewares."""
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

    register_prompts(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)

    registered_tags: list[str] = []
    return mcp, args, middlewares, registered_tags


def mcp_server() -> None:
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
