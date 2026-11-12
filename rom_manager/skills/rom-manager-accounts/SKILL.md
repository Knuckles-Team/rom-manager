---
name: rom-manager-accounts
skill_type: skill
description: >-
  Manage RomM accounts, invites, passwords and tokens. Do NOT use for tasks outside the
  rom-manager connector.
license: MIT
tags: [rom-manager, mcp]
metadata:
  author: Knuckles-Team
  version: '1.0.0'
---

# RomM accounts and sign-in

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

### `rom-manager-manage-account`

1. `romm_get_current_user` (no parameters) - Run romm get current user.
2. `romm_get_user` (`id`) - Run romm get user.
3. `romm_get_user_identifiers` (no parameters) - Run romm get user identifiers.
4. `romm_list_users` (no parameters) - Run romm list users.
5. `romm_add_user` (`body`, `params_json`) - Run romm add user.
6. `romm_create_invite_link` (`role`) - Run romm create invite link.
7. `romm_register_user_from_invite` (`body`, `params_json`) - Run romm register user from invite.
8. `romm_update_user` (`data`, `id`) - Run romm update user.
9. `romm_delete_user` (`confirm`, `id`) - Run romm delete user. (destructive: ask the operator first)

### `rom-manager-manage-auth`

1. `romm_create_token` (`password`, `scopes`, `username`) - Run romm create token.
2. `romm_forgot_password` (`body`, `params_json`) - Run romm forgot password.
3. `romm_login` (`body`, `params_json`) - Run romm login.
4. `romm_login_via_openid` (no parameters) - Run romm login via openid.
5. `romm_logout` (no parameters) - Run romm logout.
6. `romm_oauth_openid` (no parameters) - Run romm oauth openid.
7. `romm_reset_password` (`body`, `params_json`) - Run romm reset password. (destructive: ask the operator first)

## Guardrails

- Read before you write: every change starts from the read steps of its contract.
- Never print or log RomM credentials, tokens or invite links.
- Identify games by RomM id or file hash and confirm the record exists before changing or deleting it.
- Report a tool refusal or HTTP error as it is; never retry past a refusal or invent a result.
