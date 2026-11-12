---
name: rom-manager-library-catalog
skill_type: skill
description: >-
  Browse and maintain platforms, collections, firmware and ROMs, including their files and
  metadata. Do NOT use for tasks outside the rom-manager connector.
license: MIT
tags: [rom-manager, mcp]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---

# RomM library

Use the typed tools of the `rom-manager` connector: one tool per upstream API operation, named `<operation>`. Each tool takes typed parameters; there is no `action` or `params_json` routing.

## Where the data lives

- **rom-games** (`ROMM_HOST`): holds Game; read with `romm_list_roms`.
- **rom-platforms** (`ROMM_HOST`): holds GameSystem; read with `romm_list_platforms`.
- **rom-collections** (`ROMM_HOST`): holds GameCollection; read with `romm_list_collections`.
- **rom-saves** (`ROMM_HOST`): holds GameSave; read with `romm_list_saves`.
- **rom-states** (`ROMM_HOST`): holds GameState; read with `romm_list_states`.
- **rom-firmware** (`ROMM_HOST`): holds Firmware; read with `romm_list_firmware`.

## Workflows (tool-use contracts)

Each workflow is a tool-use contract in the connector ontology. Run the steps in order; read before you write.

### `rom-manager-manage-collection`

1. `romm_get_collection` (`id`) - Run romm get collection.
2. `romm_get_collection_identifiers` (no parameters) - Run romm get collection identifiers.
3. `romm_get_smart_collection` (`id`) - Run romm get smart collection.
4. `romm_get_smart_collection_identifiers` (no parameters) - Run romm get smart collection identifiers.
5. `romm_get_virtual_collection` (`id`) - Run romm get virtual collection.
6. `romm_get_virtual_collection_identifiers` (no parameters) - Run romm get virtual collection identifiers.
7. `romm_list_collections` (`updated_after`) - Run romm list collections.
8. `romm_list_smart_collections` (`updated_after`) - Run romm list smart collections.
9. `romm_list_virtual_collections` (`limit`, `type`) - Run romm list virtual collections.
10. `romm_add_collection` (`data`, `is_favorite`, `is_public`) - Run romm add collection.
11. `romm_add_smart_collection` (`data`, `is_public`) - Run romm add smart collection.
12. `romm_update_collection` (`data`, `id`, `is_public`, `remove_cover`) - Run romm update collection.
13. `romm_update_smart_collection` (`data`, `id`, `is_public`) - Run romm update smart collection.
14. `romm_delete_collection` (`confirm`, `id`) - Run romm delete collection. (destructive: ask the operator first)
15. `romm_delete_smart_collection` (`confirm`, `id`) - Run romm delete smart collection. (destructive: ask the operator first)

### `rom-manager-manage-firmware`

1. `romm_get_firmware` (`id`) - Run romm get firmware.
2. `romm_get_firmware_content` (`dest`, `file_name`, `id`) - Run romm get firmware content.
3. `romm_get_firmware_identifiers` (no parameters) - Run romm get firmware identifiers.
4. `romm_head_firmware_content` (`file_name`, `id`) - Run romm head firmware content.
5. `romm_list_firmware` (`platform_id`) - Run romm list firmware.
6. `romm_add_firmware` (`file_path`, `platform_id`) - Run romm add firmware.
7. `romm_delete_firmware` (`confirm`, `delete_from_fs`, `firmware`) - Run romm delete firmware. (destructive: ask the operator first)

### `rom-manager-manage-platform`

1. `romm_get_platform` (`id`) - Run romm get platform.
2. `romm_get_platform_identifiers` (no parameters) - Run romm get platform identifiers.
3. `romm_get_supported_platforms` (no parameters) - Run romm get supported platforms.
4. `romm_list_platforms` (`updated_after`) - Run romm list platforms.
5. `romm_add_platform` (`body`, `params_json`) - Run romm add platform.
6. `romm_add_platform_binding` (`body`, `params_json`) - Run romm add platform binding.
7. `romm_add_platform_version` (`body`, `params_json`) - Run romm add platform version.
8. `romm_create_setup_platforms` (`platforms`) - Run romm create setup platforms.
9. `romm_update_platform` (`id`, `params_json`) - Run romm update platform.
10. `romm_delete_platform` (`confirm`, `id`) - Run romm delete platform. (destructive: ask the operator first)
11. `romm_delete_platform_binding` (`confirm`, `fs_slug`) - Run romm delete platform binding. (destructive: ask the operator first)
12. `romm_delete_platform_version` (`confirm`, `fs_slug`) - Run romm delete platform version. (destructive: ask the operator first)

### `rom-manager-manage-rom`

1. `romm_download_roms` (`dest`, `filename`, `rom_ids`) - Run romm download roms.
2. `romm_get_rom` (`id`) - Run romm get rom.
3. `romm_get_rom_by_hash` (`crc_hash`, `md5_hash`, `ra_hash`, `sha1_hash`) - Run romm get rom by hash.
4. `romm_get_rom_by_metadata_provider` (`flashpoint_id`, `hasheous_id`, `igdb_id`, `launchbox_id`, `moby_id`, `params_json`, `ra_id`, `ss_id`, `tgdb_id`) - Run romm get rom by metadata provider.
5. `romm_get_rom_content` (`dest`, `file_ids`, `file_name`, `id`) - Run romm get rom content.
6. `romm_get_rom_filters` (no parameters) - Run romm get rom filters.
7. `romm_get_rom_identifiers` (no parameters) - Run romm get rom identifiers.
8. `romm_get_romfile` (`id`) - Run romm get romfile.
9. `romm_get_romfile_content` (`dest`, `file_name`, `id`) - Run romm get romfile content.
10. `romm_head_rom_content` (`file_ids`, `file_name`, `id`) - Run romm head rom content.
11. `romm_list_roms` (`collection_id`, `favorite`, `limit`, `offset`, `order_by`, `order_dir`, `params_json`, `platform_ids`, `search_term`) - Run romm list roms.
12. `romm_search_cover` (`search_term`) - Run romm search cover.
13. `romm_search_roms` (`rom_id`, `search_by`, `search_term`) - Run romm search roms.
14. `romm_add_rom` (`file_path`, `filename`, `platform`) - Run romm add rom.
15. `romm_add_rom_manuals` (`file_path`, `filename`, `id`) - Run romm add rom manuals.
16. `romm_update_rom` (`data`, `id`, `remove_cover`, `unmatch_metadata`) - Run romm update rom.
17. `romm_update_rom_user` (`id`, `params_json`) - Run romm update rom user.
18. `romm_delete_rom_manuals` (`confirm`, `id`) - Run romm delete rom manuals. (destructive: ask the operator first)
19. `romm_delete_roms` (`confirm`, `delete_from_fs`, `roms`) - Run romm delete roms. (destructive: ask the operator first)

## Guardrails

- Read before you write: every change starts from the read steps of its contract.
- Never print or log RomM credentials, tokens or invite links.
- Identify games by RomM id or file hash and confirm the record exists before changing or deleting it.
- Report a tool refusal or HTTP error as it is; never retry past a refusal or invent a result.
