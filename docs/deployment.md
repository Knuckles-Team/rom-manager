# Deployment

<!-- BEGIN GENERATED: deployment-options -->
## Deployment Options

`rom-manager` supports local stdio, a loopback-only development listener, a
least-privilege stdio container, and a remote authenticated HTTPS boundary.
Provider endpoint, credential, selector, identity, and trust material are supplied
at runtime through `AgentConfig`; none is stored in this repository.

### Installed stdio process

```json
{
  "mcpServers": {
    "rom-manager": {
      "command": "rom-manager-mcp",
      "args": [],
      "env": {"MCP_TOOL_MODE": "intent"}
    }
  }
}
```

### Loopback development listener

```bash
rom-manager-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

Do not expose this listener beyond loopback. Network deployments require direct TLS
or an explicitly trusted TLS-terminating ingress, configured authentication, exact
`MCP_ALLOWED_HOSTS`, and an exact trusted-proxy CIDR policy.

### Least-privilege local container

```bash
docker run -i --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --pids-limit=256 \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m \
  -e TRANSPORT=stdio \
  registry.example.invalid/rom-manager@sha256:<digest> rom-manager-mcp
```

The operator projects the selected AgentConfig profile into the process at runtime;
the image remains immutable and contains no environment connection profile.

### Remote authenticated HTTPS endpoint

```json
{
  "mcpServers": {
    "rom-manager": {"url": "https://service.example.invalid/mcp"}
  }
}
```

Store the real remote URL, outbound identity reference, and TLS-profile reference in
`AgentConfig`, not in MCP client JSON or documentation.
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

The prebuilt image `example/rom-manager` ships with `chdman` (mame-tools)
and `7z` (p7zip-full) so conversions work out of the box. Mount your ROM
directory and set `ROM_DIRECTORY`.

```bash
docker run --rm -it \
  -v /games:/games -e ROM_DIRECTORY=/games \
  -p 8000:8000 -e TRANSPORT=streamable-http \
  example/rom-manager@sha256:<digest>
```

### Docker Compose

```bash
docker compose -f docker/mcp.compose.yml up -d     # MCP only
docker compose -f docker/agent.compose.yml up -d   # MCP + agent
```

!!! note "RVZ output"
    `dolphin-tool` is not packaged in the MCP-serving image. Install it into the
    container (or a derived image) if you need RVZ output.
