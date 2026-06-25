# ROM Manager
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/rom-manager)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/rom-manager)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/rom-manager)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/rom-manager)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/rom-manager)
![PyPI - License](https://img.shields.io/pypi/l/rom-manager)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/rom-manager)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/rom-manager)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/rom-manager)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/rom-manager)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/rom-manager)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/rom-manager)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/rom-manager)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/rom-manager)

*Version: 1.4.0*

> **Documentation** — Installation, deployment, and usage across the API, CLI, and
> MCP interfaces, plus the integrated A2A agent server, are maintained in the
> [official documentation](https://knuckles-team.github.io/rom-manager/).

> ⚠️ **Back up your ROMs before working with this tool.** Conversion and the
> `--delete` / `clean_origin_files` options are destructive to source files.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Usage (CLI or API)](#usage-cli-or-api)
- [MCP](#mcp)
- [Agent](#agent)
- [Environment Variables](#environment-variables)
- [Security & Governance](#security--governance)
- [External Binary Dependencies](#external-binary-dependencies)
- [Installation](#installation)
- [Deployment (agent_server.py)](#deployment-agent_serverpy)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**ROM Manager** is a production-grade ROM converter/organizer with an integrated
Model Context Protocol (MCP) server and Agent-to-Agent (A2A) agent. It extracts
archives, auto-renames ROMs via a known game-code registry, converts ISO/WBFS
images to **CHD** (`chdman`) or **RVZ** (`dolphin-tool`), generates missing `.cue`
sheets, and cleans up source files — in parallel.

It also speaks to **[RomM](https://romm.app)** (`CONCEPT:ROM-003`) — a self-hosted
ROM *library server* — through a full REST client, so one `rom-manager` tool
manages both the files on disk (local conversion) and the web library (RomM).

The local conversion pipeline needs no service URL or credentials; the RomM
client is configured via `ROMM_*` environment variables.

---

## Key Features

- **Real conversion pipeline:** parallel extract → rename → convert (CHD/RVZ) → cleanup.
- **Full RomM REST client (`CONCEPT:ROM-003`):** complete coverage of the RomM API
  (roms, platforms, collections, saves, states, firmware, users, tasks, search,
  config, feeds, devices, …) with Basic/OAuth2 auth — one unified CLI and one
  action-routed MCP tool per resource group.
- **Consolidated Action-Routed MCP Tools:** togglable domains (`conversion`,
  `game-codes`, `romm-*`) minimize token overhead and IDE tool bloat.
- **Integrated Graph Agent:** built-in Pydantic-AI agent (AG-UI / ACP).
- **Native Telemetry & Tracing:** OpenTelemetry exports out of the box.
- **Lazy native deps:** archive backends are optional extras, imported only when used.

---

## Architecture

ROM Manager keeps a single, well-factored pipeline behind three entry surfaces
(CLI, MCP server, A2A agent). The orchestrator (`RomManager`) composes focused
responsibility layers and shells out to external conversion binaries:

```mermaid
flowchart LR
    subgraph Entry["Entry Surfaces"]
        CLI["CLI<br/>rom-manager"]
        MCP["MCP Server<br/>rom-manager-mcp<br/>(CONCEPT:ROM-001/002)"]
        AGENT["A2A Agent<br/>rom-manager-agent"]
    end

    CLI --> RM
    MCP --> API["api_client.Api<br/>(facade)"]
    AGENT --> MCP
    API --> RM

    subgraph Pipeline["RomManager orchestrator"]
        RM["RomManager"] --> ARCH["archives.py<br/>extract + cue"]
        RM --> NAME["naming.py<br/>game-code rename"]
        RM --> CONV["conversion.py<br/>command + runner seam"]
    end

    ARCH --> P7Z["7z / patool"]
    CONV --> CHDMAN["chdman (CHD)"]
    CONV --> DOLPHIN["dolphin-tool (RVZ)"]
    NAME --> CODES["game_codes.py<br/>(PSX registry, DATA)"]
```

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Orchestrator | `rom_manager/rom_manager.py` | Pipeline composition + CLI (`RomManager`, `rom_manager()`). |
| Archives | `rom_manager/archives.py` | Archive detection, extraction, `.cue` generation. |
| Conversion | `rom_manager/conversion.py` | `chdman`/`dolphin-tool` command building + runner seam. |
| Naming | `rom_manager/naming.py` | Game-code lookup + in-place rename. |
| Data | `rom_manager/game_codes.py` | Verbatim PSX serial→title registry (DATA). |
| Facade | `rom_manager/api_client.py` | `Api` wrapper consumed by MCP tools/agent. |

---

## Usage (CLI or API)

This package wraps a local ROM conversion pipeline (`rom_manager.rom_manager.RomManager`).
Use it via the CLI or the `rom_manager.api_client.Api` facade.

```bash
rom-manager --directory "/games/PSX/" --iso chd --verbose
```

| Flag | Long | Description |
|------|------|-------------|
| `-c` | `--cpu-count` | Limit max CPUs for parallel processing |
| `-d` | `--directory` | Directory to process ROMs |
| `-i` | `--iso` | Conversion target: `rvz` or `chd` |
| `-f` | `--force` | Force overwrite of existing `.chd` files |
| `-v` | `--verbose` | Display all output messages |
| `-x` | `--delete` | Delete original files after processing |

Detailed API usage is in [docs/usage.md](docs/usage.md).

### RomM web library (`CONCEPT:ROM-003`)

The same `rom-manager` command manages a running RomM server. Set `ROMM_URL` and
credentials (`ROMM_USERNAME`/`ROMM_PASSWORD` or `ROMM_TOKEN`), then use
`rom-manager <resource> <action> [positionals] [--flag value …]`:

```bash
rom-manager roms list --platform_ids 7 --limit 50   # list/search ROMs
rom-manager roms get 123                             # positional id
rom-manager platforms list
rom-manager saves add --rom_id 5 --file_path ./game.srm
rom-manager tasks run scan                           # trigger a library scan
rom-manager stats                                    # server statistics
```

Resources map 1:1 to `RommApi` methods. The on-disk converter is reachable as
before (bare flags) or via the explicit `rom-manager convert …` alias. From
Python, use `rom_manager.get_romm_client()` → `RommApi`.

---

## MCP

This server utilizes dynamic Action-Routed tools to optimize token overhead and
maximize IDE compatibility.

### Available MCP Tools

The table below is auto-generated from the MCP server — do not edit by hand.

<!-- MCP-TOOLS-TABLE:START -->

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `rom_conversion` | `CONVERSIONTOOL` | Manage ROM conversion operations (CONCEPT:ROM-001). |
| `rom_game_codes` | `GAME_CODESTOOL` | Manage ROM game code lookup and naming operations (CONCEPT:ROM-002). |
| `romm_collections` | `ROMMTOOL` |  |
| `romm_config` | `ROMMTOOL` |  |
| `romm_devices` | `ROMMTOOL` |  |
| `romm_feeds` | `ROMMTOOL` |  |
| `romm_firmware` | `ROMMTOOL` |  |
| `romm_platforms` | `ROMMTOOL` |  |
| `romm_roms` | `ROMMTOOL` |  |
| `romm_saves` | `ROMMTOOL` |  |
| `romm_screenshots` | `ROMMTOOL` |  |
| `romm_search` | `ROMMTOOL` |  |
| `romm_states` | `ROMMTOOL` |  |
| `romm_system` | `ROMMTOOL` |  |
| `romm_tasks` | `ROMMTOOL` |  |
| `romm_users` | `ROMMTOOL` |  |

_16 action-routed tools (default `MCP_TOOL_MODE=condensed`). Each is enabled unless its toggle is set false; set `MCP_TOOL_MODE=verbose` (or `both`) for the 1:1 per-operation surface. Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->

### Dynamic Tool Selection

Each domain is gated by an environment toggle (default `True`). Set a toggle to
`False` to omit that tool from the registered surface.

### Running the MCP server

```bash
# stdio (default)
rom-manager-mcp

# Streamable HTTP
rom-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

> **Install the slim `[mcp]` extra.** The examples below install
> `rom-manager[mcp]` — the MCP-server extra that pulls only the FastMCP / FastAPI
> tooling (`agent-utilities[mcp]`). It deliberately **excludes** the heavy agent
> runtime (the epistemic-graph engine, `pydantic-ai`, `dspy`, `llama-index`,
> `tree-sitter`), so `uvx`/container installs are dramatically smaller and faster.
> Use the full `[agent]` extra only when you need the integrated Pydantic AI agent
> (see [Installation](#installation)).

#### stdio client config

```json
{
  "mcpServers": {
    "rom-manager": {
      "command": "uvx",
      "args": ["--from", "rom-manager[mcp]", "rom-manager-mcp"],
      "env": { "ROM_DIRECTORY": "/games", "CONVERSIONTOOL": "True", "GAME_CODESTOOL": "True" }
    }
  }
}
```

#### Docker

```bash
docker run --rm -it -v /games:/games -e ROM_DIRECTORY=/games \
  -p 8000:8000 -e TRANSPORT=streamable-http knucklessg1/rom-manager:mcp
```

> The `:mcp` tag is the **slim MCP-server image** (built from
> `docker/Dockerfile --target mcp`, installing `rom-manager[mcp]`). The default
> `:latest` tag is the **full agent image** (`--target agent`, `rom-manager[agent]`)
> which also bundles the Pydantic AI agent and the epistemic-graph engine — use it
> when you run `rom-manager-agent` (the agent), not just the MCP server. See
> [Container images](#container-images-mcp-vs-agent).

---

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`rom-manager` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/rom-manager/deployment/) has full, copy-paste
`mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://rom-manager-mcp.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->

## Agent

ROM Manager ships a Pydantic-AI agent (`rom-manager-agent`) that calls the MCP
tool surface and exposes an AG-UI web interface. Its identity lives in
`rom_manager/agent_data/IDENTITY.md`.

```bash
rom-manager-agent --web
```

---

## Environment Variables

<!-- ENV-VARS-TABLE:START -->

#### Package environment variables

| Variable | Example | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` |  |
| `PORT` | `8000` |  |
| `TRANSPORT` | `stdio` | options: stdio, streamable-http, sse |
| `AUTH_TYPE` | `none` | Authentication mode for the MCP server (none for this local tool). |
| `FASTMCP_LOG_LEVEL` | `ERROR` | FastMCP internal log verbosity (the server pins this to ERROR at startup). |
| `NO_COLOR` | `1` | Disable ANSI colour output in child tooling. |
| `TERM` | `dumb` | Force a dumb terminal so progress bars / colour codes do not corrupt stdio. |
| `ENABLE_OTEL` | `True` |  |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:8080/api/public/otel` |  |
| `OTEL_EXPORTER_OTLP_PUBLIC_KEY` | `pk-...` |  |
| `OTEL_EXPORTER_OTLP_SECRET_KEY` | `sk-...` |  |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` |  |
| `EUNOMIA_TYPE` | `none` | options: none, embedded, remote |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` |  |
| `EUNOMIA_REMOTE_URL` | `http://eunomia-server:8000` |  |
| `ROM_DIRECTORY` | `./roms` | Default directory of ROMs to process when none is supplied. |
| `ROM_ISO_TYPE` | `chd` | Conversion target: chd (chdman) or rvz (dolphin-tool) |
| `ROM_VERBOSE` | `False` |  |
| `ROM_FORCE` | `False` |  |
| `ROMM_URL` | `http://localhost:3000` | any RomM (`roms`, `platforms`, ...) command or MCP tool. |
| `ROMM_USERNAME` | `admin` | Credentials: Basic/OAuth username+password, or a pre-minted bearer token. |
| `ROMM_PASSWORD` | `changeme` |  |
| `ROMM_TOKEN` | — |  |
| `ROMM_AUTH_MODE` | `basic` | Auth mode: basic (default, no expiry) or oauth (password grant via /api/token). |
| `ROMM_SCOPES` | `roms.read roms.write platforms.read` | Space-separated OAuth scopes (defaults to RomM's full read+write set). |
| `ROMM_SSL_VERIFY` | `True` |  |
| `CONVERSIONTOOL` | `True` | MCP tools table (condensed action-routed surface). |
| `GAME_CODESTOOL` | `True` |  |
| `ROMMTOOL` | `True` | Master switch for the RomM remote-library tools. |

#### Inherited agent-utilities variables (apply to every connector)

| Variable | Example | Description |
|----------|---------|-------------|
| `MCP_TOOL_MODE` | `condensed` | Tool surface: `condensed` | `verbose` | `both` |
| `MCP_ENABLED_TOOLS` | — | Comma-separated tool allow-list |
| `MCP_DISABLED_TOOLS` | — | Comma-separated tool deny-list |
| `MCP_ENABLED_TAGS` | — | Comma-separated tag allow-list |
| `MCP_DISABLED_TAGS` | — | Comma-separated tag deny-list |
| `MCP_CLIENT_AUTH` | — | Outbound MCP auth (`oidc-client-credentials` for fleet calls) |
| `OIDC_CLIENT_ID` | — | OIDC client id (service-account auth) |
| `OIDC_CLIENT_SECRET` | — | OIDC client secret (service-account auth) |
| `DEBUG` | `False` | Verbose logging |
| `PYTHONUNBUFFERED` | `1` | Unbuffered stdout (recommended in containers) |
| `MCP_URL` | `http://localhost:8000/mcp` | URL of the MCP server the agent connects to |
| `PROVIDER` | `openai` | LLM provider for the agent |
| `MODEL_ID` | `gpt-4o` | Model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_29 package + 14 inherited variable(s). Auto-generated from `.env.example` + the shared agent-utilities set — do not edit._
<!-- ENV-VARS-TABLE:END -->


All settings are optional — ROM Manager runs with sensible defaults and requires
no credentials. Copy [`.env.example`](.env.example) to `.env` to override.

### Application Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ROM_DIRECTORY` | `.` (cwd) | Default directory of ROMs to process when none is supplied. |
| `ROM_ISO_TYPE` | `chd` | Conversion target: `chd` (chdman) or `rvz` (dolphin-tool). |
| `ROM_VERBOSE` | `False` | Emit verbose conversion output. |
| `ROM_FORCE` | `False` | Force overwrite of existing converted files. |
| `CONVERSIONTOOL` | `True` | Toggle registration of the **conversion** MCP tool domain (`CONCEPT:ROM-001`). |
| `GAME_CODESTOOL` | `True` | Toggle registration of the **game-codes** MCP tool domain (`CONCEPT:ROM-002`). |
| `ROMMTOOL` | `True` | Toggle registration of the **RomM** MCP tool domains (`CONCEPT:ROM-003`). |

> CPU count and "delete originals" are exposed as CLI flags (`--cpu-count` /
> `--delete`) and MCP action params (`cpu_count` / `clean_origin_files`) rather
> than environment variables.

### RomM Variables (`CONCEPT:ROM-003`)

Required only when using RomM (`roms`, `platforms`, … commands / `romm_*` tools).

| Variable | Default | Description |
|----------|---------|-------------|
| `ROMM_URL` | — | Base URL of the RomM instance (e.g. `http://host:3000`). **Required** for RomM. |
| `ROMM_USERNAME` / `ROMM_PASSWORD` | — | Basic or OAuth password-grant credentials. |
| `ROMM_TOKEN` | — | Pre-minted OAuth2 bearer token (takes precedence over username/password). |
| `ROMM_AUTH_MODE` | `basic` | `basic` (no expiry) or `oauth` (password grant via `/api/token`, auto-refresh). |
| `ROMM_SCOPES` | RomM full set | Space-separated OAuth scopes requested when minting a token. |
| `ROMM_SSL_VERIFY` | `True` | Verify TLS certificates. |

### MCP / Framework Variables (agent-utilities)

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind host for HTTP/SSE transports. |
| `PORT` | `8000` | Bind port for HTTP/SSE transports. |
| `TRANSPORT` | `stdio` | MCP transport: `stdio`, `streamable-http`, or `sse`. |
| `AUTH_TYPE` | `none` | MCP authentication mode (this local tool needs none). |
| `FASTMCP_LOG_LEVEL` | `ERROR` | FastMCP internal log verbosity (pinned at startup). |
| `ENABLE_OTEL` | `True` | Enable OpenTelemetry export of traces/metrics. |
| `EUNOMIA_TYPE` | `none` | Eunomia authorization mode: `none`, `embedded`, or `remote`. |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` | Path to the Eunomia policy file when embedded. |

### Terminal Variables

These are set automatically by the server to keep stdio transport clean; you do
not normally set them yourself.

| Variable | Default | Description |
|----------|---------|-------------|
| `NO_COLOR` | `1` | Disable ANSI colour codes in child tooling output. |
| `TERM` | `dumb` | Force a dumb terminal so progress output does not corrupt the stdio channel. |

---

## Security & Governance

- **No credentials:** ROM Manager is a local tool with no service URL/token.
- **Eunomia policies & OpenTelemetry:** inherited from the `agent-utilities`
  middleware (see `.env.example`).
- **Destructive-op safety:** the agent recommends backing up ROMs before
  `clean_origin_files`/delete operations.

---

## External Binary Dependencies

Conversion *actions* shell out to native tools (the Python package installs fine
without them):

- **`chdman`** (CHD) — `apt install mame-tools` (Ubuntu) or MAME tools on Windows.
- **`dolphin-tool`** (RVZ) — see the Dolphin emulator docs.
- **`7z` / archive backends** (extraction) — `apt install p7zip-full`; pair with
  the `rom-manager[native]` extra (`patool`).

---

## Installation

Pick the extra that matches what you want to run:

| Extra | Installs | Use when |
|-------|----------|----------|
| `rom-manager` (core) | CLI converter + `Api` facade (no server tooling) | You only use the **CLI / Python API** |
| `rom-manager[mcp]` | Slim MCP server (`agent-utilities[mcp]` — FastMCP/FastAPI) | You run the **MCP server** (smallest server install / image) |
| `rom-manager[agent]` | Full agent runtime (`agent-utilities[agent,logfire]` — Pydantic AI + the epistemic-graph engine) | You run the **integrated agent** |
| `rom-manager[native]` | + `patool` (archive extraction backends) | You convert archived ROMs locally |
| `rom-manager[all]` | Everything (`mcp` + `agent` + `native` + `otel`) | Development / all surfaces |

```bash
pip install rom-manager            # core CLI + Api
pip install "rom-manager[mcp]"     # + slim MCP server
pip install "rom-manager[agent]"   # + A2A agent (Pydantic AI + epistemic-graph engine)
pip install "rom-manager[native]"  # + patool (archive extraction)
pip install "rom-manager[all]"     # everything
```

### Container images (`:mcp` vs `:agent`)

One multi-stage `docker/Dockerfile` builds two right-sized images, selected by `--target`:

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|
| `knucklessg1/rom-manager:mcp` | `--target mcp` | `rom-manager[mcp]` — **slim**, no engine/`pydantic-ai`/`dspy`/`llama-index`/`tree-sitter` | `rom-manager-mcp` |
| `knucklessg1/rom-manager:latest` | `--target agent` (default) | `rom-manager[agent]` — **full** agent runtime + epistemic-graph engine | `rom-manager-agent` |

```bash
docker build --target mcp   -t knucklessg1/rom-manager:mcp    docker/   # slim MCP server
docker build --target agent -t knucklessg1/rom-manager:latest docker/   # full agent
```

`docker/mcp.compose.yml` runs the slim `:mcp` server; `docker/agent.compose.yml` runs the
agent (`:latest`) with a co-located `:mcp` sidecar.

### Knowledge-graph database (`epistemic-graph`)

The **full agent** (`[agent]` / `:latest`) embeds the **epistemic-graph** engine (pulled in
transitively via `agent-utilities[agent]`). For production — or to share one knowledge graph
across multiple agents — run **epistemic-graph as its own database container** and point the
agent at it instead of embedding it. Deployment recipes (single-node + Raft HA), connection
config, and the full database architecture (with diagrams) are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).
The slim `[mcp]` server and the core CLI do **not** require the database.

---

## Deployment (agent_server.py)

`rom-manager-agent` (entry point `rom_manager.agent_server:agent_server`) starts a
Pydantic-AI A2A agent that auto-discovers the MCP tool surface from
`mcp_config.json` and can expose an AG-UI web interface.

```bash
# Local: web UI on the default host/port, OTEL enabled
rom-manager-agent --web --otel \
  --provider openai --model-id gpt-4o-mini \
  --host 0.0.0.0 --port 8080
```

Container deployment (compose):

```yaml
# docker/agent.compose.yml (excerpt)
services:
  rom-manager-agent:
    image: knucklessg1/rom-manager:latest
    command: ["rom-manager-agent", "--web"]
    environment:
      ROM_DIRECTORY: /games
      TRANSPORT: streamable-http
      HOST: 0.0.0.0
      PORT: 8080
      ENABLE_OTEL: "True"
      AUTH_TYPE: none
    volumes:
      - /srv/roms:/games
    ports:
      - "8080:8080"
```

The MCP server (`rom-manager-mcp`) deploys the same way; see
[docs/deployment.md](docs/deployment.md) for the full compose/Swarm recipes.

---

## Documentation

- [Installation](docs/installation.md)
- [Deployment](docs/deployment.md)
- [Usage (API / CLI / MCP)](docs/usage.md)
- [Overview](docs/overview.md)
- [Concepts (`CONCEPT:ROM-*`)](docs/concepts.md)

---

## Contributing

Contributions are welcome. Run `pre-commit run --all-files` before opening a PR.
Preserve the real conversion pipeline — wrap `RomManager`, do not break it.

## License

MIT © Knuckles-Team


<!-- BEGIN agent-os-genesis-deploy (generated; do not edit between markers) -->

## Deploy with `agent-os-genesis`

This package can be provisioned for you — skill-guided — by the **`agent-os-genesis`**
universal skill (its *single-package deploy mode*): it picks your install method, seeds
secrets to OpenBao/Vault (or `.env`), trusts your enterprise CA, registers the MCP
server, and verifies it — the same machinery that stands up the whole Agent OS, narrowed
to just this package. Ask your agent to **"deploy `rom-manager` with agent-os-genesis"**.

| Install mode | Command |
|------|---------|
| Bare-metal, prod (PyPI) | `uvx rom-manager-mcp` · or `uv tool install rom-manager` |
| Bare-metal, dev (editable) | `uv pip install -e ".[all]"` · or `pip install -e ".[all]"` |
| Container, prod | deploy `knucklessg1/rom-manager:latest` via docker-compose / swarm / podman / podman-compose / kubernetes |
| Container, dev (editable) | deploy `docker/compose.dev.yml` (source-mounted at `/src`; edits live on restart) |

Secrets are read-existing + seeded via `vault_sync` — you are only prompted for what's missing.

<!-- END agent-os-genesis-deploy -->
