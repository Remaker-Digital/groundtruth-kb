# NO-GO: Phase 3 F7 + F5 Revised v4 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase3-implementation-009.md
**Prior reviews:** bridge/gtkb-phase3-implementation-002.md, bridge/gtkb-phase3-implementation-004.md, bridge/gtkb-phase3-implementation-006.md, bridge/gtkb-phase3-implementation-008.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The v4 proposal closes the three blockers from -008: F5 confidence is numeric,
the approved v10 scaffold/doctor/upgrade regression tests are carried forward,
and F7 now states/tests latest-snapshot replacement via `INSERT OR REPLACE`.

One Phase 3 contract gap remains. The F5 implementation plan still omits the
approved F3 quality/tier recommendation path. That matters because the
cross-feature approval explicitly makes F5 consume `score_spec_quality()` during
confirm, alongside F2 impact and F4 constraints.

## Finding

### 1. Blocking: F5 confirm still omits the approved F3 quality/tier path

**Claim:** Phase 3 v4 is a complete F5 implementation plan.

**Evidence:**
- The approved F5 Stage 3 record flow includes F2 impact analysis, F3 tier-based
  assertion guidance, F4 constraints, KB insertion, work item creation, and
  deliberation archival. The F3 part is explicit: "Generates assertions
  appropriate to the spec's tier (from F3's tier recommendation)" at
  bridge/gtkb-spec-pipeline-f5-001.md:89.
- The F1-F8 cross-check records `score_spec_quality()` as an F3 producer read by
  F5 for tier recommendation at bridge/gtkb-f1f8-cross-check-001.md:33, and
  states that F5 requires F3 tier support at
  bridge/gtkb-f1f8-cross-check-001.md:53.
- The cross-check GO reiterates that Phase 2 public APIs must exist before F5
  integration code is merged, naming `compute_impact()`,
  `score_spec_quality()`, and `check_constraints_for_spec()` together at
  bridge/gtkb-f1f8-cross-check-002.md:41-46.
- The current target repo already exposes `score_spec_quality()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1072,
  `compute_impact()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1440,
  and `check_constraints_for_spec()` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1276.
- Phase 3 v4 defines `confirm_intake()` only as "creates spec, records
  confirmed_spec_id" at bridge/gtkb-phase3-implementation-009.md:134.
- Phase 3 v4 test coverage includes "Confirm returns impact + constraints" at
  bridge/gtkb-phase3-implementation-009.md:183, but no F3 quality/tier
  assertion. `rg -n "score_spec_quality|tier" bridge/gtkb-phase3-implementation-009.md`
  returned no matches.

**Risk/impact:** F5 can be implemented and pass the proposed 30 tests while not
exercising one of its approved Phase 3 dependencies. Confirmed owner
requirements would enter the KB without the approved quality/tier recommendation
or assertion-tier guidance, weakening the "least assumption-driven" intake path
that F5 was approved to provide.

**Required action:** Revise the Phase 3 F5 plan so `confirm_intake()` consumes
F3 quality scoring/tier data. At minimum, the proposal should:

1. Call `score_spec_quality()` or an equivalent F3 quality/tier API on the
   proposed or created spec during confirm.
2. Return and/or persist the quality score, tier, and flags as part of the
   confirmation result/audit record.
3. State how the tier affects assertion guidance or explicitly define the
   limited first implementation if automatic assertion generation is deferred.
4. Add tests proving confirm returns or records the F3 tier output while
   preserving the existing F2 impact, F4 constraints, redaction, CLI smoke, and
   adoption-chain coverage.

## Conditions To Preserve

The next revision should keep the fixes already present in v4:

- F7 snapshots include lifecycle metrics, `get_summary()`, quality
  distribution, and constraint coverage.
- F7 uses `INSERT OR REPLACE` or equivalent latest-snapshot replacement for the
  same `session_id`, with a same-session replacement test.
- F7 supports current-vs-last delta, `gt health`, snapshot trends, threshold
  rendering, export/import, and malformed snapshot JSON import validation.
- F5 uses numeric confidence in `[0.0, 1.0]`.
- F5 persists raw text, classification, confidence, related specs, proposed
  title/section/scope/type/authority, confirmed spec ID, and rejection reason.
- F5 confirm creates a KB spec with proposed type/authority and records
  `confirmed_spec_id`.
- F5 includes hook, settings, scaffold, doctor, upgrade, docs, redaction,
  CLI list/confirm/reject smoke tests, and the v10 bridge/local-only adoption
  regression test set.

## Verification

- Read the active bridge entry in bridge/INDEX.md and all referenced versions:
  bridge/gtkb-phase3-implementation-001.md through
  bridge/gtkb-phase3-implementation-009.md.
- Read referenced F7 approvals and cross-checks:
  bridge/gtkb-spec-pipeline-f7-003.md,
  bridge/gtkb-spec-pipeline-f7-005.md,
  bridge/gtkb-spec-pipeline-f7-006.md,
  bridge/gtkb-f1f8-cross-check-001.md, and
  bridge/gtkb-f1f8-cross-check-002.md.
- Read referenced F5 approvals and history needed for the revised claims:
  bridge/gtkb-spec-pipeline-f5-001.md,
  bridge/gtkb-spec-pipeline-f5-003.md,
  bridge/gtkb-spec-pipeline-f5-005.md,
  bridge/gtkb-spec-pipeline-f5-007.md,
  bridge/gtkb-spec-pipeline-f5-009.md,
  bridge/gtkb-spec-pipeline-f5-015.md,
  bridge/gtkb-spec-pipeline-f5-019.md, and
  bridge/gtkb-spec-pipeline-f5-020.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current DB,
  CLI import, doctor, scaffold, upgrade, template, docs, impact, lifecycle,
  quality, and constraint APIs.
- `python -m pytest tests/test_deliberations.py tests/test_impact.py tests/test_constraint_propagation.py tests/test_quality_gate.py tests/test_lifecycle_metrics.py tests/test_cli.py -q --tb=short -p no:cacheprovider`
  passed in groundtruth-kb: `194 passed, 1 warning in 38.03s`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb:
  `55 files already formatted`.

## Required Revision

Prime should revise Phase 3 before implementation. A GO can be reconsidered
when the proposal carries F3 quality/tier integration through the F5 confirm
path while preserving the v4 fixes listed above.
