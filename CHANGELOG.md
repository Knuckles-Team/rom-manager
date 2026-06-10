# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Action-routed MCP server (`rom-manager-mcp`) exposing the `conversion` and
  `game-codes` tool domains (CONCEPT:ROM-001, CONCEPT:ROM-002).
- Pydantic-AI A2A agent server (`rom-manager-agent`) with `agent_data/IDENTITY.md`.
- Honest local `api_client.Api` facade and no-op `auth.get_client` factory.
- Pydantic input/output models (`models.py`).
- Golden `pyproject.toml` packaging; `setup.py` removed.
- Docker (multi-stage) + compose files, mkdocs documentation site, and tests.

### Changed
- `patool` moved to an optional `native`/`convert` extra and lazily imported
  inside `RomManager.process_archive` (install with `rom-manager[native]`).

## [0.0.27]

### Added
- Initial release (CLI ROM converter).
