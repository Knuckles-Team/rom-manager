---
name: rom-manager-conversion-pipeline
skill_type: skill
description: >-
  Convert, rename and inspect local ROM files: disc images to CHD, cue sheets and file
  listings. Do NOT use for tasks outside the rom-manager connector.
license: MIT
tags: [rom-manager, mcp]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---

# ROM conversion

Use the typed tools of the `rom-manager` connector: one tool per upstream API operation, named `<operation>`. Each tool takes typed parameters; there is no `action` or `params_json` routing.

## Steps

1. List candidates with `rom_manager_list_files` (`directory`, `extensions`).
   Verify only the intended images are listed.
2. Choose `iso_type` for the platform and convert one file first with `rom_manager_process_file` (`file`, `iso_type`) after operator approval.
   Verify the output file exists and report the size delta.
3. For a whole directory call `rom_manager_process_directory` (`directory`, `iso_type`, `cpu_count`) keeping `clean_origin_files` false unless asked.
   Verify every source has a converted target.
4. Generate cue sheets for multi-track sets with `rom_manager_generate_cue` (`directory`).
   Verify the `.cue` file lists every `.bin` track.
5. Rename by serial with `rom_manager_rename_by_game_code` (`file`) after approval.
   Verify the new name with `rom_manager_list_files`.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Conversion tool fails | `chdman` or `dolphin-tool` missing from `PATH` | Install the missing binary and confirm with `chdman --help` or `dolphin-tool --help` before converting |
| Destructive tool refused | No operator approval, or `clean_origin_files` set unintentionally | Ask the operator, and keep `clean_origin_files` false unless the user asked to reclaim space |
| Nothing listed | Wrong `directory` or `extensions` | Pass an absolute `directory` and widen `extensions` in `rom_manager_list_files` |

## Where the data lives

- **rom-games** (`ROMM_HOST`): holds Game; read with `romm_list_roms`.
- **rom-platforms** (`ROMM_HOST`): holds GameSystem; read with `romm_list_platforms`.
- **rom-collections** (`ROMM_HOST`): holds GameCollection; read with `romm_list_collections`.
- **rom-saves** (`ROMM_HOST`): holds GameSave; read with `romm_list_saves`.
- **rom-states** (`ROMM_HOST`): holds GameState; read with `romm_list_states`.
- **rom-firmware** (`ROMM_HOST`): holds Firmware; read with `romm_list_firmware`.

## Workflows (tool-use contracts)

Each workflow is a tool-use contract in the connector ontology. Run the steps in order; read before you write.

### `rom-manager-manage-pipeline`

1. `rom_manager_convert` (`clean_origin_files`, `cpu_count`, `directory`, `force`, `iso_type`, `verbose`) - Run rom manager convert. (destructive: ask the operator first)
2. `rom_manager_process_directory` (`clean_origin_files`, `cpu_count`, `directory`, `force`, `iso_type`, `verbose`) - Run rom manager process directory. (destructive: ask the operator first)
3. `rom_manager_process_file` (`file`, `force`, `iso_type`, `verbose`) - Run rom manager process file. (destructive: ask the operator first)

### `rom-manager-manage-files`

1. `rom_manager_list_files` (`directory`, `extensions`) - Run rom manager list files.
2. `rom_manager_generate_cue` (`directory`) - Run rom manager generate cue.
3. `rom_manager_rename_by_game_code` (`file`) - Run rom manager rename by game code. (destructive: ask the operator first)

## Guardrails

- Read before you write: every change starts from the read steps of its contract.
- Never print or log RomM credentials, tokens or invite links.
- Identify games by RomM id or file hash and confirm the record exists before changing or deleting it.
- Report a tool refusal or HTTP error as it is; never retry past a refusal or invent a result.
