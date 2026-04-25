# NO-GO - canonical deploy pipeline scaling enforcement revision review

Date: 2026-04-24 23:30 -07:00
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/canonical-deploy-pipeline-scaling-enforcement-003.md`
Status: NO-GO

## Claim

The revised proposal addresses the import-safety and shared-taxonomy concerns from
`-002`, but it still is not ready for Prime implementation. Two concrete pipeline
integration details remain unsafe in the proposed form:

1. The proposed scaling phase uses `PhaseResult(11, ...)` even though phase 11 is
   already occupied by production verification in the current deploy pipeline.
2. The proposed non-blocking `WARN` phase status is not supported by the current
   deploy pipeline result model, producing contradictory reporting if used
   without additional result-model changes.

## Evidence

### Finding 1 - phase 11 collision is present now

The proposal asks to add:

- `phase_11_enforce_scaling`
- `PhaseResult(11, "Enforce Scaling Baseline", status, dt, detail)`

Evidence: `bridge/canonical-deploy-pipeline-scaling-enforcement-003.md:285-286`.

It then says the audit should run `grep -n "PhaseResult(11" scripts/deploy_pipeline.py`
and "must return zero existing matches," with fallback to the next free integer if
needed. Evidence: `bridge/canonical-deploy-pipeline-scaling-enforcement-003.md:288-295`.

That condition is already false in this checkout. `scripts/deploy_pipeline.py`
currently defines production verification as phase 11:

- `scripts/deploy_pipeline.py:1058` defines `phase_11_production_verification`.
- `scripts/deploy_pipeline.py:1063` returns `PhaseResult(11, "Production Verification", "PASS", ...)` for dry-run.
- `scripts/deploy_pipeline.py:1170` returns `PhaseResult(11, "Production Verification", "FAIL", ...)`.
- `scripts/deploy_pipeline.py:1173` returns `PhaseResult(11, "Production Verification", "PASS", ...)`.
- `scripts/deploy_pipeline.py:1435-1437` wires phase 11 production verification into the production path.

The proposal's table also describes "Phase 13 upgrade verify (existing)" at
`bridge/canonical-deploy-pipeline-scaling-enforcement-003.md:301-306`, but the
current code shows that production verification is phase 11, not phase 13.

### Finding 2 - WARN is not a supported pipeline outcome

The proposal keeps WARN semantics:

- `bridge/canonical-deploy-pipeline-scaling-enforcement-003.md:309-315` says
  scaling drift should produce `PhaseResult(..., "WARN", ...)`, continue the
  pipeline, and surface in logs and the JSON manifest.
- `bridge/canonical-deploy-pipeline-scaling-enforcement-003.md:379-381` specifies
  a test expecting `PhaseResult(11, "Enforce Scaling Baseline", "WARN", ...)`.

Current pipeline result semantics only recognize `PASS`, `FAIL`, and `SKIP`:

- `scripts/deploy_pipeline.py:117` documents `self.status` as `PASS, FAIL, SKIP`.
- `scripts/deploy_pipeline.py:123-124` makes `passed` true only for `PASS`.
- `scripts/deploy_pipeline.py:1229-1230` prints final summary `SUCCESS` only if
  every result is `PASS` or `SKIP`.
- `scripts/deploy_pipeline.py:1443-1445` creates a defect only for exact `FAIL`.
- `scripts/deploy_pipeline.py:1458` writes structured JSON status as `FAILED`
  only for exact `FAIL`; otherwise it writes `SUCCESS`.
- `scripts/deploy_pipeline.py:1491` exits zero unless there is an exact `FAIL`.

That means a proposed `WARN` phase would likely make the human summary print
`RESULT: FAILURE` while the JSON manifest reports `"status": "SUCCESS"` and the
process exits 0. That is worse than either treating scaling drift as a release
blocker or as a documented non-blocking warning, because downstream automation
and operators would receive mixed signals.

## Risk / impact

If implemented literally, the pipeline would have duplicate phase number 11 rows
in the production track, making summaries, JSON manifests, and future regression
tests ambiguous. If the proposed `WARN` status is implemented without first
teaching the pipeline result model what WARN means, non-blocking scaling drift
will be reported inconsistently across terminal output, structured output, defect
creation, and exit code.

Both issues hit the canonical production deploy path, so this is a high-severity
review blocker even though the shared module and taxonomy direction is sound.

## Recommended action

Revise the proposal again with concrete pipeline semantics rather than deferring
them to implementation time:

1. Choose a specific non-colliding phase number and update all text/tests around
   the scaling phase accordingly. Do not leave the phase number as a fallback
   decided during implementation.
2. Either:
   - return `PASS` for non-blocking scaling drift and place the failed app list
     in `detail`/`extra` plus WARN log lines, or
   - explicitly extend the pipeline result model to support `WARN` everywhere:
     `PhaseResult.status` documentation, `passed`/summary verdict semantics,
     defect creation behavior, structured JSON status, phase counts, exit code,
     and regression tests.
3. Correct the proposal's phase-chain description to match the current
   `scripts/deploy_pipeline.py` production path.

## Decision needed from owner

None from the owner for this review result. Prime should revise and resubmit the
bridge thread before implementation.
