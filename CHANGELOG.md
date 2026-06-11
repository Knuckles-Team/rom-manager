# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **RomM (romm.app) remote-library integration** (`CONCEPT:ROM-003`). The package
  now manages both ROM files on disk *and* a running RomM library server:
  - `rom_manager/romm/` — a full `RommApi` REST client (one mixin per resource:
    roms, platforms, collections, saves, states, screenshots, firmware, users,
    tasks, search, config, feeds, devices, system/auth) with Basic + OAuth2
    password-grant auth (transparent 401 refresh) and streamed up/downloads.
    Covers **all 126** RomM operations (parity-guarded against the vendored
    `romm/openapi.json`).
  - `get_romm_client` factory reading `ROMM_URL`, `ROMM_USERNAME`/`ROMM_PASSWORD`
    or `ROMM_TOKEN`, `ROMM_AUTH_MODE`, `ROMM_SCOPES`, `ROMM_SSL_VERIFY` (optional
    OIDC delegation).
  - One action-routed MCP tool per RomM resource group (`romm_roms`,
    `romm_platforms`, …), gated by the `ROMMTOOL` flag.
  - Unified CLI: the existing `rom-manager` entry point gains `convert` and RomM
    subcommands (e.g. `rom-manager roms list --platform_ids 7`, `rom-manager
    stats`); legacy on-disk conversion flags are unchanged.
- `requests` added to core dependencies.

## [1.0.0] - 2026-06-10

### Added

- Action-routed MCP server (`rom-manager-mcp`) exposing the `conversion` and
  `game-codes` tool domains (`CONCEPT:ROM-001`, `CONCEPT:ROM-002`).
- Pydantic-AI A2A agent server (`rom-manager-agent`) with
  `agent_data/IDENTITY.md`.
- Honest local `api_client.Api` facade and no-op `auth.get_client` factory.
- Pydantic input/output models (`models.py`).
- Responsibility layers split out of the former `rom_manager.py` god module:
  `archives.py` (extract + cue), `conversion.py` (chdman/dolphin-tool command
  building + an injectable runner seam), and `naming.py` (game-code rename).
- Concept traceability: `concept` pytest marker plus `@pytest.mark.concept(...)`
  decorators and `CONCEPT:ROM-*` docstring markers across code, tests, and
  `docs/concepts.md`.
- Comprehensive README Environment Variables table, architecture overview with a
  Mermaid diagram, Table of Contents, and `agent_server.py` deployment config.
- Unit tests for the new archive, conversion, and naming layers (mocking the
  external-binary runner seam so no native tools are required).
- Docker (multi-stage) + compose files, mkdocs documentation site.

### Changed

- `RomManager` is now an orchestrator that composes the archive/conversion/naming
  layers; its public API (`RomManager`, `rom_manager()`) is unchanged.
- `patool` moved to an optional `native`/`convert` extra and lazily imported
  inside the archive layer (install with `rom-manager[native]`).
- Migrated packaging from `setup.py` to a golden `pyproject.toml`.

### Removed

- `setup.py` (superseded by `pyproject.toml`).

## [0.0.27] - 2024-01-01

### Added

- Initial release: parallel CLI ROM converter (CHD/RVZ) with archive extraction,
  cue-sheet generation, and PSX game-code renaming.

[Unreleased]: https://github.com/Knuckles-Team/rom-manager/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Knuckles-Team/rom-manager/compare/v0.0.27...v1.0.0
[0.0.27]: https://github.com/Knuckles-Team/rom-manager/releases/tag/v0.0.27
