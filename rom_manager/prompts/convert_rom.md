# Convert ROM — Guided Prompt

CONCEPT:ROM-001 — Externalized prompt template for the ROM conversion workflow.

You are assisting with **ROM conversion** using the ROM Manager MCP tools.

Goal: convert the ROMs in `{directory}` to the `{iso_type}` format
(`chd` via `chdman`, or `rvz` via `dolphin-tool`).

Follow this checklist:

1. **Back up first.** Conversion and the `clean_origin_files`/`--delete` option
   are destructive to the source files. Confirm the user has a backup.
2. List candidate files with the `conversion` tool, `action="list_files"`.
3. Normalize names with the `game-codes` tool (`action="rename"`) so titles
   resolve via the embedded PSX registry (CONCEPT:ROM-002).
4. Run `conversion` with `action="convert"`, passing `directory`, `iso_type`,
   and optionally `force` / `cpu_count`.
5. Report the storage delta (size before vs. after) back to the user.

If the external `chdman` or `dolphin-tool` binaries are missing, surface the
install guidance instead of failing silently.
