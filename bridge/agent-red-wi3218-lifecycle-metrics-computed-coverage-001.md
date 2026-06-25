NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e30eeba-5f51-4cad-89fd-793ac8f59e98
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: Claude Code interactive; role=prime-builder; output_style=explanatory
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge proposal

# Implementation Proposal - WI-3218 Pipeline Lifecycle Metrics Computed & Aggregation Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3218-lifecycle-metrics-computed-coverage
Version: 001 (NEW)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3218

target_paths: ["platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py"]

## Claim

WI-3218 should add explicit deterministic coverage for the live `SPEC-2100`
"Pipeline lifecycle metrics: computed metrics and aggregation" contract and route
that evidence through the bridge for Loyal Opposition verification.

`SPEC-2100` is implemented GT-KB platform infrastructure (the `compute_m*`
metric methods and the `get_lifecycle_metrics()` aggregator in
`groundtruth-kb/src/groundtruth_kb/db.py`), not an Agent Red application feature.
The owner authorization snapshot nevertheless includes `WI-3218`, and the WI is
still open/backlogged in `PROJECT-AGENT-RED-TEST-COVERAGE-GAPS`. The WI was
classified γ' (phantom-only evidence) by the 16.B methodology review
(`DELIB-0712`): MemBase maps `SPEC-2100` only to `TEST-11219` ("Spec-derived test
for SPEC-2100"), a placeholder with no `test_file` path and no `assertion_runs`.

As with the sibling WI-3217 item, live state is richer than the historical
"phantom-only" framing, and this proposal scopes around that honestly. A real
suite already exists on disk at `groundtruth-kb/tests/test_lifecycle_metrics.py`
and comprehensively covers each implemented Phase-1 metric (M2, M4, M6, M10, M11,
M12, M16, M17, M18) with per-metric edge cases, zero-denominator handling, and
the structured-metadata contract. That suite is not bridged/mapped to `WI-3218`,
and it does **not** deterministically assert three `SPEC-2100` clauses that sit
above the individual metric computations:

1. **Phase-1 scope boundary** — `SPEC-2100` enumerates 20 metrics (M1-M20) but
   only 9 are implemented ("Phase 1"). No test asserts the implemented-vs-deferred
   manifest, so silent drift in either direction is undetected.
2. **Trend analysis over time windows** — `SPEC-2100` requires "All metrics
   computable over time windows (last N sessions, days, all time)." The aggregator
   accepts `last_n_days` and threads it to M6; `compute_m17` accepts `now`. The
   existing suite never exercises the windowed/trend path through the aggregator.
3. **On-demand aggregation ("No pre-aggregation")** — `SPEC-2100` requires
   computation on demand from `pipeline_events` + existing KB tables with no
   pre-aggregation. No test proves a metric reflects a live mutation made after a
   prior computation (i.e., that results are not cached/pre-aggregated).

This proposal is a bounded `test_addition` item. It adds one focused platform
test module that closes those three aggregation/scope clauses **without
duplicating** the existing per-metric coverage (it references the existing suite
for that surface). It expects no production source mutation;
`groundtruth-kb/src/groundtruth_kb/db.py` remains the read-only implementation
surface under test.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-2100` (status `implemented`, P1) specifies the metric set, the aggregation
contract ("AGGREGATION: On demand from pipeline_events + existing KB tables. No
pre-aggregation."), and the trend-analysis requirement ("All metrics computable
over time windows"). That is enough detail for deterministic coverage of the
aggregation/scope clauses.

The current WI is a test-coverage gap, not a new feature request. No owner
clarification is required because the proposal only adds tests over the
already-implemented, in-root platform behavior and does not add new work items,
formal artifacts, release state, deployment state, credentials, or Agent Red
application behavior.

Observed implemented-vs-intended boundary (documented, not in scope to change):
only 9 of the 20 spec-listed metrics are implemented in Phase 1 (M2, M4, M6, M10,
M11, M12, M16, M17, M18). The deferred 11 (M1, M3, M5, M7, M8, M9, M13, M14, M15,
M19, M20) are out of scope for this test-coverage backfill; the new test asserts
the current Phase-1 manifest and documents the deferred set rather than treating
their absence as a defect.

## In-Root Placement Evidence

The implementation target is under the GT-KB root:

- `E:\GT-KB\platform_tests\scripts\test_lifecycle_metrics_spec2100_coverage.py`

Read-only verification may inspect these in-root implementation and historical
evidence paths:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py` (compute_m2/m4/m6/m10/m11/m12/m16/m17/m18
  at lines 7726-7972; `get_lifecycle_metrics` at line 7974)
- `E:\GT-KB\groundtruth-kb\tests\test_lifecycle_metrics.py` (existing per-metric suite)

## Specification Links

- `SPEC-2100` - Direct requirement: computed lifecycle metrics, the Phase-1
  metric set, time-window/trend computability, and on-demand aggregation with no
  pre-aggregation.
- `SPEC-2099` - Upstream data-model dependency: the metric computations aggregate
  over the `pipeline_events` table; M10 joins it directly.
- `GOV-08` - Canonical Knowledge Database / MemBase behavior; metrics are
  computed on demand from canonical KB tables.
- `GOV-10` - Test artifacts must exercise live project interfaces; this proposal
  adds executable tests over the production `KnowledgeDB` metric interface instead
  of phantom-only evidence.
- `SPEC-1649` - Master test plan / live-interface policy; the new test file
  provides deterministic repository-native coverage.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance; the new test file creates
  visible executable evidence for the WI.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - The "no pre-aggregation / on-demand"
  clause is a source-of-truth freshness property; the test proves metrics reflect
  live mutations rather than cached/pre-aggregated values.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner
  authorization is required but does not replace bridge review, `GO`, target
  paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies changed-file hygiene; Python
  coverage uses targeted pytest plus ruff check and ruff format checks on the
  touched test file.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing
  AUQ-backed project authorization; this proposal requests no new owner decision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority,
  role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this
  proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation
  verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project
  authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms all files are under
  `E:\GT-KB`; this proposal does not depend on out-of-root archives.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal
  uses the existing authorized WI and does not add project scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence
  for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and
  review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as
  a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project
authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`,
citing owner decision `DELIB-20265586` (2026-06-23), and remains inside
snapshot-bound project member `WI-3218`. The authorization's allowed mutation
classes include `test_addition`, which is the only mutation class this proposal
exercises.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red
  test-coverage-gap project; the standing authority for this WI's implementation.
- `DELIB-0712` - POR Step 16.B methodology review classifying `SPEC-2100` as γ'
  (phantom-only evidence) and scheduling it for live-interface remediation per
  GOV-10. This proposal is the remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected
  assertion-only verification for behavioral requirements; this proposal supplies
  executable test evidence.
- `DELIB-0018` - Project Progress Dashboard KPI Proposal; the conceptual origin of
  pipeline lifecycle metrics. It motivates the metric set but predates the
  implementation and provides no executable coverage for this WI.
- `gt bridge threads --wi WI-3218 --json` returned `match_count: 0` before this
  proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt projects show PROJECT-AGENT-RED-TEST-COVERAGE-GAPS --json` shows `WI-3218`
  open/backlogged among 7 remaining members; the PAUTH `included_work_item_ids`
  snapshot includes `WI-3218`.
- `gt spec show SPEC-2100` shows status `implemented`, type `requirement`,
  priority P1, the M1-M20 metric catalogue, the on-demand aggregation clause, and
  the trend-analysis clause.
- `gt tests list --spec-id SPEC-2100` returns only `TEST-11219` ("Spec-derived
  test for SPEC-2100"), a phantom placeholder with no `test_file` path.
- `groundtruth-kb/src/groundtruth_kb/db.py:7726-7972` implements the 9 Phase-1
  metric methods; `get_lifecycle_metrics(last_n_days=None)` at line 7974
  aggregates exactly `{M2, M4, M6, M10, M11, M12, M16, M17, M18}` and threads
  `last_n_days` to `compute_m6_defect_injection_rate`.
- `groundtruth-kb/tests/test_lifecycle_metrics.py` already covers each Phase-1
  metric and the structured-metadata contract but is not WI-bridged and does not
  assert the scope-boundary, time-window, or on-demand-aggregation clauses.

## Proposed Scope

1. Add `platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py`.
2. Phase-1 scope-boundary manifest: assert `get_lifecycle_metrics()` returns
   exactly the 9 implemented keys `{M2, M4, M6, M10, M11, M12, M16, M17, M18}`;
   assert none of the 11 deferred ids (`M1, M3, M5, M7, M8, M9, M13, M14, M15,
   M19, M20`) is present; assert the corresponding `compute_m*` methods exist for
   the 9 and are absent for a representative deferred id (e.g. no
   `compute_m1_*`/`compute_m5_*` attribute) — locking the implemented-vs-intended
   boundary against silent drift.
3. Time-window / trend computability: seed a dataset whose defect and
   implemented-spec timestamps straddle a window cutoff, then assert
   `get_lifecycle_metrics(last_n_days=N)` and `compute_m6_defect_injection_rate(last_n_days=N)`
   honor the window (windowed result differs from all-time); assert
   `compute_m17_stale_test_ratio(now=...)` honors the injected `now` so trend
   computation over a window is deterministic.
4. On-demand aggregation ("No pre-aggregation"): compute a metric (e.g. M12
   retirement rate or M6), mutate the DB (retire a spec / add a defect WI),
   recompute on the same `KnowledgeDB`, and assert the value reflects the new
   state — proving on-demand computation from live tables rather than a cached or
   pre-aggregated value.
5. Structured-metadata smoke: assert every metric returned by
   `get_lifecycle_metrics()` is a dict with `value` and `unit` keys (minimal
   contract restatement; the exhaustive per-metric and ratio-metadata assertions
   remain in `groundtruth-kb/tests/test_lifecycle_metrics.py` and are referenced,
   not duplicated).
6. Do not change production source, formal artifacts, project membership,
   release/deployment state, existing MemBase test rows, credentials, or Agent Red
   application behavior.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-2100` (Phase-1 scope) | `get_lifecycle_metrics()` returns exactly the 9 implemented keys; deferred ids absent; deferred `compute_m*` attributes absent. |
| `SPEC-2100` (trend / time windows) | Windowed `get_lifecycle_metrics(last_n_days=N)` / `compute_m6(last_n_days=N)` differ from all-time on a straddling dataset; `compute_m17(now=...)` honors injected now. |
| `SPEC-2100` (on-demand aggregation), `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Mutate-then-recompute proves metrics reflect live state with no pre-aggregation/caching. |
| `SPEC-2099` (data dependency) | M6/M10 aggregation over `pipeline_events`-backed data is exercised through the seeded dataset. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the live `KnowledgeDB` metric interface, creating an explicit test file for WI-3218 rather than relying on phantom-only evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3218-lifecycle-metrics-computed-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, targeted pytest, adjacent pytest, and a whitespace diff check on the touched file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py -q --tb=short
python -m pytest platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py groundtruth-kb/tests/test_lifecycle_metrics.py -q --tb=short
python -m ruff check platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py
python -m ruff format --check platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py
git diff --check -- platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py
```

## Acceptance Criteria

- PASS when `get_lifecycle_metrics()` returns exactly the 9 Phase-1 keys and no
  deferred id is present, and deferred `compute_m*` attributes are absent.
- PASS when windowed aggregation differs from all-time on a straddling dataset and
  `compute_m17(now=...)` is deterministic.
- PASS when a mutate-then-recompute sequence proves on-demand aggregation.
- PASS when every aggregated metric is a structured dict with `value` + `unit`.
- PASS when targeted pytest, adjacent pytest, ruff check, ruff format check, and
  diff whitespace checks pass.
- PASS when no production source, formal artifacts, project membership, new work
  items, credentials, release tags, deployment state, or Agent Red application
  behavior are changed.

## Risks / Rollback

Risk is low. This is additive test coverage over implemented platform behavior.
The main risk is coupling to the exact Phase-1 metric set; that coupling is
intentional — the test's purpose is to lock the implemented-vs-intended boundary,
and a future metric promotion (e.g. M5) is expected to update this manifest
deliberately.

Rollback is to delete `platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py`.
Bridge audit files remain append-only.

## Files Expected To Change

- `platform_tests/scripts/test_lifecycle_metrics_spec2100_coverage.py`

## Pre-Filing Preflight Evidence

Both mandatory preflights were run against this draft body (`--content-file`)
before filing. Loyal Opposition should rerun both against the operative bridge
file.

Applicability preflight (`scripts/bridge_applicability_preflight.py --content-file ... --json`):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `work_items: ["WI-3217", "WI-3218"]` (WI-3218 is the authoritative `Work Item:`
  header; WI-3217 appears only as a sibling cross-reference in the body prose).

Clause preflight (`scripts/adr_dcl_clause_preflight.py --content-file ...`):

- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

Phantom-spec sweep: all cited SPEC/GOV/ADR/DCL ids (the WI-3217 proven battery
plus `SPEC-2099` and `SPEC-2100`) confirmed present in the live `specifications`
table.

## Recommended Commit Type

`test:`
