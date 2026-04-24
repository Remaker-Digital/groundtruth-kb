GO

# GTKB Scoped Service Boundary Baseline Review Revision 4

**Status:** GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md`

## Verdict

GO to implement Revision 3 as written.

Revision 3 resolves the `-006` blocker by making the first slice internally
coherent again: it narrows the scoped-client contract to one operation
(`dashboard.summary.read`), commits to fully migrating the live summary path,
and explicitly defers the separate history path to a later slice.

## Rationale

- The proposal now claims only one read operation and binds that claim to the
  exact live summary surface: `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md:33-39`,
  `:57-91`, and `:149-163`.
- The deferred history surface is now explicitly out of scope instead of being
  silently left on a parallel raw-reader path:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md:93-107`
  and `:121-130`.
- Live code still cleanly separates the two raw-reader paths named in `-006`,
  which makes the narrowed migration feasible:
  `scripts/session_self_initialization.py:645-709` and `:2355-2360` for the
  current summary path, versus `scripts/session_self_initialization.py:2552-2616`
  and `:4434-4445` for the historical backfill path.
- A direct search of `scripts/session_self_initialization.py` shows only two
  `sqlite3.connect(...)` sites there, at lines 650 and 2557, so no additional
  dashboard-summary raw reader surfaced beyond the summary/history split
  already named in the bridge thread.

## Findings

### F1 - No residual blocker found after the one-operation narrowing

Severity: None

Evidence:

- Revision 3 narrows the allowlist to `["dashboard.summary.read"]` and removes
  `dashboard.history.read` from this slice's config and client contract:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md:57-65`,
  `:95-106`, and `:113-146`.
- Revision 3 requires full migration of the live summary path and adds a
  no-raw-read guard for that path:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md:79-91`
  and `:159-181`.
- Live code confirms the cited summary path is `_database_metrics(...)`,
  called from `build_startup_model(...)`:
  `scripts/session_self_initialization.py:645-709` and `:2355-2360`.
- Live code confirms the cited history path is separate and remains isolated in
  `_historical_agent_red_backfill(...)`, called only when writing dashboard
  history:
  `scripts/session_self_initialization.py:2552-2616` and `:4434-4445`.

Risk/impact:

The scoped client can now become the authoritative boundary for the one
operation it claims in this slice instead of coexisting with an unscoped
parallel implementation for the same claimed surface.

Recommended action:

Proceed with implementation on the narrowed summary-only slice.

### O1 - The governance-adoption failure count in `-007` is stale, but still non-blocking

Severity: Low

Evidence:

- Revision 3 says `test_groundtruth_governance_adoption.py` remains excluded
  because it has "3 unrelated workstream-focus failures":
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md:183-184`.
- Live rerun now shows a different baseline:
  `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  exited 1 with `1 failed, 29 passed, 1 warning`.
- The remaining failure is the bridge-protocol wording assertion at
  `tests/scripts/test_groundtruth_governance_adoption.py:762-775`, specifically
  the expectation at line 772 that the protocol mention startup reports.
- The focused proof lane named in Revision 3 still excludes that suite:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-007.md:166-184`.
- The in-scope baseline suites cited by Revision 3 are currently green:
  `python -m pytest tests/scripts/test_release_candidate_gate.py -q --tb=short`
  -> `9 passed`; `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
  -> `21 passed`.

Risk/impact:

The stale count does not change the slice boundary or the focused verification
plan, but the post-implementation report should not repeat the older
"3 failures" statement as if it were still current.

Recommended action:

Treat the updated governance-adoption baseline as context only and keep that
suite out of this slice's focused verification lane unless a later bridge item
re-expands scope.

## Conditions Of Approval

1. The implementation must fully replace the summary-path raw DB reader at
   `scripts/session_self_initialization.py:645-709` / `:2355-2360` with the
   scoped client, not merely add the client alongside it.
2. The new checker must fail closed if a direct `sqlite3.connect(...groundtruth.db...)`
   remains on that migrated summary path.
3. The post-implementation report must include fresh output for:
   `python scripts/check_scoped_service_boundary.py --json` and
   `python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py -q --tb=short`.

## Decision Needed From Owner

None for this GO.
