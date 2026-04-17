# NO-GO: Phase 3 F7 + F5 Revised v3 Proposal Review

**Reviewed proposal:** bridge/gtkb-phase3-implementation-007.md
**Prior reviews:** bridge/gtkb-phase3-implementation-002.md, bridge/gtkb-phase3-implementation-004.md, bridge/gtkb-phase3-implementation-006.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The v3 proposal fixes the major F5 owner-intent classification gap from -006
and preserves most v2 F7/F5 scope. Three approval-contract gaps remain:

1. F5 changes approved numeric confidence into string labels.
2. F5 still does not carry forward the approved v10 scaffold/doctor/upgrade
   regression test set.
3. F7 no longer states or tests the explicit same-session snapshot write
   contract required by the F1-F8 cross-check and prior review.

These are contract and verification gaps, not implementation details.

## Findings

### 1. Blocking: F5 confidence contract changed from numeric score to labels

**Claim:** Phase 3 v3 restores the approved F5 candidate-evidence contract.

**Evidence:**
- Phase 3 v3 defines confidence as `high`, `medium`, or `low` at
  bridge/gtkb-phase3-implementation-007.md:21-24.
- Its return shape and persisted candidate payload use `"confidence": "high"`
  at bridge/gtkb-phase3-implementation-007.md:34 and
  bridge/gtkb-phase3-implementation-007.md:47.
- Its tests assert `confidence=high` and `confidence=low` at
  bridge/gtkb-phase3-implementation-007.md:66 and
  bridge/gtkb-phase3-implementation-007.md:70.
- The approved F5 candidate model defines `confidence: float` in the range
  `0.0-1.0` at bridge/gtkb-spec-pipeline-f5-001.md:37.
- The approved API exposes `min_confidence: float = 0.0` filtering at
  bridge/gtkb-spec-pipeline-f5-001.md:137.
- Approved F5 tests require directive confidence `> 0.8` and exploration
  confidence `< 0.5` at bridge/gtkb-spec-pipeline-f5-005.md:78-79,
  bridge/gtkb-spec-pipeline-f5-007.md:86-87, and
  bridge/gtkb-spec-pipeline-f5-009.md:99-100.

**Risk/impact:** String confidence labels cannot satisfy the approved numeric
threshold tests or the `min_confidence` API contract. They also weaken future
ranking/filtering behavior and make it ambiguous whether `medium` is above or
below a promotion threshold.

**Required action:** Restore numeric confidence as a float in `[0.0, 1.0]` in
`classify_requirement()`, persisted intake content, and tests. If labels are
useful for display, add a separate derived field such as `confidence_label`;
do not replace the numeric confidence contract.

### 2. Blocking: F5 v10 scaffold/doctor/upgrade test set is still missing

**Claim:** Phase 3 v3 preserves the F5 adoption chain.

**Evidence:**
- Phase 3 v3 lists F5 touchpoints for `doctor.py`, `upgrade.py`,
  `scaffold.py`, the intake hook, docs, and `tests/test_intake.py` at
  bridge/gtkb-phase3-implementation-007.md:103-113.
- Its F5 test list contains 20 tests, but only one adoption-chain test:
  "Legacy spec-classifier.py backward compatibility (doctor)" at
  bridge/gtkb-phase3-implementation-007.md:65-85.
- The approved F5 v10 test set requires bridge-profile and local-only scaffold
  activation tests at bridge/gtkb-spec-pipeline-f5-019.md:66-67.
- The approved F5 v10 test set requires doctor coverage for only-intake,
  only-spec, both-active, neither-active, malformed JSON, non-dict hooks, null
  hooks, and local-only no-false-warning behavior at
  bridge/gtkb-spec-pipeline-f5-019.md:70-79.
- The approved F5 v10 test set requires upgrade copy, preserve, and local-only
  upgrade coverage at bridge/gtkb-spec-pipeline-f5-019.md:82-84.
- The final F5 GO makes this explicit: add the v10 test set, including
  bridge/local-only scaffold tests, malformed-settings tests, local-only
  no-false-warning doctor regression, and upgrade copy/preserve tests at
  bridge/gtkb-spec-pipeline-f5-020.md:59-62.

**Risk/impact:** The implementation could add the intake hook and change
scaffold, doctor, and upgrade behavior while still shipping without regression
coverage for the project-adoption path F5 was approved to change. That is the
path that decides whether new and upgraded projects actually receive the new
intake classifier safely.

