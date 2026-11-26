---
name: rom-manager-operations
skill_type: skill
description: >-
  Operate rom-manager through its governed MCP and Arbora capabilities, including rom manager conversion, rom manager game codes, rom manager library sync. Use when a request requires this provider's read, change, automation, ingestion, troubleshooting, or evidence workflows.
---

# Rom Manager Operations

Use the provider's governed MCP tools through Arbora delegation.

## Steps

1. Establish the verified session and tenant, and list the tool surface with the `find` operation of the Arbora MCP server.
   Verify the rom-manager tools are listed before choosing one.
2. Open the workflow catalog at `references/catalog.md` only if the request needs a provider-specific procedure.
   Verify the procedure matches the tool names just discovered.
3. Run a read-only tool first, for example `romm_heartbeat` (no parameters) or `rom_manager_list_files` (`directory`).
   Verify it returns data without an auth error.
4. For any change, present the impact to the operator and preview it by calling the Arbora tool without `execute=true`.
   Verify the preview names the exact files or records affected.
5. Execute the approved change and read the result back with the matching read tool such as `rom_manager_list_files` (`directory`).
   Verify the observed state matches the stated impact.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Tool not found | Stale tool name or schema | Re-run discovery with `find` and use the exact name returned |
| HTTP 401 or 403 from a RomM tool | `ROMM_URL` with `ROMM_USERNAME` and `ROMM_PASSWORD` (or `ROMM_TOKEN`) missing, wrong, or the account lacks the role | Set valid RomM credentials for the `rom-manager` server and call `romm_heartbeat` (no parameters) to confirm; ask the operator for an account with the needed role |
| Preview unavailable | The tool has no preview mode | Report that to the operator and require explicit approval before executing; read back the affected records after |

## Workflow

1. Establish the verified GraphSession and tenant before discovery or retrieval.
2. Discover the current condensed tool surface; never assume a stale tool name or schema.
3. Prefer read-only inspection first. For changes, present impact and use the provider's
   dry-run or preview mode when available.
4. Execute mutations as fenced WorkItems so retries remain idempotent and auditable.
5. Ingest source data only through the signed connector preset and ChangeEnvelope path.
6. Verify the durable result and its trace/evidence before reporting completion.

## Safety contract

- Never persist credentials, endpoints, raw personal identifiers, hostnames, or local paths.
- Resolve TLS trust and verification from environment/configuration; never hardcode bypasses.
- Treat unknown ACL, tenant, schema, or tool-contract state as a hard failure.
- Require explicit approval for destructive, externally visible, or irreversible actions.
- Keep runtime traces policy-scoped and privacy-sanitized.

## Specialized workflows

Read [the workflow catalog](references/catalog.md) only when the request needs a
provider-specific procedure, parameter map, script, or reference asset.
