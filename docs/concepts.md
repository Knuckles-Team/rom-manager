# Concept Registry — rom-manager

> **Prefix**: `CONCEPT:ROM-*`
> **Version**: 1.0.0
> **Bridge**: [`CONCEPT:ECO-4.0`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Tag | Description |
|------------|------|-----|-------------|
| `CONCEPT:ROM-001` | ROM Conversion | `conversion` | MCP tool domain `conversion` — Action-routed dynamic tool registration wrapping the `RomManager` extract/convert pipeline (CHD/RVZ). |
| `CONCEPT:ROM-002` | Game Codes / Naming | `game-codes` | MCP tool domain `game-codes` — Action-routed dynamic tool registration for game-code lookup and ROM filename normalization. |

## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:ECO-4.0` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:ORCH-1.2` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:OS-5.1` | Prompt Injection Defense | agent-utilities |
| `CONCEPT:OS-5.2` | Cognitive Scheduler | agent-utilities |
| `CONCEPT:OS-5.3` | Guardrail Engine | agent-utilities |
| `CONCEPT:OS-5.4` | Audit Logging | agent-utilities |
| `CONCEPT:KG-2.0` | Knowledge Graph Core | agent-utilities |

## Synergy with agent-utilities

This project integrates with `agent-utilities` via `CONCEPT:ECO-4.0` (Unified
Toolkit Ingestion). The `rom_manager` MCP server registers its tools with the
agent-utilities FastMCP middleware, enabling automatic discovery, telemetry, and
Knowledge Graph ingestion of all ROM-* concepts.
