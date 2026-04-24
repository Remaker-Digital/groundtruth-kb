NO-GO

# GTKB Scoped Service Boundary Baseline Review Revision 3

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-005.md`

## Verdict

NO-GO on Revision 2 as currently proposed.

Revision 2 correctly narrows the focused verification lane by removing
`tests/scripts/test_groundtruth_governance_adoption.py`; live rerun confirms
that suite still fails on 3 unrelated tests while
`tests/scripts/test_release_candidate_gate.py` and
`tests/scripts/test_session_self_initialization.py` are currently clean.

The remaining blocker is in the implementation scope, not the test lane: the
proposal adds a scoped client for both `dashboard.summary.read` and
`dashboard.history.read`, but it only commits to routing one startup/dashboard
read path through that client. The live startup/dashboard flow still has two
separate raw `groundtruth.db` readers for those surfaces, so the proposed slice
does not yet make the scoped client the real boundary for the functionality it
claims.

## Prior Deliberations

- `DELIB-0877`, `DELIB-0878`, and `DELIB-0879` remain the current GTKB
  application-isolation planning context for this thread.
- Direct bridge priors are `-002` and `-004` (NO-GO) and `-003` and `-005`
  (REVISED).

## Findings

### F1 - The proposal still leaves parallel raw `groundtruth.db` dashboard reads in the live startup path

Severity: High

Evidence:

- Revision 2 defines a scoped client surface with two read operations,
  `dashboard.summary.read` and `dashboard.history.read`:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-005.md:91-101`
  and `:136-149`.
- The same revision only commits to "one" startup/dashboard integration point:
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-005.md:109-112`
  and `:154-163`.
- Live startup-model generation still reads raw `groundtruth.db` directly for
  the current dashboard summary surface:
  `scripts/session_self_initialization.py:645-709` and
  `:2355-2360`.
- Live dashboard/history generation still reads raw `groundtruth.db` directly
  for the historical backfill path before writing dashboard history output:
  `scripts/session_self_initialization.py:2552-2616` and
  `:4417-4445`.

Risk/impact:

If this slice receives GO as written, the new scoped client would exist beside
the real startup/dashboard readers instead of becoming the authoritative
boundary for them. That leaves a partial adoption pattern where one of the two
advertised read operations can remain unintegrated while the dashboard pipeline
continues to bypass the new contract on a parallel raw SQLite path. For a
service-boundary baseline, that is too weak a proof point.

Required action:

Revise the proposal so the first slice chooses one of these coherent options:

1. Route both live startup/dashboard read surfaces that map to the proposed
   client contract through the scoped client (or a single client-backed helper
   that owns both summary and history generation), and add tests that guard
   against direct `groundtruth.db` reads remaining on those paths.
2. Narrow the client contract and claim to a single read operation, then defer
   the second operation and its corresponding startup/dashboard path to a later
   bridge slice.

## Passing Evidence

- The focused-lane correction from `-004` is real:
  `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  currently exits 1 with 3 failures tied to missing `workstream-focus.py`
  expectations and a `file-bridge-protocol.md` wording assertion.
- `python -m pytest tests/scripts/test_release_candidate_gate.py -q --tb=short`
  currently passes with 9 passed.
- `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
  currently passes with 21 passed.

## Required Action Items Or Conditions

1. Revise the implementation scope so the scoped client owns the full live
   startup/dashboard surface it claims, or narrow the claimed client surface to
   match the one path actually being migrated.
2. Preserve the `-005` focused-verification-lane correction; that part should
   carry forward unchanged.

## Decision Needed From Owner

None for this NO-GO.
