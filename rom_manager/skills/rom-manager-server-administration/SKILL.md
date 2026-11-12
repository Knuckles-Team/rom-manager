---
name: rom-manager-server-administration
skill_type: skill
description: >-
  Check server health and configuration, manage exclusions and run background tasks. Do
  NOT use for tasks outside the rom-manager connector.
license: MIT
tags: [rom-manager, mcp]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---

# RomM administration

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

### `rom-manager-manage-server`

1. `romm_get_config` (no parameters) - Run romm get config.
2. `romm_get_raw_asset` (`dest`, `path`) - Run romm get raw asset.
3. `romm_get_setup_library` (no parameters) - Run romm get setup library.
4. `romm_head_raw_asset` (`path`) - Run romm head raw asset.
5. `romm_heartbeat` (no parameters) - Run romm heartbeat.
6. `romm_metadata_heartbeat` (`source`) - Run romm metadata heartbeat.
7. `romm_stats` (no parameters) - Run romm stats.
8. `romm_add_exclusion` (`body`, `params_json`) - Run romm add exclusion.
9. `romm_delete_exclusion` (`confirm`, `exclusion_type`, `exclusion_value`) - Run romm delete exclusion. (destructive: ask the operator first)

### `rom-manager-manage-task`

1. `romm_get_task` (`task_id`) - Run romm get task.
2. `romm_get_tasks_status` (no parameters) - Run romm get tasks status.
3. `romm_list_tasks` (no parameters) - Run romm list tasks.
4. `romm_run_all_tasks` (no parameters) - Run romm run all tasks.
5. `romm_run_task` (`task_name`) - Run romm run task.

## Guardrails

- Read before you write: every change starts from the read steps of its contract.
- Never print or log RomM credentials, tokens or invite links.
- Identify games by RomM id or file hash and confirm the record exists before changing or deleting it.
- Report a tool refusal or HTTP error as it is; never retry past a refusal or invent a result.
