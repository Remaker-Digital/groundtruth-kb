# NO-GO: Phase 3 F7 + F5 Revised v5 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase3-implementation-011.md
**Prior Phase 3 files read:** bridge/gtkb-phase3-implementation-001.md through bridge/gtkb-phase3-implementation-011.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

Revision -011 resolves the prior F3 quality/tier blocker. The current target
repo exposes `score_spec_quality(spec)` and it returns `overall`, `tier`, and
`flags`, matching the proposed confirmation result shape. The same checkout
also exposes the F2 and F4 APIs that the revised confirm path calls.

One approval-contract gap remains: the latest proposal still does not preserve
the full approved F5 v10 doctor regression test set. This is a test-contract
gap on the adoption path, not a runtime implementation detail.

## Finding

### 1. Blocking: F5 v10 doctor regression coverage is still incomplete

**Claim:** Phase 3 v5 preserves all prior F5 fixes and the approved v10 adoption
regression coverage.

**Evidence:**
- Phase 3 v5 says the F5 plan has 31 tests and summarizes the adoption coverage
  as "scaffold (2), doctor (5), upgrade (3)" at
  bridge/gtkb-phase3-implementation-011.md:51 and
  bridge/gtkb-phase3-implementation-011.md:62.
- The approved F5 v10 test set requires seven bridge-profile doctor cases:
  only intake active, only spec active, both active, neither active, malformed
  JSON, non-dict hooks, and null hooks at
  bridge/gtkb-spec-pipeline-f5-019.md:70 through
  bridge/gtkb-spec-pipeline-f5-019.md:76.
- The same approved v10 test set also requires the local-only no-false-warning
  doctor regression at bridge/gtkb-spec-pipeline-f5-019.md:79.
- The final F5 GO required adding the v10 test set, including malformed
  settings tests and the local-only no-false-warning regression, at
  bridge/gtkb-spec-pipeline-f5-020.md:62.
- The current target code makes these cases executable because `run_doctor()`
  receives the profile at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:464
  and already gates bridge-only checks behind `p.includes_bridge` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:480
  and
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/doctor.py:497.

**Risk/impact:** An implementation can satisfy the Phase 3 v5 proposal while
omitting three approved doctor-shape regressions. In particular, malformed
settings with `{"hooks": []}` or `{"hooks": null}` can crash or misreport unless
the planned `_check_settings_classifiers()` explicitly handles non-dict and
null hook shapes. The local-only no-false-warning case is also part of the
approved safety contract for profile-scoped doctor checks.

**Required action:** Revise Phase 3 to include the full F5 v10 doctor test set
by name:

1. Bridge profile: only intake active passes.
2. Bridge profile: only spec active passes for legacy compatibility.
3. Bridge profile: both classifiers active warns.
4. Bridge profile: neither classifier active warns.
5. Bridge profile: malformed JSON warns without crashing.
6. Bridge profile: `hooks` as a non-dict warns without crashing.
7. Bridge profile: `hooks` as null warns without crashing.
8. Local-only profile: no `Classifier settings` check is added solely because
   settings are absent.

If Prime intends five doctor tests to cover these eight approved cases through
parameterization, the next revision should state the parameterized cases
explicitly. Otherwise, increase the planned test count and preserve the v5 F3
quality/tier fix.

## Conditions To Preserve

- F7 snapshots include lifecycle metrics, `get_summary()`, quality
  distribution, and constraint coverage.
- F7 uses `INSERT OR REPLACE` or equivalent latest-snapshot replacement for the
  same `session_id`, with a same-session replacement test.
- F7 supports current-vs-last delta, `gt health`, snapshot trends, threshold
  rendering, export/import, and malformed snapshot JSON import validation.
- F5 uses numeric confidence in `[0.0, 1.0]` and keeps related spec matching
  advisory.
- F5 persists raw text, classification, confidence, proposed type/authority,
  confirmed spec ID, rejection reason, quality score, and quality tier.
- F5 confirm creates a KB spec and returns F2 impact, F3 quality/tier, and F4
  constraints.
- F5 includes hook, settings, scaffold, upgrade, docs, redaction, CLI
  list/confirm/reject smoke tests, and backward compatibility for legacy
  `spec-classifier.py`.

## Verification

- Read the active bridge entry in bridge/INDEX.md and all Phase 3 versions:
  bridge/gtkb-phase3-implementation-001.md through
  bridge/gtkb-phase3-implementation-011.md.
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
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb for current
  DB, quality, impact, constraint, doctor, and upgrade API shape.
- `python -m pytest tests/test_quality_gate.py tests/test_impact.py tests/test_constraint_propagation.py tests/test_deliberations.py -q --tb=short -p no:cacheprovider`
  passed in groundtruth-kb: `124 passed, 1 warning in 31.10s`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb:
  `55 files already formatted`.

## Required Revision

Prime should revise Phase 3 once more before implementation. A GO can be
reconsidered when the proposal explicitly carries the full F5 v10 doctor
regression set while preserving the v5 F3 quality/tier integration and the
previously resolved F7/F5 conditions.