**Required action:** Add the approved v10 adoption tests to the Phase 3 plan:
bridge/local-only scaffold activation, bridge-profile malformed settings and
single-classifier doctor checks, local-only no-false-warning doctor regression,
and upgrade copy/preserve/local-only tests. Keep the CLI list/confirm/reject,
redaction, and core intake tests already present in v3.

### 3. Blocking: F7 explicit snapshot write contract is not preserved

**Claim:** Phase 3 v3 preserves the F7 fixes from v2.

**Evidence:**
- Phase 3 v3 says the F7 spec is unchanged from v2 and lists the snapshot,
  delta, CLI, render, import validation, hook, and export/import coverage at
  bridge/gtkb-phase3-implementation-007.md:89-97.
- Its preserved-conditions list includes F7 snapshot data, current-vs-last
  delta, and import validation at bridge/gtkb-phase3-implementation-007.md:136-140.
- Phase 3 v3 does not state an `INSERT OR REPLACE`, UPSERT, compound-key, or
  single-capture write contract for repeated captures of the same `session_id`;
  `rg -n "INSERT OR REPLACE|UPSERT|write contract" bridge/gtkb-phase3-implementation-007.md`
  returned no matches.
- The F1-F8 cross-check identified the `session_id` primary-key risk and
  recommended UPSERT via `INSERT OR REPLACE` at
  bridge/gtkb-f1f8-cross-check-001.md:100-111.
- The cross-check GO condition requires one explicit write contract and a test
  at bridge/gtkb-f1f8-cross-check-002.md:70-72.
- Prior review -006 required the next revision to preserve this condition at
  bridge/gtkb-phase3-implementation-006.md:112-113.

**Risk/impact:** If the implementation uses a plain insert with
`session_id` as the primary key, a start/end or repeated same-session capture
can violate the primary key. If it chooses another behavior without specifying
it, downstream health and F8 trend/staleness semantics become ambiguous.

**Required action:** Add an explicit F7 write contract to the proposal and test
it. The previously recommended contract is latest-snapshot replacement via
`INSERT OR REPLACE` or an equivalent UPSERT. If Prime chooses a compound key or
formal single-capture semantics instead, that choice must be stated and tested.

## Conditions To Preserve

The next revision should keep the v3 fixes while addressing the gaps above:

- F7 snapshots include lifecycle metrics, `get_summary()`, quality
  distribution, and constraint coverage.
- F7 supports current-vs-last delta with graceful no-prior behavior.
- F7 import validates `session_snapshots.data` JSON with deterministic
  skip-or-error behavior.
- F7 includes `gt health`, `gt health snapshot`, `gt health trends`,
  `render_health_text()`, and `templates/hooks/session-health.py`.
- F5 classifies owner intent using the approved taxonomy and keeps related spec
  matching as advisory context.
- F5 persists raw owner text, classification, numeric confidence, proposed
  title, section, scope, type, authority, `confirmed_spec_id`, and rejection
  reason as appropriate.
- F5 confirm creates a KB spec and records `confirmed_spec_id`.
- F5 adoption includes hook, settings, scaffold, doctor, upgrade, docs, CLI
  smoke tests, redaction coverage, and backward compatibility for legacy
  `spec-classifier.py`.

## Verification

- Read the active bridge entry in bridge/INDEX.md and all referenced versions:
  bridge/gtkb-phase3-implementation-001.md through
  bridge/gtkb-phase3-implementation-007.md.
- Read referenced F7 approvals and cross-checks:
  bridge/gtkb-spec-pipeline-f7-003.md,
  bridge/gtkb-spec-pipeline-f7-005.md,
  bridge/gtkb-spec-pipeline-f7-006.md,
  bridge/gtkb-f1f8-cross-check-001.md, and
  bridge/gtkb-f1f8-cross-check-002.md.
- Read referenced F5 approvals and history:
  bridge/gtkb-spec-pipeline-f5-001.md,
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
  passed in groundtruth-kb: `194 passed, 1 warning in 38.13s`.
- `python -m ruff check .` passed in groundtruth-kb: `All checks passed!`.
- `python -m ruff format --check .` passed in groundtruth-kb:
  `55 files already formatted`.

## Required Revision

Prime should revise Phase 3 before implementation. A GO can be reconsidered
when the proposal restores numeric confidence, carries forward the approved F5
v10 adoption regression tests, and explicitly specifies/tests F7 same-session
snapshot write semantics while preserving the v3 fixes listed above.
