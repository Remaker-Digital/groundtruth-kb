# Bridge Fallback Review: WI-3031 Status

Date: 2026-04-23
Reviewer: Codex Loyal Opposition
Mode: Bridge fallback review / code-config review
Specs: SPEC-1755
WIs: WI-3031, WI-3156, WI-3171

## Claim

The authoritative bridge queue was empty at review start, so no bridge-thread
action was available. The highest-risk open carryover selected as fallback,
`WI-3031`, is no longer a live deploy-path baseline defect. The remaining issue
is stale review memory: `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md`
still says `deploy.py` does not encode the scaling baseline even though the
current deploy path and focused tests now do.

## Evidence

- Live bridge read at session start showed no document whose latest status was
  `NEW` or `REVISED`; all current entries topped out at `VERIFIED`:
  `bridge/INDEX.md:8-87`.
- `scripts/deploy.py` now defines name-keyed scaling baselines for the
  production gateway, staging gateway, six deploy-managed agent apps, and SLIM:
  `scripts/deploy.py:85-98`.
- `scripts/deploy.py` applies scaling with `_enforce_one(...)` and
  `enforce_all_scaling(environment)`: `scripts/deploy.py:183-239`.
- The main deploy path runs the scaling pass after deploy-managed containers are
  updated: `scripts/deploy.py:665`.
- Terraform reference values for the deploy-managed container set still match
  the script baselines for production gateway, agents, and SLIM:
  `infrastructure/terraform/main.tf:138-254`.
- Focused reconciliation tests exist and passed in this session:
  `tests/unit/test_deploy_scaling.py:1-374`;
  command run: `python -m pytest tests/unit/test_deploy_scaling.py -q --tb=short`
  -> `11 passed in 0.25s`.
- A prior Loyal Opposition status review already recorded the open
  `WI-3031` log row as stale and recommended retiring or narrowing it:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-22-12-57-WI-3031-DEPLOY-SCALING-STATUS.md:12-19,38-50,65-85`.
- The still-open log row has not been updated and therefore continues to assert
  the superseded claim:
  `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:112`.

## Risk / Impact

- Severity: `P3` for stale operational memory.
- Practical risk is process drift, not current deploy-path absence. Future
  sessions can keep re-opening an already-verified concern, waste review time,
  and misstate the current release risk around scaling enforcement.
- The narrower residual technical policy question remains unchanged from the
  April 22 review: scaling enforcement is warning-only by design. That is not a
  hidden defect, but it would become a `P2` concern if the project decides
  failed scaling updates must block deployment success.

## Recommended Action

1. Retire or rewrite the `WI-3031` row in
   `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md` on the next
   approved log-maintenance pass.
2. Preserve a narrower note, if desired, that scaling enforcement remains
   warning-only and could be promoted to a hard gate only by an explicit
   project decision.
3. Treat the current bridge state as clean: no pending latest-status
   `NEW`/`REVISED` work was available during this review pass.

## Decision Needed From Owner

None now.

An owner decision is only needed if failed scaling enforcement should stop a
deployment instead of remaining warning-only.
