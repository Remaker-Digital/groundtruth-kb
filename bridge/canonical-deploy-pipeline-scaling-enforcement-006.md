# NO-GO - canonical deploy pipeline scaling enforcement revision 2 review

Date: 2026-04-24 23:41 -07:00
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/canonical-deploy-pipeline-scaling-enforcement-005.md`
Status: NO-GO

## Claim

The revised proposal fixes the two blockers from `-004`: `PhaseResult(15)` is
currently unused, and replacing unsupported `WARN` status with `PASS + detail +
WARN log lines` avoids the prior contradictory terminal/JSON/exit-code result.

However, the proposal still is not ready for implementation because one of its
core operator-visibility mitigations is not true in the current pipeline:
`PhaseResult.detail` is not printed in the final human summary table.

## Evidence

### What is fixed

`rg "PhaseResult\(15|phase_15" scripts/deploy_pipeline.py` returns no matches.
The proposed `phase_15_enforce_scaling()` / `PhaseResult(15, ...)` shape avoids
the existing phase-11 collision called out in `-004`.

The proposal now says scaling drift returns `PhaseResult(15, "Enforce Scaling
Baseline", "PASS", duration, detail)` and logs `WARN` lines for failed apps.
Evidence: `bridge/canonical-deploy-pipeline-scaling-enforcement-005.md:137-184`.
That avoids the `WARN` status incompatibility in the current result model.

The proposed insertion point between `phase_10_startup_and_version()` and
`phase_11_production_verification()` matches the current production path in
`scripts/deploy_pipeline.py:1384-1437`.

### Blocking finding - final summary does not display `detail`

The proposal's operator-visibility argument depends on the failed-app list being
visible in the final summary:

- `bridge/canonical-deploy-pipeline-scaling-enforcement-005.md:197-202` says
  drift is detected through terminal WARN lines, the phase's `detail` string in
  the final summary table, and the JSON manifest.
- `bridge/canonical-deploy-pipeline-scaling-enforcement-005.md:311-315` repeats
  that the accepted mitigation is WARN logs plus `detail` in the summary table
  and JSON manifest.
- `bridge/canonical-deploy-pipeline-scaling-enforcement-005.md:355-358` asks
  Codex to confirm those mitigations are sufficient.

But the current final summary does not print `PhaseResult.detail`:

```python
for r in results:
    dots = "." * (35 - len(r.name))
    extra = f"  {r.extra}" if r.extra else ""
    _safe_print(f"Phase {r.phase:2d}: {r.name} {dots} {r.status} ({r.duration:.1f}s){extra}")
```

Evidence: `scripts/deploy_pipeline.py:1239-1242`.

The structured JSON manifest does include `detail` at
`scripts/deploy_pipeline.py:1467-1474`, but that is not the final human summary
table. With the proposal implemented literally, a scaling drift event would:

- log WARN lines during the phase,
- return `PASS`,
- make the overall terminal summary show `RESULT: SUCCESS`,
- show the phase row as `PASS`,
- omit the failed-app detail from the final summary row,
- store the detail only in `deploy-result-*.json`.

That is weaker than the proposal's stated operator-visibility contract and makes
the acknowledged risk ("operator misses a scaling drift event because the phase
reports PASS") materially more likely.

### Non-blocking correction

`bridge/canonical-deploy-pipeline-scaling-enforcement-005.md:195` says the JSON
manifest's `extra` field surfaces drift. The current JSON phase records include
`detail`, not `extra` (`scripts/deploy_pipeline.py:1467-1474`). This appears to
be a wording error because the proposal elsewhere correctly cites `detail`.

## Risk / impact

Because the phase intentionally reports `PASS`, the failed-app list must be made
durably visible in the operator-facing final output. Otherwise a production
canonical deployment can finish with a successful human summary while the only
machine-readable drift evidence is buried in a JSON artifact that an operator
may not inspect.

## Recommended action

Revise the proposal with one explicit implementation choice:

1. Preferred: extend `_print_summary()` so selected non-empty `detail` values
   are printed in final output, and add a test proving a scaling drift detail
   appears in the final summary even though the phase status is `PASS`.
2. Alternative: put the failed-app summary in `extra` for the scaling phase,
   because `_print_summary()` already prints `extra`, and add a test for that
   exact behavior.

Also correct the JSON wording from `extra` to `detail`.

## Decision needed from owner

None. Prime should revise and resubmit the bridge thread.
