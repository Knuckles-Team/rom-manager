---
name: rom-manager-catalog-feeds
skill_type: skill
description: >-
  Export RomM catalogs as console store feeds and gamelists. Do NOT use for tasks outside
  the rom-manager connector.
license: MIT
tags: [rom-manager, mcp]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---

# Catalog feeds and exports

Use the typed tools of the `rom-manager` connector: one tool per upstream API operation, named `<operation>`. Each tool takes typed parameters; there is no `action` or `params_json` routing.

## Steps

1. List platforms with `romm_list_platforms` (no parameters) to pick the feed target.
   Verify the platform slug exists.
2. Fetch the matching feed such as `romm_tinfoil_feed` (`slug`) or `romm_webrcade_feed` (no parameters).
   Verify the response is non-empty and well-formed.
3. For a gamelist call `romm_export_gamelist` (`platform_ids`, `local_export`).
   Verify the export covers the requested platforms.
4. Spot-check one entry against `romm_get_rom` (`id`).
   Verify its title and platform match the feed.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| HTTP 401 or 403 from a RomM tool | `ROMM_URL` with `ROMM_USERNAME` and `ROMM_PASSWORD` (or `ROMM_TOKEN`) missing, wrong, or the account lacks the role | Set valid RomM credentials for the `rom-manager` server and call `romm_heartbeat` (no parameters) to confirm; ask the operator for an account with the needed role |
| Empty feed | Platform has no ROMs or the slug is wrong | Check `romm_list_platforms` for the exact slug and `romm_list_roms` (`platform_ids`) for content |
| Local export not written | `local_export` was set where the server cannot write | Call `romm_export_gamelist` with `local_export` false and take the returned content |

## Where the data lives

- **rom-games** (`ROMM_HOST`): holds Game; read with `romm_list_roms`.
- **rom-platforms** (`ROMM_HOST`): holds GameSystem; read with `romm_list_platforms`.
- **rom-collections** (`ROMM_HOST`): holds GameCollection; read with `romm_list_collections`.
- **rom-saves** (`ROMM_HOST`): holds GameSave; read with `romm_list_saves`.
- **rom-states** (`ROMM_HOST`): holds GameState; read with `romm_list_states`.
- **rom-firmware** (`ROMM_HOST`): holds Firmware; read with `romm_list_firmware`.

## Workflows (tool-use contracts)

Each workflow is a tool-use contract in the connector ontology. Run the steps in order; read before you write.

### `rom-manager-inspect-feed`

1. `romm_export_gamelist` (`local_export`, `platform_ids`) - Run romm export gamelist.
2. `romm_fpkgi_feed` (`platform_slug`) - Run romm fpkgi feed.
3. `romm_kekatsu_feed` (`platform_slug`) - Run romm kekatsu feed.
4. `romm_pkgi_ps3_feed` (`content_type`) - Run romm pkgi ps3 feed.
5. `romm_pkgi_psp_feed` (`content_type`) - Run romm pkgi psp feed.
6. `romm_pkgi_psvita_feed` (`content_type`) - Run romm pkgi psvita feed.
7. `romm_pkgj_psp_dlc_feed` (no parameters) - Run romm pkgj psp dlc feed.
8. `romm_pkgj_psp_games_feed` (no parameters) - Run romm pkgj psp games feed.
9. `romm_pkgj_psvita_dlc_feed` (no parameters) - Run romm pkgj psvita dlc feed.
10. `romm_pkgj_psvita_games_feed` (no parameters) - Run romm pkgj psvita games feed.
11. `romm_pkgj_psx_games_feed` (no parameters) - Run romm pkgj psx games feed.
12. `romm_tinfoil_feed` (`slug`) - Run romm tinfoil feed.
13. `romm_webrcade_feed` (no parameters) - Run romm webrcade feed.

## Guardrails

- Read before you write: every change starts from the read steps of its contract.
- Never print or log RomM credentials, tokens or invite links.
- Identify games by RomM id or file hash and confirm the record exists before changing or deleting it.
- Report a tool refusal or HTTP error as it is; never retry past a refusal or invent a result.
