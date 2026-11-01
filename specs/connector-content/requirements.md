# CONN-ROM-MANAGER-CONNECTOR-CONTENT — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-ROM-MANAGER-CONNECTOR-CONTENT-R001` | **Default content.** `pyproject.toml` declares `rom-manager-mcp` as the single `scion_sdk.connector` entry point. The server lists the packaged `skill://` and `ontology://` resources and the packaged prompts with no `content=` argument. Caller chain: `rom-manager` in `pyproject.toml` runs `rom_manager.rom_manager:rom_manager`, which builds the server from the `scion_sdk.connector` entry point `rom_manager:connector` (`rom_manager/__init__.py:47`); the SDK `Connector` then lists the packaged skills, ontology and prompts. Shape: `pyproject.toml` entry point `rom-manager-mcp` plus the `connector = Connector(.)` object in `rom_manager/__init__.py`; the packaged `skills/`, `ontology/` and `prompts/` directories of `rom_manager` are reused as is, with no connector-local registration code. Proving test: `tests/test_default_content_surfaces.py::test_default_content_surfaces`. | `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. |
