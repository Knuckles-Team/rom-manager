# Usage

## CLI

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

## Python API (local facade)

```python
from rom_manager.api_client import Api

api = Api(directory="/games/PSX/", iso_type="chd")
result = api.convert()                       # full pipeline over the directory
print(result["storage_delta_gb"])

api.lookup_game_code("SLUS-00594")           # {'code': ..., 'name': ...}
api.list_game_codes(prefix="SLUS")           # filtered registry
```

## MCP tools

The MCP server exposes two action-routed tools. Pass an `action` and a
`params_json` JSON string.

```jsonc
// conversion tool
{ "action": "convert", "params_json": "{\"directory\": \"/games/PSX/\", \"iso_type\": \"chd\"}" }
{ "action": "generate_cue", "params_json": "{\"directory\": \"/games/PSX/Game/\"}" }

// game-codes tool
{ "action": "lookup", "params_json": "{\"code\": \"SLUS-00594\"}" }
{ "action": "list",   "params_json": "{\"prefix\": \"SLUS\"}" }
{ "action": "rename", "params_json": "{\"file\": \"/games/PSX/SLUS-00594.cue\"}" }
```

Run the server:

```bash
rom-manager-mcp                                              # stdio
rom-manager-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```
