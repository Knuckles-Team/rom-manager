# Deployment

## Console scripts

| Script | Entrypoint | Purpose |
|--------|------------|---------|
| `rom-manager` | `rom_manager.rom_manager:rom_manager` | Local CLI converter |
| `rom-manager-mcp` | `rom_manager.mcp_server:mcp_server` | MCP server |
| `rom-manager-agent` | `rom_manager.agent_server:agent_server` | A2A agent server |

## Transports

```bash
rom-manager-mcp                                              # stdio (default)
rom-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
rom-manager-mcp --transport sse --host 0.0.0.0 --port 8000
```

## Docker

The prebuilt image `knucklessg1/rom-manager` ships with `chdman` (mame-tools)
and `7z` (p7zip-full) so conversions work out of the box. Mount your ROM
directory and set `ROM_DIRECTORY`.

```bash
docker run --rm -it \
  -v /games:/games -e ROM_DIRECTORY=/games \
  -p 8000:8000 -e TRANSPORT=streamable-http \
  knucklessg1/rom-manager:latest
```

### Docker Compose

```bash
docker compose -f docker/mcp.compose.yml up -d     # MCP only
docker compose -f docker/agent.compose.yml up -d   # MCP + agent
```

!!! note "RVZ output"
    `dolphin-tool` is not packaged in the slim image. Install it into the
    container (or a derived image) if you need RVZ output.
