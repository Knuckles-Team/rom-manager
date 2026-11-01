# CONN-ROM-MANAGER-COMPETENCY-OPERATIONS — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-ROM-MANAGER-COMPETENCY-OPERATIONS-R001` | The connector must serve a `romm_roms` verify action that returns a checksum verdict for each ROM against its reference set. Caller chain: arbora `fleet.call` reaches the `romm_roms` tool of `rom_manager/mcp_server.py`, whose new `verify` action compares each ROM checksum with its reference set. Shape: a `verify` action in the `romm_roms` tool of `rom_manager/mcp_server.py` returning a checksum verdict per ROM; reuses the checksum helpers of `rom_manager/`. Proving test (planned): `tests/test_romm_verify.py::test_verify_returns_a_verdict_per_rom`. | The operation returns the documented fields. |
