---
name: rom-manager-player-assets
skill_type: skill
description: >-
  Manage saves, emulator states, screenshots, notes, devices, netplay rooms and
  achievements. Do NOT use for tasks outside the rom-manager connector.
license: MIT
tags: [rom-manager, mcp]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---

# Player assets

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

### `rom-manager-manage-save`

1. `romm_download_save` (`dest`, `device_id`, `id`, `optimistic`) - Run romm download save.
2. `romm_get_save` (`device_id`, `id`) - Run romm get save.
3. `romm_get_save_identifiers` (no parameters) - Run romm get save identifiers.
4. `romm_get_saves_summary` (`rom_id`) - Run romm get saves summary.
5. `romm_list_saves` (`device_id`, `platform_id`, `rom_id`, `slot`) - Run romm list saves.
6. `romm_add_save` (`autocleanup`, `autocleanup_limit`, `device_id`, `emulator`, `file_path`, `overwrite`, `rom_id`, `slot`) - Run romm add save.
7. `romm_confirm_save_download` (`id`, `params_json`) - Run romm confirm save download.
8. `romm_track_save` (`id`, `params_json`) - Run romm track save.
9. `romm_untrack_save` (`id`, `params_json`) - Run romm untrack save.
10. `romm_update_save` (`id`, `params_json`) - Run romm update save.
11. `romm_delete_saves` (`confirm`, `saves`) - Run romm delete saves. (destructive: ask the operator first)

### `rom-manager-manage-screenshot`

1. `romm_add_screenshot` (`file_path`, `rom_id`) - Run romm add screenshot.

### `rom-manager-manage-state`

1. `romm_get_state` (`id`) - Run romm get state.
2. `romm_get_state_identifiers` (no parameters) - Run romm get state identifiers.
3. `romm_list_states` (`platform_id`, `rom_id`) - Run romm list states.
4. `romm_add_state` (`emulator`, `file_path`, `rom_id`) - Run romm add state.
5. `romm_update_state` (`id`, `params_json`) - Run romm update state.
6. `romm_delete_states` (`confirm`, `states`) - Run romm delete states. (destructive: ask the operator first)

### `rom-manager-manage-note`

1. `romm_get_rom_note_identifiers` (`id`) - Run romm get rom note identifiers.
2. `romm_list_rom_notes` (`id`, `public_only`, `search`, `tags`) - Run romm list rom notes.
3. `romm_create_rom_note` (`id`, `params_json`) - Run romm create rom note.
4. `romm_update_rom_note` (`id`, `note_id`, `params_json`) - Run romm update rom note.
5. `romm_delete_rom_note` (`confirm`, `id`, `note_id`) - Run romm delete rom note. (destructive: ask the operator first)

### `rom-manager-manage-device`

1. `romm_get_device` (`device_id`) - Run romm get device.
2. `romm_list_devices` (no parameters) - Run romm list devices.
3. `romm_list_netplay_rooms` (`game_id`) - Run romm list netplay rooms.
4. `romm_register_device` (`body`, `params_json`) - Run romm register device.
5. `romm_update_device` (`device_id`, `params_json`) - Run romm update device.
6. `romm_delete_device` (`confirm`, `device_id`) - Run romm delete device. (destructive: ask the operator first)

### `rom-manager-manage-achievement`

1. `romm_refresh_retro_achievements` (`id`, `params_json`) - Run romm refresh retro achievements.

## Guardrails

- Read before you write: every change starts from the read steps of its contract.
- Never print or log RomM credentials, tokens or invite links.
- Identify games by RomM id or file hash and confirm the record exists before changing or deleting it.
- Report a tool refusal or HTTP error as it is; never retry past a refusal or invent a result.
