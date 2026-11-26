---
name: rom-manager-code-registry
skill_type: skill
description: >-
  Look up game codes in the PlayStation code registry. Do NOT use for tasks outside the
  rom-manager connector.
license: MIT
tags: [rom-manager, mcp]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---

# Game codes

Use the typed tools of the `rom-manager` connector: one tool per upstream API operation, named `<operation>`. Each tool takes typed parameters; there is no `action` or `params_json` routing.

## Steps

1. Take the serial from the file name or request and normalize its case.
   Verify it matches a pattern like `SLUS-00594`.
2. Look it up with `rom_manager_lookup_game_code` (`code`).
   Verify the result is a title or an explicit miss.
3. To browse a region, call `rom_manager_list_game_codes` (`prefix`) with `SLUS`, `SLES` or `SLPS`.
   Verify the returned codes start with the prefix.
4. Report the title with the region the prefix implies, taken from the `rom_manager_lookup_game_code` result.
   Verify the same title is not claimed for a different region.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Lookup misses | Code absent from the local registry | Call `rom_manager_list_game_codes` (`prefix`) to check nearby codes, and report an unknown title instead of guessing |
| Wrong region title | Same game has a different serial per region | Look up the exact serial from the file name and do not reuse another region's code |

## Where the data lives

- **rom-games** (`ROMM_HOST`): holds Game; read with `romm_list_roms`.
- **rom-platforms** (`ROMM_HOST`): holds GameSystem; read with `romm_list_platforms`.
- **rom-collections** (`ROMM_HOST`): holds GameCollection; read with `romm_list_collections`.
- **rom-saves** (`ROMM_HOST`): holds GameSave; read with `romm_list_saves`.
- **rom-states** (`ROMM_HOST`): holds GameState; read with `romm_list_states`.
- **rom-firmware** (`ROMM_HOST`): holds Firmware; read with `romm_list_firmware`.

## Workflows (tool-use contracts)

Each workflow is a tool-use contract in the connector ontology. Run the steps in order; read before you write.

### `rom-manager-inspect-game-code`

1. `rom_manager_list_game_codes` (`prefix`) - Run rom manager list game codes.
2. `rom_manager_lookup_game_code` (`code`) - Run rom manager lookup game code.

## Guardrails

- Read before you write: every change starts from the read steps of its contract.
- Never print or log RomM credentials, tokens or invite links.
- Identify games by RomM id or file hash and confirm the record exists before changing or deleting it.
- Report a tool refusal or HTTP error as it is; never retry past a refusal or invent a result.
