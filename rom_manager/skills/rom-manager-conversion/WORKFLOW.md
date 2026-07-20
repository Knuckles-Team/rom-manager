# Rom Manager Conversion

Convert and organise ROM/disc images on local disk via the rom-manager MCP server — convert ISO/WBFS to space-efficient CHD (chdman) or RVZ (dolphin-tool), extract archives, generate .cue sheets for multi-track .bin sets, and list candidate files. Use when the agent must shrink a disc-image library, prep a directory of ROMs, or rebuild missing cue sheets. Do NOT use for browsing a RomM server (rom-manager-library-sync) or resolving serial codes to titles (rom-manager-game-codes).

# ROM Manager — Conversion & Organising

Local, filesystem-side ROM operations through the `rom-manager` MCP server:
convert disc images to compressed formats, extract archives, and generate cue
sheets. Requires the external `chdman` and/or `dolphin-tool` binaries for the
conversion actions.

## When to use
- Convert ISO/WBFS disc images to **CHD** (`chdman`) or **RVZ** (`dolphin-tool`) to
  reclaim storage; report the size delta.
- Extract archives (`.zip`, `.7z`, …) into a working directory.
- Generate a `.cue` sheet for a directory of multi-track `.bin` files.
- List candidate ROM/image files in a directory before acting.

## When NOT to use
- Browse / sync a remote RomM library, or ingest games into the KG →
  `rom-manager-library-sync`.
- Resolve a serial code to a clean title, or rename by code →
  `rom-manager-game-codes`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`rom-manager`** MCP server. This
is a **local** tool — no service URL or credentials — but conversion needs binaries:

| Requirement | Notes |
|-------------|-------|
| `chdman` on `PATH` | required for `iso_type=chd` conversion |
| `dolphin-tool` on `PATH` | required for `iso_type=rvz` conversion |
| `patool` (extra `native`/`convert`) | required for archive extraction |
| `ROM_DIRECTORY` (env) | default working directory when `directory` omitted |
| `ROM_ISO_TYPE` (env) | default target format (`chd` or `rvz`) |

## Tools & actions
One condensed tool, `action` + `params_json` **JSON string**.

| Condensed tool | Actions |
|----------------|---------|
| `rom_conversion` | `convert`, `process_directory`, `process_file`, `generate_cue`, `list_files` |

### Key parameters
- `directory` — target directory (defaults to `ROM_DIRECTORY`).
- `file` — a single file for `process_file`.
- `iso_type` — `chd` or `rvz` (conversion target).
- `cpu_count` — parallelism for batch conversion.
- `force` — reconvert even if a target already exists.
- `clean_origin_files` — delete source images after a successful convert (**off by
  default** — only set when explicitly asked).
- `verbose` — emit tool output.

## Recipes (`params_json`)
Convert a whole directory to CHD, keeping origins:
```json
{"directory": "/roms/psx", "iso_type": "chd", "clean_origin_files": false}
```
Convert one GameCube ISO to RVZ:
```json
{"file": "/roms/gc/game.iso", "iso_type": "rvz"}
```
Generate a cue sheet for a multi-track dump:
```json
{"directory": "/roms/psx/Some Game (Disc 1)"}
```
List convertible files first:
```json
{"directory": "/roms/psx"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Conversion actions fail cleanly if `chdman`/`dolphin-tool` is not on `PATH`;
  install them (or the `native` extra) first.
- `clean_origin_files` is destructive — it deletes the source images; default is
  false and it should stay false unless the user explicitly asks to reclaim space.
- CHD is for CD/DVD disc images (PSX, Saturn, Dreamcast, …); RVZ is for
  GameCube/Wii — pick `iso_type` to match the platform.
- `generate_cue` expects the `.bin` track files already present in `directory`.

## Related
- **Remote library / KG ingest:** `rom-manager-library-sync`.
- **Naming / serial-code resolution:** `rom-manager-game-codes`.
- After converting, ingest the resulting bytes as a `:AssetOccurrence` blob via
  `rom_manager.kg_media.ingest_rom_file` (internal seam).
