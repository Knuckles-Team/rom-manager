# Concept Registry — rom-manager

> **Prefix**: `CONCEPT:ROM-*`
> **Version**: 1.0.0
> **Bridge**: [`CONCEPT:AU-ECO.messaging.native-backend-abstraction`](https://github.com/Knuckles-Team/agent-utilities/blob/main/docs/concepts.md) (Unified Toolkit Ingestion)

---

## Project-Specific Concepts

| Concept ID | Name | Tag | Description |
|------------|------|-----|-------------|
| `CONCEPT:RO-OS.identity.verifies-chdman-dolphin-tool` | ROM Conversion | `conversion` | MCP tool domain `conversion` — Action-routed dynamic tool registration wrapping the `RomManager` extract/convert pipeline (CHD/RVZ). |
| `CONCEPT:RO-OS.governance.game-codes-naming-resolves` | Game Codes / Naming | `game-codes` | MCP tool domain `game-codes` — Action-routed dynamic tool registration for game-code lookup and ROM filename normalization. |
| `CONCEPT:RO-OS.state.api-base-one-mixin` | RomM Remote Library API | `romm-*` | RomM ([romm.app](https://romm.app)) remote-library integration — a full `RommApi` REST client (one mixin per resource), the `get_romm_client` factory, unified-CLI commands, and one action-routed MCP tool per resource group (`romm-roms`, `romm-platforms`, …) covering all RomM operations. |

## Cross-Project References (from agent-utilities)

| Concept ID | Name | Origin |
|------------|------|--------|
| `CONCEPT:AU-ECO.messaging.native-backend-abstraction` | Unified Toolkit Ingestion | agent-utilities |
| `CONCEPT:AU-ORCH.adapter.hot-cache-invalidation` | Confidence-Gated Router | agent-utilities |
| `CONCEPT:AU-OS.config.secrets-authentication` | Prompt Injection Defense | agent-utilities |
| `CONCEPT:AU-OS.state.cognitive-scheduler-preemption` | Cognitive Scheduler | agent-utilities |
| `CONCEPT:AU-OS.governance.reactive-multi-axis-budget` | Guardrail Engine | agent-utilities |
| `CONCEPT:AU-OS.governance.wasm-micro-agent-sandbox` | Audit Logging | agent-utilities |
| `CONCEPT:AU-KG.query.object-graph-mapper` | Knowledge Graph Core | agent-utilities |

## Synergy with agent-utilities

This project integrates with `agent-utilities` via `CONCEPT:AU-ECO.messaging.native-backend-abstraction` (Unified
Toolkit Ingestion). The `rom_manager` MCP server registers its tools with the
agent-utilities FastMCP middleware, enabling automatic discovery, telemetry, and
Knowledge Graph ingestion of all ROM-* concepts.
