NEW

# Implementation Proposal - GTKB-EVALUATION-MODULE-RESTORATION-001: Retire Evaluation-Module Waiver

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Test/runtime restoration proposal
**Risk tier:** Medium (performance baseline tests and deleted module history; no deployment)
**Backlog item:** `GTKB-EVALUATION-MODULE-RESTORATION-001`

---

## Background

Slice 8.6 Phase 3-G waived two performance tests because they import
`evaluation.pilots.quality_pilot`, but the `evaluation/` module was deleted at
S320 commit `c9fc7216` during isolation cleanup. The waiver expires when the
module is restored or the tests are rewritten.

This proposal files the normal bridge packet for retiring that waiver.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md` with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites
  required specs and waiver evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must map
  restored or rewritten tests to the cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 38 of
  `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the waiver retirement must be
  explicit and evidence-backed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - restored code must not recreate
  stale mixed-platform/application structure.
- `DELIB-S330-SLICE-8-6-PHASE-3-G-EVALUATION-MODULE-WAIVER` - owner-approved
  temporary skip for the two affected performance tests.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "evaluation module restoration evaluation.pilots.quality_pilot deleted tests performance waiver" --limit 8
```

The search did not return a strong pre-existing restoration decision. The live
authority is the Slice 8.6 waiver and row 38 in `memory/work_list.md`.

## Proposed Scope

Preferred implementation: rewrite the two performance tests to avoid restoring
the deleted `evaluation/` module unless inspection proves the deleted module is
still the right product surface.

Steps:

1. Inspect the deleted `evaluation/` module from the parent of commit
   `c9fc7216` using non-destructive git history commands.
2. Decide between two paths in the implementation report:
   - Path A: restore only the minimal needed evaluation code and dataset.
   - Path B: rewrite `tests/performance/test_concurrent_tenants.py` to inline
     or mock the golden-dataset/pilot behavior without restoring deleted
     infrastructure.
3. Remove the two skip markers once the replacement path is implemented.
4. Preserve or update `tests/evaluation/test_quality_pilot.py` coherently,
   because it also imports `evaluation.pilots.quality_pilot`.

## Acceptance Criteria

- The two skipped performance tests no longer skip for the evaluation-module
  waiver.
- `tests/evaluation/test_quality_pilot.py` is either restored to passing or
  explicitly dispositioned in the same report.
- No broad stale infrastructure is restored without justification.
- The waiver record is retired or narrowed with evidence.
- Tests pass locally for the affected performance/evaluation surfaces.

## Test Plan

Suggested commands:

```powershell
python -m pytest tests/performance/test_concurrent_tenants.py tests/evaluation/test_quality_pilot.py -q --tb=short
python -m ruff check tests/performance/test_concurrent_tenants.py tests/evaluation/test_quality_pilot.py
python -m ruff format --check tests/performance/test_concurrent_tenants.py tests/evaluation/test_quality_pilot.py
```

If source code is restored, add the restored package path to the ruff commands.

## Out Of Scope

- Reverting the whole S320 isolation cleanup.
- Restoring unrelated deleted modules.
- Changing live production behavior.

## Prime Builder Recommendation

Proceed after Loyal Opposition `GO`, preferring Path B unless git-history
inspection shows the deleted module is still minimal, current, and appropriate.

