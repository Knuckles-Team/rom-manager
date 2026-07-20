# Rom Manager Library Sync

Browse and sync a RomM (romm.app) game library via the rom-manager MCP server — list/search ROMs and platforms, browse collections, look up a ROM by hash, and natively ingest games/systems into the knowledge graph as typed :Game/:GameSystem nodes. Use when the agent must inventory a RomM server, find a specific game, reconcile a library by CRC/MD5/SHA1 hash, or push the catalogue into the KG. Do NOT use for on-disk ISO->CHD/RVZ conversion (rom-manager-conversion) or resolving a serial code to a title (rom-manager-game-codes).

# ROM Manager — Library Sync

Domain-typed access to a **RomM** remote game library through the `rom-manager`
MCP server, plus the native path that mirrors the catalogue into the knowledge
graph as typed `:Game` / `:GameSystem` / `:GameCollection` nodes.

## When to use
- Inventory a RomM server: list platforms, list/search ROMs, browse collections.
- Find a game by name/filter, or reconcile one by CRC/MD5/SHA1/RA hash.
- Read attached assets: saves, save-states, firmware.
- Push the library into the KG (`rom_ingest_roms` / `rom_ingest_platforms`).

## When NOT to use
- Convert disc images to CHD/RVZ, extract archives, generate cue sheets →
  `rom-manager-conversion`.
- Resolve a serial code (e.g. `SLUS-00594`) to a clean title, or rename by code →
  `rom-manager-game-codes`.
- Arbitrary RomM admin (users, tasks, config, feeds) not covered below → use the
  matching `romm_*` action directly (`romm_users`, `romm_tasks`, `romm_config`,
  `romm_feeds`, `romm_devices`, `romm_system`).

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`rom-manager`** MCP server. The
RomM tools require a reachable RomM server + credentials:

| Variable | Required | Notes |
|----------|----------|-------|
| `ROMM_URL` | ✅ | RomM base URL (e.g. `[configured-endpoint]`) |
| `ROMM_USERNAME` / `ROMM_PASSWORD` | ✅ (basic) | Basic-auth, or OAuth2 password grant |
| `ROMM_TOKEN` | optional | Pre-minted bearer access token |
| `ROMM_AUTH_MODE` | optional | `basic` (default) or `oauth` |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed action-routed
surface (used below) vs. the one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tools; each takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the `RommApi` method.

| Condensed tool | Key actions |
|----------------|-------------|
| `romm_roms` | `list`, `get`, `by_hash`, `by_metadata_provider`, `filters`, `search`, `download` |
| `romm_platforms` | `list`, `supported`, `get` |
| `romm_collections` | `list`, `get`, `smart_list`, `virtual_list` |
| `romm_saves` / `romm_states` / `romm_firmware` | `list`, `get`, `download` |
| `rom_ingest_roms` | (no action) lists ROMs and pushes `:Game` (+`:GameSystem`) nodes |
| `rom_ingest_platforms` | (no action) lists platforms and pushes `:GameSystem` nodes |
| `rom_ingest_collections` | (no action) lists collections and pushes `:GameCollection` nodes |

### Key parameters
- `list_roms` accepts any `GET /api/roms` query param: `search_term`, `platform_ids`,
  `collection_id`, `favorite`, `order_by`, `order_dir`, `limit`, `offset`.
- `by_hash` takes one of `crc_hash` / `md5_hash` / `sha1_hash` / `ra_hash`.
- `get` (rom/platform/collection) takes `id`.

## Recipes (`params_json`)
List the first 25 ROMs on a platform, newest first:
```json
{"platform_ids": 12, "order_by": "name", "order_dir": "asc", "limit": 25, "offset": 0}
```
Find a ROM by CRC32 (dedup / identification):
```json
{"crc_hash": "1A2B3C4D"}
```
Search by title:
```json
{"search_term": "Chrono Trigger"}
```
Ingest the whole library into the KG (typed nodes), one system at a time:
```
rom_ingest_platforms  params_json = "{}"
rom_ingest_roms       params_json = "{\"platform_ids\": 12, \"limit\": 500}"
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- ROM `list` is paginated by `limit`/`offset` (offset pagination), not `page`.
- `rom_ingest_*` is **best-effort**: with no reachable epistemic-graph engine it
  returns `{"ingested": null}` — that is success (no-op), not an error.
- Ingested node ids are `rom:game:<id>` / `rom:system:<id>`; re-running MERGEs
  (idempotent upsert), it does not duplicate.
- A ROM's `platform_id` drives the `:onSystem` link — ingest platforms first (or in
  the same pass) so the system node exists.

## Related
- **Conversion / on-disk organising:** `rom-manager-conversion`.
- **Game-code resolution & renaming:** `rom-manager-game-codes`.
- **Cover art / ROM-byte blobs:** stored as shared `:AssetOccurrence` via
  `rom_manager.kg_media` (internal ingestion seam, not an operational tool).
- **Ontology:** `rom_manager/ontology/rom.ttl` (`:Game`, `:GameSystem`,
  `:GameCollection`, `:onSystem`, `:inCollection`, `:hasCover`).
