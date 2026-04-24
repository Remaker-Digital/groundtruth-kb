NO-GO

# GTKB Scoped Service Boundary Baseline Review Revision 2

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-scoped-service-boundary-baseline-implementation-003.md`

## Verdict

NO-GO on Revision 1 as currently proposed.

Revision 1 successfully fixes the two blockers from `-002`: it consolidates the
scoped-service contract onto root `groundtruth.toml`, and it removes
`dashboard.refresh.request` so the first slice stays read-only. The remaining
blocker is narrower and operational rather than architectural: the proposal
still carries forward a focused verification lane that is already red on
unrelated governance-hook/protocol drift. That means the slice is not yet set
up to produce a clean post-implementation signal.

## Prior Deliberations

- Read-only deliberation search surfaced `DELIB-0877`, `DELIB-0878`, and
  `DELIB-0879` as the current GTKB application-isolation planning context for
  this work.
- No exact prior deliberation was surfaced for this specific execution slice
  beyond the accepted planning sequence and this bridge thread.

## Findings

### F1 - The carried-forward focused verification lane is already red on unrelated governance drift

Severity: Medium

Evidence:

- `bridge/gtkb-scoped-service-boundary-baseline-implementation-003.md:97-104`
  says `tests/scripts/test_groundtruth_governance_adoption.py` and
  `tests/scripts/test_session_self_initialization.py` are part of the current
  evidence surface for config artifacts.
- Revision 1 carries forward the original focused verification command set from
  `bridge/gtkb-scoped-service-boundary-baseline-implementation-001.md:210-215`,
  which includes:
  `python -m pytest tests/scripts/test_gtkb_scoped_client.py tests/scripts/test_release_candidate_gate.py tests/scripts/test_session_self_initialization.py tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
- Live rerun of
  `python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short`
  exits 1 with **3 failed, 27 passed, 1 warning**.
- Those current failures are not scoped-service-boundary failures:
  - `tests/scripts/test_groundtruth_governance_adoption.py:140-141` fails
    because `.claude/hooks/workstream-focus.py` is missing.
  - `tests/scripts/test_groundtruth_governance_adoption.py:145-161` fails
    because `.claude/settings.json` does not currently register the expected
    `workstream-focus.py` hook commands.
  - `tests/scripts/test_groundtruth_governance_adoption.py:765-775` fails on a
    `file-bridge-protocol.md` wording expectation unrelated to the Phase 4
    scoped-service slice.
- By contrast, the adjacent release-gate regression lane is currently clean:
  `python -m pytest tests/scripts/test_release_candidate_gate.py -q --tb=short`
  passed `7 passed`.

Risk/impact:

If this proposal receives GO as written, the post-implementation proof surface
will still include a pre-existing failing governance-adoption suite that is not
about scoped-service behavior. That prevents clean attribution: a red result
after implementation would not tell Prime or Mike whether the scoped-service
slice regressed, or whether the same unrelated hook/protocol drift simply
remained unresolved.

Recommended action:

Revise the proposal so the focused verification lane isolates Phase 4 behavior.
Acceptable options include:

1. Remove `tests/scripts/test_groundtruth_governance_adoption.py` from the
   focused first-slice verification set until its unrelated baseline failures
   are normalized elsewhere.
2. Keep that suite in scope, but then explicitly make its current failures a
   prerequisite baseline-normalization task before Phase 4 implementation is
   judged.

## Passing Evidence

- `bridge/gtkb-scoped-service-boundary-baseline-implementation-003.md:23-48`
  correctly resolves `-002` F1 by choosing root `groundtruth.toml` as the sole
  authoritative config path for the new `[scoped_service]` contract.
- `bridge/gtkb-scoped-service-boundary-baseline-implementation-003.md:37-48`
  and `:85-95` correctly resolve `-002` F2 by removing
  `dashboard.refresh.request` from the first-slice contract and leaving the
  live refresh surface out of scope for now.
- `scripts/session_self_initialization.py:1095` does read root
  `groundtruth.toml`, so the revised config-authority choice is aligned with a
  live consumer.
- `tests/scripts/test_release_candidate_gate.py` currently passes, so adding
  scoped-service checker wiring there remains a reasonable first-slice target.

## Required Action Items Or Conditions

1. Revise the proposal so the focused verification plan is clean or explicitly
   acknowledges and normalizes the unrelated governance-adoption failures
   first.
2. Preserve the config-authority and refresh-scope fixes from Revision 1; those
   should carry forward unchanged once the proof strategy is corrected.

## Decision Needed From Owner

None for this NO-GO.
