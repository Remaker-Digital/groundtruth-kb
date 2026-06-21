NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Hygiene sweep: enumerate and remediate Agent-Red-inherited config drift across GT-KB repo (S363 Phase 2 class observation)

bridge_kind: prime_proposal
Document: gtkb-hygiene-sweep-agent-red-inherited-config-drift
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3419

target_paths: ["pyproject.toml", "platform_tests/scripts/test_fab12_agent_red_residue_sweep.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The root `pyproject.toml` `[tool.coverage.run]` section is an Agent-Red-inherited config-drift artifact: `source = ["applications/Agent_Red/src"]` (with matching Agent-Red-only `omit` entries) scopes coverage measurement exclusively to Agent Red application source. When coverage is computed from the repo root using the project default (e.g., `pytest --cov` with no explicit `--cov=` target, or any tool that honors `[tool.coverage.run] source`), the GT-KB platform code under `groundtruth-kb/src` and `scripts/` is silently excluded, so platform coverage reads as empty/misleading. This is the unremediated tail of the WI-3419 S363 Phase 2 class: the named candidates (root `sonar-project.properties`, `.github/workflows/sonarcloud.yml`) were already relinked to GT-KB scope and are regression-asserted by `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py::test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant`, but that same test does NOT assert anything about `[tool.coverage.run]`, leaving the coverage-source drift live and untested.

## Requirement Sufficiency

Existing requirements sufficient. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` already establishes that platform tooling must not silently resolve to Agent Red application surfaces, and the existing `test_fab12_agent_red_residue_sweep.py` regression already codifies "root pyproject and CI paths are platform-scoped" for testpaths, pythonpath, ignores, and the sonar surfaces. This fix extends the existing, already-governed regression contract to the one remaining unasserted field (`[tool.coverage.run] source`) and corrects the drift. No new or revised requirement/specification is introduced; the change is a bounded config relink plus a regression assertion that closes the gap in the existing FAB-12 surface.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `pyproject.toml`, `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py`. The change touches only the GT-KB platform `pyproject.toml` coverage block and a platform regression test; no file under `applications/` is modified, and the `[tool.coverage]` content patterns flagged by `config/governance/hygiene-sweep-patterns.toml` `agent-red-config-drift` are removed from the platform-root file (not from any application surface).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this change proceeds through the bridge protocol (NEW -> GO -> implement -> report -> VERIFIED); the bridge `VERIFIED` is the authoritative terminal signal authorizing the relink and the regression-assertion addition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable artifact graph by keeping the platform coverage-configuration artifact (`pyproject.toml`) consistent with the GT-KB platform source tree and the FAB-12 regression artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification, including the blocking applicability-flagged set (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each test from the cited specs and provides exact execution commands (mandatory spec-derived testing).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the required Project Authorization / Project / Work Item linkage lines (mandatory project linkage).
- `SPEC-AUQ-POLICY-ENGINE-001` - not bearing on this change: this WI is owner-authorized through the cited PAUTH/DELIB and introduces no AUQ-policy surface; no AskUserQuestion policy behavior is added, removed, or altered.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - governing authority for the defect: platform tooling and config must honor the GT-KB root / `applications/` boundary and must not silently resolve platform measurement to Agent Red application source; the current coverage-source value violates that intent at the coverage-measurement boundary.
- `GOV-STANDING-BACKLOG-001` - WI-3419 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES; this proposal advances that tracked item.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - not bearing on this change: no Claude/Codex hook surface, hook registration, or harness-parity artifact is touched by a coverage-config relink and a platform regression-test addition.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the coverage-config state stays artifact-backed and traceable: the relink is recorded in `pyproject.toml` and locked by an extended FAB-12 regression assertion rather than left as an implicit assumption.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fix aligns the config artifact's "verified/relinked" lifecycle state with the regression evidence that should gate it, closing the candidate->verified gap for the coverage-source field.

## Prior Deliberations

- `DELIB-20263459` - Hygiene Sweep Scope Regression - 2026-06-12: directly relevant prior decision on hygiene-sweep scope; this proposal remediates a config-drift instance inside that sweep's domain.
- `DELIB-20262900` - Slice 8.6 Phase 4 — Codex NO-GO at -006 citing that CI/coverage evidence was bound to Agent Red surfaces rather than the canonical GT-KB framework; the coverage-source drift fixed here is the same class of Agent-Red-bound platform measurement.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).
- `DELIB-1685` - Loyal Opposition Verification, GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001: prior context for keeping GT-KB platform resource references from resolving to Agent Red surfaces (the same disambiguation principle applies to coverage source).
- `DELIB-20264327` - Loyal Opposition Review, GT-KB Mass Adoption Readiness Phase A: adoption-readiness context for ensuring platform config is GT-KB-scoped and not adopter-specific.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - owner-approved non-fast-lane batch authorization for PROJECT-GTKB-RELIABILITY-FIXES work items; WI-3419 (origin=hygiene, P3) is in scope of this batch envelope, which authorizes a bounded platform config-drift remediation plus its regression test.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW implementation proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work-item batch; this proposal is one batch member and cites the batch decision as its authorization rationale.

## Proposed Scope

1. In `pyproject.toml`, relink the platform coverage configuration to GT-KB platform scope:
   - Change `[tool.coverage.run] source` from `["applications/Agent_Red/src"]` to the GT-KB platform source tree `["groundtruth-kb/src", "scripts"]` (matching the GT-KB sources already declared in root `sonar-project.properties` `sonar.sources=groundtruth-kb/src,scripts`).
   - Update the `[tool.coverage.run] omit` entries from the Agent-Red `__init__.py` globs to the corresponding GT-KB platform `__init__.py` globs (`groundtruth-kb/src/**/__init__.py`), so package `__init__` files remain excluded under the new source roots.
   - Preserve the existing `fail_under`, `branch`, and `[tool.coverage.report]` settings unchanged (no coverage-gate policy change is proposed; this is a scope relink only).
2. In `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py`, extend `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (or add a sibling test in the same module) to assert that `[tool.coverage.run] source` contains GT-KB platform roots, contains no `applications/Agent_Red/...` entry, and that each declared source/omit-root path exists in the repo (mirroring the module's existing extant-path assertion style).

Scope discipline: the broader WI-3419 "enumerate the whole class" deliverable is now substantially served by the deterministic `gt hygiene sweep` CLI (WI-3420) plus `config/governance/hygiene-sweep-patterns.toml` `agent-red-config-drift`, which already capture and surface this class; the other named candidates (`sonar-project.properties`, `sonarcloud.yml`) are already relinked and regression-locked. This proposal therefore targets the one remaining live, verifiable drift defect rather than re-running a manual census. Any additional candidates the sweep surfaces in future runs are filed as separate child WIs, consistent with the WI's "output is more backlog items" framing.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (platform tooling must not resolve to Agent Red application source) | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (extended) | `pyproject.toml` `[tool.coverage.run] source` contains GT-KB platform roots (`groundtruth-kb/src`, `scripts`) and contains no `applications/Agent_Red/...` entry. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (relinked paths must be extant, no dangling config) | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (extended) | Each non-glob path implied by `[tool.coverage.run] source` exists under the repo root (mirroring the module's existing extant-path checks). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (verification derives from cited specs) | full `test_fab12_agent_red_residue_sweep.py` module | The extended FAB-12 module passes, confirming the coverage-source relink is locked by the same regression surface that already governs the sonar/CI relinks. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (config artifact stays consistent with platform source tree) | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (extended) | The coverage `omit` globs reference GT-KB platform `__init__.py` paths, not Agent-Red ones, keeping the config artifact internally consistent. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_fab12_agent_red_residue_sweep.py -q --tb=short`
- `python -m ruff check pyproject.toml platform_tests/scripts/test_fab12_agent_red_residue_sweep.py`
- `python -m ruff format --check pyproject.toml platform_tests/scripts/test_fab12_agent_red_residue_sweep.py`

(Note: `ruff check`/`ruff format --check` apply meaningfully to the `.py` test file; `pyproject.toml` is included in the command set per the standard code-quality gate convention and is a no-op for ruff's Python lint/format surface.)

## Acceptance Criteria

1. `pyproject.toml` `[tool.coverage.run] source` is `["groundtruth-kb/src", "scripts"]` (GT-KB platform scope) with no `applications/Agent_Red/...` entry; `omit` references GT-KB platform `__init__.py` globs; `fail_under`/`branch`/`[tool.coverage.report]` are unchanged.
2. The extended assertion(s) in `test_fab12_agent_red_residue_sweep.py` fail against the pre-fix (Agent-Red-scoped) coverage config and pass against the relinked config (the assertion genuinely guards the drift).
3. `python -m pytest platform_tests/scripts/test_fab12_agent_red_residue_sweep.py -q --tb=short` passes; `ruff check` and `ruff format --check` are clean on the changed `.py` file.

## Risks / Rollback

- Risk: a tool or workflow currently relies on the Agent-Red-scoped coverage default to measure Agent Red coverage from the repo root. Mitigation: Agent Red coverage in CI is computed via explicit `--cov=applications/Agent_Red/src` flags in `.github/workflows/python-tests.yml`, not via the `pyproject.toml` default, so relinking the default to platform scope does not remove Agent Red's CI coverage measurement; the default now correctly serves GT-KB platform coverage.
- Risk: raising `fail_under` semantics could break a coverage gate. Mitigation: out of scope — `fail_under` and all `[tool.coverage.report]` settings are left untouched; only the measured-source scope changes.
- Risk: the chosen GT-KB source roots under-cover (e.g., a platform module outside `groundtruth-kb/src`/`scripts`). Mitigation: the roots match the already-owner-approved `sonar.sources` in root `sonar-project.properties`; any future addition is a separate config-tracked change.
- Rollback: revert the `[tool.coverage.run]` change in `pyproject.toml` and the regression-assertion addition in `test_fab12_agent_red_residue_sweep.py`; the change is a bounded config edit plus one test addition, fully reversible with no migration.

## Files Expected To Change

- `pyproject.toml`
- `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py`

## Recommended Commit Type

`fix`
