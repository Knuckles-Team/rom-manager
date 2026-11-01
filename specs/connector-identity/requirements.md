# CONN-ROM-MANAGER-CONNECTOR-IDENTITY — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-ROM-MANAGER-CONNECTOR-IDENTITY-R001` | **Fleet name.** `pyproject.toml` declares `rom-manager-mcp` as the single `scion_sdk.connector` entry point. The content pack, the manifest `connector`, the fingerprints and the ingest binding all carry `rom-manager-mcp`. Caller chain: `rom-manager` in `pyproject.toml` runs `rom_manager.rom_manager:rom_manager`, which builds the server from the `scion_sdk.connector` entry point `rom_manager:connector` (`rom_manager/__init__.py:47`); `connector_name("rom_manager")` in the SDK resolves the same entry point name for the content pack, the manifest and the ingest binding. Shape: `pyproject.toml` entry point `rom-manager-mcp`, the `connector_name` helper of the SDK and the `ConnectorContent`/`IngestBinding` calls under `rom_manager/`; reuses the SDK name resolution and adds no second constant. Proving test: `tests/test_fleet_name.py::test_connector_name_is_the_fleet_name`. | Every connector name in the package is `rom-manager-mcp`. |
