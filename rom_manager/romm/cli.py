"""RomM command-line handlers (CONCEPT:ROM-003).

Extends the unified ``rom-manager`` CLI with RomM web-library commands of the
form ``rom-manager <resource> <action> [positionals] [--flag value ...]``, e.g.::

    rom-manager roms list --platform_ids 7 --limit 50
    rom-manager roms get 123
    rom-manager platforms list
    rom-manager saves add --rom_id 5 --file_path ./game.srm
    rom-manager tasks run scan
    rom-manager stats

Resource/action names map 1:1 to :class:`RommApi` methods — the same map the MCP
tools use (:data:`rom_manager.mcp.mcp_romm.ROMM_TOOLS`) — so the CLI and tools
stay in lockstep.
"""

import inspect
import json
import sys
from typing import Any

from rom_manager.mcp.mcp_romm import ROMM_TOOLS
from rom_manager.romm.api import RommApi
from rom_manager.romm.auth import get_romm_client

# Short resource name (e.g. "roms") -> {action: RommApi method}.
RESOURCE_ACTIONS: dict[str, dict[str, str]] = {
    name.removeprefix("romm_"): actions for name, _tag, _summary, actions in ROMM_TOOLS
}

# Convenience top-level aliases that resolve to a (resource, action) pair so users
# can type the natural command directly.
ALIASES: dict[str, tuple[str, str]] = {
    "stats": ("system", "stats"),
    "heartbeat": ("system", "heartbeat"),
    "login": ("system", "login"),
    "logout": ("system", "logout"),
    "auth": ("system", "token"),
}

# The subcommand keywords the unified CLI routes here (resources + aliases).
ROMM_COMMANDS: frozenset[str] = frozenset(RESOURCE_ACTIONS) | frozenset(ALIASES)


def _coerce(value: str) -> Any:
    """Coerce a CLI string to bool/int/float/JSON where it clearly is one."""
    low = value.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "none"):
        return None
    if value and (value[0] in "[{"):
        try:
            return json.loads(value)
        except ValueError:
            return value
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            continue
    return value


def _parse_args(tokens: list[str]) -> tuple[list[Any], dict[str, Any]]:
    """Split tokens into positionals and ``--key value`` / ``--key=value`` kwargs.

    A repeated ``--key`` accumulates into a list.
    """
    positionals: list[Any] = []
    kwargs: dict[str, Any] = {}
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("--"):
            key = tok[2:]
            if "=" in key:
                key, raw = key.split("=", 1)
            elif i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                raw = tokens[i + 1]
                i += 1
            else:
                raw = "true"  # bare flag -> boolean true
            key = key.replace("-", "_")
            val = _coerce(raw)
            if key in kwargs:
                existing = kwargs[key]
                kwargs[key] = (
                    existing + [val] if isinstance(existing, list) else [existing, val]
                )
            else:
                kwargs[key] = val
        else:
            positionals.append(_coerce(tok))
        i += 1
    return positionals, kwargs


def _bind_positionals(
    method: Any, positionals: list[Any], kwargs: dict[str, Any]
) -> None:
    """Assign positional CLI args to the method's parameters by name (skipping self)."""
    if not positionals:
        return
    params = [
        p
        for p in inspect.signature(method).parameters.values()
        if p.name != "self"
        and p.kind
        in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY)
    ]
    for value, param in zip(positionals, params, strict=False):
        kwargs.setdefault(param.name, value)


def romm_usage() -> str:
    """Build a help string listing every RomM resource and its actions."""
    lines = [
        "RomM (web library) commands — rom-manager <resource> <action> [args]",
        "",
    ]
    for name, _tag, summary, actions in ROMM_TOOLS:
        res = name.removeprefix("romm_")
        lines.append(f"  {res:<14} {summary}")
        lines.append(f"  {'':<14} actions: {', '.join(actions)}")
    lines.append("")
    lines.append("  aliases: " + ", ".join(sorted(ALIASES)))
    return "\n".join(lines)


def run_romm_cli(argv: list[str]) -> int:
    """Dispatch a RomM CLI invocation (CONCEPT:ROM-003). Returns an exit code."""
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(romm_usage())
        return 0

    command = argv[0]
    rest = argv[1:]

    if command in ALIASES:
        resource, action = ALIASES[command]
        # An alias may still take an explicit action override as the next token.
        if (
            rest
            and not rest[0].startswith("-")
            and rest[0] in RESOURCE_ACTIONS.get(resource, {})
        ):
            action = rest[0]
            rest = rest[1:]
    else:
        resource = command
        if not rest:
            print(
                f"Missing action for '{resource}'.\n\n{romm_usage()}", file=sys.stderr
            )
            return 2
        action = rest[0]
        rest = rest[1:]

    actions = RESOURCE_ACTIONS.get(resource)
    if actions is None:
        print(f"Unknown RomM resource '{resource}'.\n\n{romm_usage()}", file=sys.stderr)
        return 2
    method_name = actions.get(action)
    if method_name is None:
        valid = ", ".join(actions)
        print(
            f"Unknown action '{action}' for '{resource}'. Valid: {valid}",
            file=sys.stderr,
        )
        return 2

    positionals, kwargs = _parse_args(rest)
    _bind_positionals(getattr(RommApi, method_name), positionals, kwargs)

    try:
        client = get_romm_client()
        result = getattr(client, method_name)(**kwargs)
    except Exception as e:  # surface a clean error, not a traceback, to the CLI user
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(result, default=str, indent=2))
    return 0
