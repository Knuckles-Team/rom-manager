# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`rom-manager` exposes its MCP server (console script `rom-manager-mcp`) four ways. Pick the row that
matches where the server runs relative to your MCP client, then copy the matching
`mcp_config.json` below. Add the service-connection environment variables documented in the **Configuration** section.

| # | Option | Transport | Where it runs | `mcp_config.json` key |
|---|--------|-----------|---------------|------------------------|
| 1 | stdio | `stdio` | client launches a subprocess | `command` |
| 2 | Streamable-HTTP (local) | `streamable-http` | a local network port | `command` or `url` |
| 3 | Local container / uv | `stdio` or `streamable-http` | Docker / Podman / uv on this host | `command` or `url` |
| 4 | Remote URL | `streamable-http` | a remote host behind Caddy | `url` |

### 1. stdio (local subprocess)

The client launches the server over stdio via `uvx` — best for local IDEs
(Cursor, Claude Desktop, VS Code):

```json
{
  "mcpServers": {
    "rom-manager-mcp": {
      "command": "uvx",
      "args": ["--from", "rom-manager", "rom-manager-mcp"]
    }
  }
}
```

### 2. Streamable-HTTP (local process)

Run the server as a long-lived HTTP process:

```bash
uvx --from rom-manager rom-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
curl -s http://localhost:8000/health        # {"status":"OK"}
```

Then either let the client launch it:

```json
{
  "mcpServers": {
    "rom-manager-mcp": {
      "command": "uvx",
      "args": ["--from", "rom-manager", "rom-manager-mcp", "--transport", "streamable-http", "--port", "8000"],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000"
      }
    }
  }
}
```

…or connect to the already-running process by URL:

```json
{
  "mcpServers": {
    "rom-manager-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

### 3. Local container / uv

**(a) Launch a container directly from `mcp_config.json`** (stdio over the container —
no ports to manage). Swap `docker` for `podman` for a daemonless runtime:

```json
{
  "mcpServers": {
    "rom-manager-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "TRANSPORT=stdio",
        "knucklessg1/rom-manager:latest"
      ]
    }
  }
}
```

**(b) Run a local streamable-http container, then connect by URL:**

```bash
docker run -d --name rom-manager-mcp -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e PORT=8000 \
  knucklessg1/rom-manager:latest
# or, from a clone of this repo:
docker compose -f docker/mcp.compose.yml up -d
```

```json
{
  "mcpServers": {
    "rom-manager-mcp": { "url": "http://localhost:8000/mcp" }
  }
}
```

**(c) From a local checkout with `uv`:**

```bash
uv run rom-manager-mcp --transport streamable-http --port 8000
```

### 4. Remote URL (deployed behind Caddy)

When the server is deployed remotely (e.g. as a Docker service) and published through
Caddy on the internal `*.arpa` zone, connect with the `"url"` key — no local process or
image required:

```json
{
  "mcpServers": {
    "rom-manager-mcp": { "url": "http://rom-manager-mcp.arpa/mcp" }
  }
}
```

Caddy reverse-proxies `http://rom-manager-mcp.arpa` to the container's `:8000`
streamable-http listener; `http://rom-manager-mcp.arpa/health` returns
`{"status":"OK"}` when the service is live.
<!-- END GENERATED: deployment-options -->

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
