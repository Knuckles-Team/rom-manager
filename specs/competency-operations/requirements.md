# CONN-ROM-MANAGER-COMPETENCY-OPERATIONS — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-ROM-MANAGER-COMPETENCY-OPERATIONS-R001` | The connector must serve a `romm_roms` verify action that returns a checksum verdict for each ROM against its reference set. Proving test: `tests/test_romm_verify.py`. | The operation returns the documented fields. |
