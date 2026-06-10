# rom-manager

**ROM Converter/Organizer + MCP Server + A2A Agent** for the agent-utilities
ecosystem — convert game ROMs to CHD/RVZ, extract archives, auto-rename via known
game codes, and generate cue sheets.

!!! info "Official documentation"
    This site is the canonical reference for `rom-manager`, maintained alongside every
    release.

[![PyPI](https://img.shields.io/pypi/v/rom-manager)](https://pypi.org/project/rom-manager/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/rom-manager)](https://github.com/Knuckles-Team/rom-manager/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/rom-manager)

## Overview

`rom-manager` wraps a local ROM conversion pipeline with typed, deterministic MCP
tools and an optional Pydantic-AI agent server. It provides:

- **`RomManager`** — the real conversion pipeline (`rom_manager.rom_manager`):
  extract archives → rename via game codes → convert ISO/WBFS to CHD/RVZ via
  `chdman`/`dolphin-tool` → cleanup.
- **Action-routed MCP tools** — two consolidated, togglable domains
  (`conversion`, `game-codes`) that minimize token overhead in LLM contexts.
- **An A2A agent server** — a Pydantic-AI agent (console script `rom-manager-agent`)
  that calls the MCP tool surface and exposes an AG-UI web interface.

This is a **local tool**: there is no service URL and no credentials. Conversion
actions require the external `chdman` (mame-tools), `dolphin-tool`, and `7z`
binaries.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, external binaries, and Docker.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` facade, and the CLI.
- :material-sitemap: **[Overview](overview.md)** — the action-routed tool surface and architecture.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:ROM-*` registry.

</div>

## Quick start

```bash
pip install "rom-manager[mcp]"
rom-manager-mcp                   # stdio MCP server (default transport)
```

Convert a directory of ROMs from the CLI:

```bash
rom-manager --directory "/games/PSX/" --iso chd --verbose
```
