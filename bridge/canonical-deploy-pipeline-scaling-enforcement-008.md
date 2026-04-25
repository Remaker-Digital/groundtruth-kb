# GO - canonical deploy pipeline scaling enforcement revision 3 review

Date: 2026-04-24 23:50 -07:00
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/canonical-deploy-pipeline-scaling-enforcement-007.md`
Status: GO

## Claim

The revised proposal is ready for the next gate. `-007` resolves the `-006`
operator-visibility blocker by moving the failed-app enumeration from
`PhaseResult.detail` to `PhaseResult.extra`, which the current final summary
printer already displays.

Implementation is still gated by explicit GOV-17 owner acknowledgement, as the
proposal states.

## Evidence

### Prior blocker resolved

`scripts/deploy_pipeline.py:1239-1242` prints `r.extra` in the final summary:

```python
for r in results:
    dots = "." * (35 - len(r.name))
    extra = f"  {r.extra}" if r.extra else ""
    _safe_print(f"Phase {r.phase:2d}: {r.name} {dots} {r.status} ({r.duration:.1f}s){extra}")
```

`bridge/canonical-deploy-pipeline-scaling-enforcement-007.md:87-142` now puts
the human-visible drift enumeration in `extra`, e.g.
`DRIFT: 2/8 failed (agent-red-slim,agent-red-staging)`, while retaining
`PASS` status and a machine-readable count in `detail`.

`bridge/canonical-deploy-pipeline-scaling-enforcement-007.md:198-207` adds the
required operator-visibility regression test: capture `_print_summary()` output
for a `PASS` scaling phase with `extra="DRIFT: 2/8 failed (app-a,app-b)"` and
assert that substring appears in the final summary output.

### Other prior concerns remain resolved

`rg "PhaseResult\(15|phase_15" scripts/deploy_pipeline.py` returns no matches,
so the proposed phase number and function name remain non-colliding.

The proposal continues to avoid unsupported `WARN` status by returning `PASS`
for non-blocking scaling drift and surfacing drift through WARN log lines plus
the final summary `extra` marker.

The insertion point remains after `phase_10_startup_and_version()` and before
`phase_11_production_verification()`, matching the current production path in
`scripts/deploy_pipeline.py:1384-1437`.

`scripts/deploy_pipeline.py:1467-1474` serializes `detail` in the JSON manifest.
`-007` now describes that correctly: terminal summary uses `extra`; JSON
manifest uses `detail`.

## Risk / impact

No blocking review findings remain in the proposal. The main implementation
risk is preserving the exact visibility contract during coding: drift must be
visible in final terminal output even though the phase status is `PASS`.

## Recommended action

Proceed to the explicit GOV-17 owner acknowledgement request. If the owner
acknowledges, implement per `-007`, including both new test files in
`scripts/release_candidate_gate.py` and preserving the T5 summary-output
regression test.

## Non-blocking note

Consider including failed app names in `detail` as well as `extra` if it remains
simple during implementation. This is not required for GO because `extra` and
WARN logs satisfy the operator-visibility contract, and `detail` already gives
JSON consumers machine-readable counts.

## Decision needed from owner

GOV-17 acknowledgement is required before implementation.
