# CONN-ROM-MANAGER-COMPETENCY-OPERATIONS — Reference-set verification

Owner: rom-manager. Cross-repo IDs: MEDULLA-MEDIA-VOCAB-R024.

## Purpose and user stories

Medulla answers a connector competency question over this connector's virtual graph. The question needs the operation below, which the connector does not serve today. Until it lands, Medulla answers with a typed abstention that names this operation.

## Why a new spec

No local spec owns connector operations that competency questions need. This spec owns them. It moved here from Medulla (MEDULLA-MEDIA-VOCAB-R024), where the rows described this connector's behaviour.

## Delivery mapping

Component: rom-manager connector

Code: ../../rom_manager/__init__.py

## User Scenarios & Testing

### User Story 1 - The connector must serve a `romm_roms` verify action that returns a checksum verdict for each ROM against its reference set (Priority: P1)

The fleet operator and the engine rely on this behaviour of `rom-manager`: The connector must serve a `romm_roms` verify action that returns a checksum verdict for each ROM against its reference set. It is proven independently of the other stories.

**Acceptance Scenarios**:

1. **Given** the `rom-manager` connector built from the default branch, **When** `tests/test_romm_verify.py::test_verify_returns_a_verdict_per_rom` runs, **Then** the operation returns the documented fields.

### Edge Cases

- The vendor service is unreachable or rejects the credential: the connector returns the SDK typed error and never a partial result.
- An argument outside the documented inputs is refused with the SDK typed refusal and causes no effect on the vendor service.

## Requirements

- **FR-001**: The connector must serve a `romm_roms` verify action that returns a checksum verdict for each ROM against its reference set. Rows: `CONN-ROM-MANAGER-COMPETENCY-OPERATIONS-R001`.

## Success Criteria

- **SC-001**: The operation returns the documented fields. Rows: `CONN-ROM-MANAGER-COMPETENCY-OPERATIONS-R001`.

## Assumptions

- The `rom-manager` package keeps the entry point and module layout named in the rows.
- The shared SDK supplies the transport, authentication, retry and certification helpers the rows reuse.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-ROM-MANAGER-COMPETENCY-OPERATIONS-R001` | plan.md Production caller chain | T-001 | tests/test_romm_verify.py::test_verify_returns_a_verdict_per_rom |
