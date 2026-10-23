# CONN-ROM-MANAGER-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `rom-manager-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `rom_manager` from it.
