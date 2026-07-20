# Rom Manager Game Codes

Resolve game serial/product codes to clean titles and rename ROM files by their embedded code via the rom-manager MCP server — look up a code (e.g. SLUS-00594), list the known code registry, or rename a file in-place from its code. Use when the agent must normalise cryptic ROM filenames or map a serial to a human title. Do NOT use for ISO->CHD/RVZ conversion (rom-manager-conversion) or browsing a RomM server (rom-manager-library-sync).

# ROM Manager — Game Codes & Naming

Domain-typed access to the `rom-manager` game-code registry: turn a game serial /
product code into its clean title, and rename ROM files in place using the code
embedded in their filename.

## When to use
- Resolve a serial/product code (e.g. `SLUS-00594`, `SLES-02731`) to a title.
- Normalise a directory of cryptically-named ROMs into clean, human titles.
- Inspect the known code→title registry.

## When NOT to use
- Convert/extract/cue disc images → `rom-manager-conversion`.
- Browse or sync a remote RomM library, or ingest into the KG →
  `rom-manager-library-sync`.
- Rich metadata scraping (cover art, release year, genres) from a provider — that
  comes from RomM's own metadata (see `romm_search` in `rom-manager-library-sync`),
  not this local code table.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`rom-manager`** MCP server. This is
a **local** tool — no service URL or credentials. `ROM_DIRECTORY` (env) supplies the
default directory when one is not passed to `rename`.

## Tools & actions
One condensed tool, `action` + `params_json` **JSON string**.

| Condensed tool | Actions |
|----------------|---------|
| `rom_game_codes` | `lookup`, `list`, `rename` |

### Key parameters
- `code` — the serial/product code for `lookup` (e.g. `SLUS-00594`).
- `file` / `directory` — target for `rename` (rename a single file or a directory
  of files by their embedded codes).

## Recipes (`params_json`)
Look up one code:
```json
{"code": "SLUS-00594"}
```
List the known registry:
```json
{}
```
Rename a directory of ROMs by embedded code:
```json
{"directory": "/roms/psx"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- `lookup` returns `null` (no match) for codes not in the local registry — that is a
  clean miss, not an error; fall back to RomM metadata (`romm_search`) for unknown
  titles.
- `rename` edits files **in place**; run `lookup` / a dry read first if unsure.
- Codes are region-specific (`SLUS`=US, `SLES`=EU, `SLPS`=JP, …) — the same game has
  different serials per region.

## Related
- **Remote metadata / library:** `rom-manager-library-sync` (`romm_search` for
  provider-backed cover art + titles).
- **Conversion / organising:** `rom-manager-conversion`.
