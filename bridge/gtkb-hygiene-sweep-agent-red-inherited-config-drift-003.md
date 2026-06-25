NEW
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 2026-06-25T01-37-14Z-prime-builder-B-a06721
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: Claude Code, prime-builder, dispatch

# GT-KB Bridge Implementation Report - gtkb-hygiene-sweep-agent-red-inherited-config-drift - 003

bridge_kind: implementation_report
Document: gtkb-hygiene-sweep-agent-red-inherited-config-drift
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-002.md
Approved proposal: bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3419

## Implementation Claim

WI-3419 is complete. The `[tool.coverage.run]` `source` field in `pyproject.toml` was
corrected from `["applications/Agent_Red/src"]` (Agent Red application source) to
`["groundtruth-kb/src", "scripts"]` (GT-KB platform source). The `omit` entries were
updated in lockstep. A regression assertion was added to
`platform_tests/scripts/test_fab12_agent_red_residue_sweep.py` as function
`test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant`, which verifies:
- `coverage.run.source` equals `["groundtruth-kb/src", "scripts"]`
- No `applications/Agent_Red` path appears in `source`
- No `applications/Agent_Red` path appears in `omit`
- All declared source and omit roots exist on disk

Both changes are committed. Coverage measurement now reports against the GT-KB
platform source tree, not the Agent Red application source tree.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this change proceeds through the bridge protocol (NEW → GO → implement → report → VERIFIED); the bridge VERIFIED is the authoritative terminal signal authorizing the relink and the regression-assertion addition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the fix preserves the durable artifact graph by keeping the platform coverage-configuration artifact (`pyproject.toml`) consistent with the GT-KB platform source tree and the FAB-12 regression artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report carries forward every governing specification cited in the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives tests from the linked specs and provides exact executed commands with observed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this report carries the required Project Authorization / Project / Work Item linkage lines.
- `SPEC-AUQ-POLICY-ENGINE-001` — not bearing on this change: no AskUserQuestion policy surface is added, removed, or altered.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the core defect: platform tooling must honor the GT-KB root / `applications/` boundary and must not silently resolve platform coverage measurement to Agent Red application source.
- `GOV-STANDING-BACKLOG-001` — WI-3419 is a standing-backlog item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — not bearing on this change: no hook surface, hook registration, or harness-parity artifact is touched.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the coverage-config state stays artifact-backed and traceable: the relink is recorded in `pyproject.toml` and locked by an extended FAB-12 regression assertion.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the fix aligns the config artifact's "verified/relinked" lifecycle state with the regression evidence that should gate it.

## Owner Decisions / Input

No new owner decision is required. Implementation is authorized under:
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` (active project authorization)
- `DELIB-20265457` (owner decision authorizing the reliability-fixes proposal batch)

## Prior Deliberations

- `bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-001.md` — approved implementation proposal (NEW).
- `bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-002.md` — Loyal Opposition GO verdict authorizing implementation, applicability preflight `sha256:8bf0c03bd9efeb3b956506c4946c38939a595fee45a06a6e5afad2a40e4c2592`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -m pytest platform_tests/scripts/test_fab12_agent_red_residue_sweep.py::test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant -v --tb=short` → **1 passed in 0.15s**. Assertion confirms `coverage.run.source == ["groundtruth-kb/src", "scripts"]` and no `applications/Agent_Red` path in source or omit. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Same test verifies on-disk existence of all declared source/omit roots, confirming artifact consistency. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The regression assertion locks the corrected lifecycle state; any drift from the Agent Red value will fail the test. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Coverage config is now artifact-backed in `pyproject.toml` with a locked regression test. |
| `GOV-STANDING-BACKLOG-001` | WI-3419 implementation complete; covered by both commits (see below). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Spec-derived test `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` executed and passed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight re-run on this report (see below). |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project Authorization, Project, Work Item metadata present in this report header. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation proceeds through the governed bridge protocol: proposal (NEW-001) → GO (002) → report (NEW-003) → VERIFIED. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Not applicable: no AUQ policy surface changed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Not applicable: no hook surface changed. |

## Commands Run

```
# Targeted regression test for WI-3419
python -m pytest platform_tests/scripts/test_fab12_agent_red_residue_sweep.py::test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant -v --tb=short

# Ruff lint gate
python -m ruff check pyproject.toml platform_tests/scripts/test_fab12_agent_red_residue_sweep.py

# Ruff format gate
python -m ruff format --check pyproject.toml platform_tests/scripts/test_fab12_agent_red_residue_sweep.py
```

## Observed Results

```
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3
rootdir: E:\GT-KB
configfile: pyproject.toml
collected 1 item

platform_tests/scripts/test_fab12_agent_red_residue_sweep.py::test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant PASSED [100%]

============================== 1 passed in 0.15s ==============================

ruff check: All checks passed!
ruff format --check: 1 file already formatted
```

## Files Changed

The implementation spans two commits. Only the target-path changes for WI-3419 are listed:

**Commit `f8936dc1e`** — `chore(config): dispatcher OpenRouter max_items=2, pyproject coverage scope, WI-4742 GO`
- `pyproject.toml` — corrected `[tool.coverage.run]` `source` from `["applications/Agent_Red/src"]` to `["groundtruth-kb/src", "scripts"]`; updated `omit` entries accordingly.

**Commit `7cd8aa86a`** — `test(platform): update platform test suite for mode-switch, dispatch, and sweep`
- `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py` — added `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` asserting platform-scoped coverage configuration (15 lines added).

## Recommended Commit Type

- Recommended commit type: `fix:` / `test:` (two commits already present in history)
- Diff-stat justification: `pyproject.toml` corrects a misconfigured coverage scope (bug fix); `test_fab12_agent_red_residue_sweep.py` adds a regression assertion (test addition). Both changes are already committed in the branch history.

## Acceptance Criteria Status

- [x] `[tool.coverage.run] source` is `["groundtruth-kb/src", "scripts"]` — no `applications/Agent_Red` references.
- [x] `[tool.coverage.run] omit` entries reference only platform paths.
- [x] Regression assertion `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` passes.
- [x] All declared source/omit roots exist on disk (verified by assertion).
- [x] Ruff lint and format clean on target files.

## Risk And Rollback

Residual risk: minimal. The change corrects measurement scope from a wrong path to the right path; it does not alter any production logic or hook behavior. Coverage percentages may shift when measured against the correct source tree, but the test gate (`fail_under = 75`) already covers that scenario.

Rollback: revert the `pyproject.toml` hunk to restore `["applications/Agent_Red/src"]` and drop the regression assertion from `test_fab12_agent_red_residue_sweep.py`. Both are in existing commits; `git revert` of the relevant hunks would restore prior state. Bridge audit files remain append-only.

## Applicability Preflight

- packet_hash: `sha256:d69e71e3caddca591147992543d430355fb51bbb85ac6f8937d11805d5e03717`
- bridge_document_name: `gtkb-hygiene-sweep-agent-red-inherited-config-drift`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-impl-reports/drafts/gtkb-hygiene-sweep-agent-red-inherited-config-drift-003.md`
- operative_file: `bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-hygiene-sweep-agent-red-inherited-config-drift`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Loyal Opposition Asks

1. Verify `pyproject.toml` `[tool.coverage.run]` contains `source = ["groundtruth-kb/src", "scripts"]` with no Agent Red paths.
2. Verify `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` exists and passes.
3. Return VERIFIED if the implementation satisfies the approved proposal and all spec links are covered; return NO-GO with findings otherwise.
