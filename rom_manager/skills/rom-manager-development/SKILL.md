---
name: rom-manager-development
skill_type: skill
domain: development
description: >-
  Develop, test, gate, and release the rom-manager connector. Use this skill
  when changing ROM conversion, RomM mappings, MCP tools, packaging,
  documentation, or repository gates.
license: MIT
tags: [rom-manager, development, connector, test, gates]
tier: repository
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---

# rom-manager development

This repository owns local ROM conversion, RomM library calls, their MCP tools,
packaged connector content, and the rom-manager agent entry points. Shared
connector contracts and transports belong to `scion-sdk`; admission,
serving, and durable graph state belong to their owning repositories. Read
`AGENTS.md` before changing code and keep provider credentials, ROM paths, and
endpoints out of source, logs, and skill content.

## Steps

1. Find the owning spec row with `git grep -n "<term>" -- specs`.
   Verify an existing row is extended before adding new requirement text.
2. Make the smallest change in the existing `RomManager` code or tool surface.
   Verify with `git diff --stat` that only intended files changed.
3. Run focused tests with `uv run --all-extras pytest tests/test_mcp_registration.py -q`.
   Verify the run ends with all tests passed.
4. Run the repository gate with `uvx pre-commit run --all-files`.
   Verify every hook reports Passed.
5. Stage reviewed paths with `git add -- <path>` and inspect `git diff --cached --name-status`.
   Verify only intended files are staged before committing with the `Spec:` trailer.

## Failure recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| Pre-commit hook fails | Formatting, spelling or spec gate violation | Read the hook output, fix the named file, and re-stage that path |
| Tests need missing binaries | A test calls `chdman` or a live RomM instead of the runner seams | Mock through the existing runner seams so the test passes without those binaries |
| No spec row found | Requirement not yet declared | Extend the nearest spec under `specs/` first |

## Rapid delivery: the 5-minute contract

Specs are already designed. Deliver small, reviewable slices and cite the
owning spec row in the commit trailer.

- Find the owning row first with `git grep -n "<term>" -- specs` and extend
  that spec before adding new requirement text.
- Reuse the existing `RomManager`, RomM API facade, SDK transport policies, and
  tool surface. Do not create a second implementation of a connector capability.
- Keep changes scoped to this connector. A change owned by the SDK, Arbora, or
  the knowledge graph belongs in that repository instead.
- Every delivered requirement needs a bound test. Generated `status.json`
  files are produced by `pipelines-hook spec-status`; never hand-edit them.
- Keep conversion tests independent of `chdman`, `dolphin-tool`, and live RomM
  services by using the existing runner seams and mocks.
- One logical change per commit, with `Spec: <ID>` and the assisting agent
  trailer adjacent in the final paragraph.

## Setup and gates

Use the pinned environment from `uv sync --locked`. Run the repository gate:

```bash
uvx pre-commit run --all-files
```

For focused feedback, run the smallest affected test file with the locked
environment, for example:

```bash
uv run --all-extras pytest tests/test_mcp_registration.py -q
uv run --all-extras pytest tests/test_romm_coverage.py -q
```

The canonical `.pre-commit-config.yaml` delegates connector-standard, secrets,
spec, tests-fast, and dependency-readiness checks to `Knuckles-Team/pipelines`
at `rev: main`. Do not replace those shared hooks with local copies or bypass a
failing check.

## Connector-specific checks

- Keep conversion, RomM, and MCP tool surfaces aligned with the SDK.
- Mock external RomM calls and validate configuration before provider requests;
  never use live credentials in a local gate.
- Keep `rom_manager/skills/`, ontology, prompts, and connector manifests in
  package data when adding content.
- Documentation lives under `docs/` and is published by the shared Pages
  workflow; source status records live under `specs/`.

## Delivery discipline

Work in a real Git worktree based on `origin/main`. Inspect the complete diff,
stage only reviewed paths, and verify `git status --short` after every gate.
Do not use `git stash`, `git add -A`, or `git add .`; do not claim Pages
publication until a successful exact-source workflow run and the public page
are both observed.
