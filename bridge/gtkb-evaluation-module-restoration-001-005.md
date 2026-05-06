NEW

# Post-Investigation REPORT - GTKB-EVALUATION-MODULE-RESTORATION-001

Reported by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: `bridge/gtkb-evaluation-module-restoration-001-003.md` REVISED-1; Loyal Opposition GO at `bridge/gtkb-evaluation-module-restoration-001-004.md`
Requested bridge disposition: `VERIFIED` for read-only investigation only

## Claim

The read-only evaluation-module investigation is complete. No source, test, MemBase, or formal-approval files were changed.

Key findings:

- Commit `c9fc7216` deleted the root `evaluation/` package during S320 isolation cleanup.
- The deleted package contains the exact modules imported by current tests: `evaluation.pilots.quality_pilot` and `evaluation.deepeval_config`.
- The waiver currently covers two skipped performance tests, but the active failure surface is wider: `tests/evaluation/test_quality_pilot.py` and `tests/evaluation/test_deepeval_scaffold.py` fail during collection because they import the deleted package at module import time.
- Minimal Path A restoration would require restoring at least six deleted files, not only `quality_pilot.py`.
- Path B test rewrite or retirement better preserves the S320 isolation cleanup intent, but it needs owner direction because `memory/work_list.md` row 38 explicitly says owner choice is required.
- The intended waiver DELIB remains an evidence gap. Current CLI search was blocked by a read-only database migration attempt; the approved proposal and Loyal Opposition review already record that exact MemBase lookup did not find the DELIB row.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report is filed in `bridge/` and registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report cites required specs and waiver evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - later implementation must map restored or rewritten tests to cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - row 38 of `memory/work_list.md` is the work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the waiver retirement path must be explicit and evidence-backed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` - restored code must not recreate stale mixed-platform/application structure.
- `.claude/rules/canonical-terminology.md` - GT-KB platform and Agent Red application concerns must stay separate.
- `memory/pending-owner-decisions.md` entries around the Slice 8.6 Phase 3-G question and answer - owner chose to skip two tests with a waiver DELIB.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-005.md` - Slice 8.6 post-implementation report recording the two waived tests and follow-on row.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-007.md` and `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-009.md` - later reports carrying the intended evaluation waiver citation.
- `bridge/gtkb-evaluation-module-restoration-001-003.md` - approved read-only investigation proposal.
- `bridge/gtkb-evaluation-module-restoration-001-004.md` - Loyal Opposition GO for read-only investigation.

## Owner Decisions / Input

Owner decision evidence:

- `memory/pending-owner-decisions.md` records the Slice 8.6 Phase 3-G question for two pre-existing Python Tests failures in `test_perf_03_*` and `test_perf_04_*`, both with `ModuleNotFoundError: No module named 'evaluation'`.
- The recorded answer is `(A) Skip both tests with waiver DELIB (recommended)`.

Waiver scope:

- Explicitly covers the two performance tests:
  - `tests/performance/test_concurrent_tenants.py::TestSingleTenantBaseline::test_perf_03_golden_dataset_loads_under_100ms`
  - `tests/performance/test_concurrent_tenants.py::TestSingleTenantBaseline::test_perf_04_quality_pilot_evaluation_under_500ms`
- Does not explicitly cover `tests/evaluation/test_quality_pilot.py` or `tests/evaluation/test_deepeval_scaffold.py`.

Expiry condition:

- The waiver should retire or narrow when either the evaluation module is restored, the tests are rewritten, or the owner approves a different disposition.

Evidence gap:

- The intended ID `DELIB-S330-SLICE-8-6-PHASE-3-G-EVALUATION-MODULE-WAIVER` is cited by bridge reports and skip reasons.
- The approved proposal and Loyal Opposition review report that exact MemBase searches did not find a current deliberation row.
- This investigation attempted `python -m groundtruth_kb deliberations search "PHASE-3-G-EVALUATION-MODULE-WAIVER" --limit 5`; it failed with `sqlite3.OperationalError: attempt to write a readonly database` while the CLI tried to run schema migration. The evidence gap is therefore unresolved and should be repaired or superseded before code implementation.

## Deleted Module Inventory

`git ls-tree -r --name-only c9fc7216^ -- evaluation tests/evaluation` showed these files before deletion:

```text
evaluation/__init__.py
evaluation/datasets/__init__.py
evaluation/datasets/response_quality.json
evaluation/deepeval_config.py
evaluation/pilots/__init__.py
evaluation/pilots/quality_pilot.py
evaluation/results/quality-raw-2026-02-23.json
evaluation/results/quality-report-2026-02-23.json
evaluation/run_quality_live.py
evaluation/seed_quality_kb.py
tests/evaluation/__init__.py
tests/evaluation/test_deepeval_scaffold.py
tests/evaluation/test_quality_pilot.py
```

`git ls-tree -r --name-only c9fc7216 -- evaluation tests/evaluation` showed only the `tests/evaluation/*` files after deletion; root `evaluation/` was removed.

`git show --stat --oneline c9fc7216 -- evaluation tests/evaluation` showed 10 deleted `evaluation/` files and 1,817 deleted lines. Relevant deleted module sizes:

| Deleted file | Role | Size observed |
|---|---|---|
| `evaluation/pilots/quality_pilot.py` | Provides `DATASET_PATH`, `ScenarioResult`, `load_dataset`, `evaluate_response`, `run_pilot` | 376 lines |
| `evaluation/datasets/response_quality.json` | Golden scenario dataset used by `load_dataset()` | 375 lines |
| `evaluation/deepeval_config.py` | Provides DeepEval availability/config/adapter/runner functions | 193 lines |
| `evaluation/__init__.py`, `evaluation/pilots/__init__.py`, `evaluation/datasets/__init__.py` | Package import surface | 17 total lines |

The deleted `evaluation/results/*`, `evaluation/run_quality_live.py`, and `evaluation/seed_quality_kb.py` are not required by the currently failing imports.

## Current Import Inventory

Current imports found by `rg`:

| Current file | Import | Status |
|---|---|---|
| `tests/performance/test_concurrent_tenants.py` | `from evaluation.pilots.quality_pilot import load_dataset` | Inside waived skipped test `test_perf_03_*` |
| `tests/performance/test_concurrent_tenants.py` | `from evaluation.pilots.quality_pilot import load_dataset, run_pilot` | Inside waived skipped test `test_perf_04_*` |
| `tests/evaluation/test_quality_pilot.py` | `from evaluation.pilots.quality_pilot import ...` | Module-level import; currently collection error |
| `tests/evaluation/test_deepeval_scaffold.py` | `from evaluation.deepeval_config import ...` | Module-level import; currently collection error |

Focused repro:

```text
python -m pytest tests/evaluation/test_quality_pilot.py tests/evaluation/test_deepeval_scaffold.py tests/performance/test_concurrent_tenants.py::TestSingleTenantBaseline::test_perf_03_golden_dataset_loads_under_100ms tests/performance/test_concurrent_tenants.py::TestSingleTenantBaseline::test_perf_04_quality_pilot_evaluation_under_500ms -q --tb=short
```

Result:

```text
ERROR tests/evaluation/test_quality_pilot.py - ModuleNotFoundError: No module named 'evaluation'
ERROR tests/evaluation/test_deepeval_scaffold.py - ModuleNotFoundError: No module named 'evaluation'
collected 2 items / 2 errors
```

The two performance tests are skipped when collection reaches them, but collection is interrupted first by the two `tests/evaluation/*` module-level import errors.

## Path Comparison

### Path A - Minimal Restore

Expected files:

- `evaluation/__init__.py`
- `evaluation/datasets/__init__.py`
- `evaluation/datasets/response_quality.json`
- `evaluation/pilots/__init__.py`
- `evaluation/pilots/quality_pilot.py`
- `evaluation/deepeval_config.py`

Benefits:

- Lowest test rewrite effort.
- Restores the original import surface for both performance and evaluation tests.
- Could allow removing the two skip markers and exercising the old performance gates.

Risks:

- Reintroduces a root `evaluation/` package deleted by S320 isolation cleanup.
- The deleted files are classified in historical reports as adopter-owned / unclassified, so restoring them into GT-KB may recreate mixed GT-KB / Agent Red application structure.
- Does not by itself answer whether evaluation belongs in GT-KB platform, Agent Red application, or a separate test fixture package.

### Path B - Rewrite Or Retire Tests

Expected files:

- Rewrite `tests/performance/test_concurrent_tenants.py` PERF-03/PERF-04 to use local fixtures or mocks instead of root `evaluation/`.
- Rewrite or retire `tests/evaluation/test_quality_pilot.py` and `tests/evaluation/test_deepeval_scaffold.py`, or move them to the appropriate Agent Red application test home.
- Remove skip markers only after the replacement behavior is covered.

Benefits:

- Preserves the S320 isolation cleanup and avoids restoring stale root infrastructure.
- Forces the owner/project to decide whether these are GT-KB platform tests or Agent Red application tests.
- Avoids making a deleted application-evaluation package a new GT-KB dependency.

Risks:

- More implementation work.
- Requires clearer acceptance criteria for what PERF-03/PERF-04 should now measure.
- May reduce historical continuity with the original CQ-1/CQ-2/CQ-4 tests unless the rewritten tests preserve the same assertions.

## Owner-Decision Packet

Decision needed before implementation:

Choose one path for `GTKB-EVALUATION-MODULE-RESTORATION-001` implementation.

Options:

1. **Path A - Minimal restore:** restore only the six files needed by current imports, then remove the two performance skip markers and run the affected tests.
2. **Path B - Rewrite/retire tests:** preserve the S320 deletion, rewrite or retire tests that still depend on root `evaluation/`, and remove/narrow the waiver only after replacement tests pass.
3. **Path C - Different disposition:** owner supplies another disposition, such as moving evaluation tests to Agent Red only.

Recommendation:

Path B is safer for GT-KB isolation because it avoids reintroducing the root `evaluation/` package deleted by the S320 cleanup. Path A is faster but risks undoing the cleanup rationale.

Separate archive repair decision:

Before any implementation requests `VERIFIED`, either repair/insert the missing `DELIB-S330-SLICE-8-6-PHASE-3-G-EVALUATION-MODULE-WAIVER` record or supersede it with a new owner-approved decision that explicitly covers the final implementation path.

## Specification-Derived Verification

| Test ID | Spec coverage | Procedure | Result |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` updated so this file is latest `NEW` | PASS |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-evaluation-module-restoration-001` | PASS - `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Report includes waiver scope, affected tests, expiry, evidence gap, and Path A/B/C decision packet | PASS |
| T-readonly-1 | Root-boundary and safety | Inspect changed paths | PASS - no source/test/MemBase/formal-approval mutations |
| T-inventory-1 | Investigation acceptance | Report lists deleted module files and current imports | PASS |

## Changed Files

- `bridge/gtkb-evaluation-module-restoration-001-005.md`
- `bridge/INDEX.md`
- `memory/work_list.md`

## Applicability Preflight

```text
packet_hash: sha256:1a8dfb62b9446f8ee9efcea2f195214720cf5c0fa9e17be433674e65b86dd295
bridge_document_name: gtkb-evaluation-module-restoration-001
operative_file: bridge/gtkb-evaluation-module-restoration-001-005.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```
