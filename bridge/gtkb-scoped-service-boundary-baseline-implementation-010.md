VERIFIED

# GTKB Scoped Service Boundary Baseline Verification

**Status:** VERIFIED
**Date:** 2026-04-23
**Reviewed report:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-009.md`

## Verdict

VERIFIED.

The implementation matches the approved summary-only Phase 4 slice from
`bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md`, and the
three approval conditions recorded in `bridge/gtkb-scoped-service-boundary-baseline-implementation-008.md`
are satisfied on the live tree.

## Findings

### F1 - The approved summary-only scoped boundary is implemented and enforced

Severity: None

Evidence:

- Root `groundtruth.toml` now defines `[scoped_service]` with
  `allowed_read_operations = ["dashboard.summary.read"]` and no request-class
  operations: `groundtruth.toml:17-28`.
- `scripts/gtkb_scoped_client.py` constrains the slice to
  `dashboard.summary.read`, rejects non-empty `allowed_request_operations`, and
  owns the summary-path `sqlite3.connect(...)` call:
  `scripts/gtkb_scoped_client.py:49-50`, `:161-168`, `:214-256`, `:284-285`.
- `scripts/session_self_initialization.py` routes `_database_metrics(...)`
  through `GtkbScopedClient.invoke(DASHBOARD_SUMMARY_READ, ...)` and no longer
  opens `groundtruth.db` directly on that path, while the deferred history path
  remains isolated in `_historical_agent_red_backfill(...)`:
  `scripts/session_self_initialization.py:653-699`, `:2385-2390`,
  `:2582-2587`.
- `scripts/check_scoped_service_boundary.py` checks both config drift and a
  no-raw-read guard for `_database_metrics`: 
  `scripts/check_scoped_service_boundary.py:54-88`, `:136-155`.
- `scripts/release_candidate_gate.py` runs
  `scripts/check_scoped_service_boundary.py` before the pytest lane, and the
  focused regression tests cover the checker and ordering:
  `scripts/release_candidate_gate.py:84-109`,
  `tests/scripts/test_release_candidate_gate.py:190-214`,
  `tests/scripts/test_gtkb_scoped_client.py:308-345`.
- Live verification on the current tree:
  - `python scripts/check_scoped_service_boundary.py --json` -> `status: "pass"`
  - `python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py -q --tb=short`
    -> `51 passed, 1 warning in 211.18s`

Risk/impact:

The scoped client is now the authoritative boundary for the one read surface
claimed in this slice, with a mechanical regression guard on the migrated
startup summary path.

Recommended action:

Mark the post-implementation report VERIFIED.

### O1 - The broader release-gate pytest lane still includes out-of-slice governance coverage

Severity: Low

Evidence:

- `scripts/release_candidate_gate.py` still includes
  `tests/scripts/test_groundtruth_governance_adoption.py` in the broader pytest
  lane alongside the new focused suites:
  `scripts/release_candidate_gate.py:97-110`.
- The approved bridge thread narrowed this slice's proof surface to the focused
  checker plus three test modules, not the full broader release gate:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md:166-184`.

Risk/impact:

`python scripts/release_candidate_gate.py --skip-frontend` is still broader
than the slice-specific proof lane and may surface unrelated governance drift.
That does not invalidate this verification, but the two lanes should not be
treated as equivalent.

Recommended action:

Keep using the focused checker + pytest lane as the acceptance signal for this
slice until the separate governance normalization work lands.

## Decision Needed From Owner

None.
