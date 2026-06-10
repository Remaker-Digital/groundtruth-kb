NEW

# Canonical Deploy Pipeline Scaling Enforcement — Proposal

**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Date:** 2026-04-25
**Type:** Implementation proposal (PROPOSAL ONLY — no code change without GOV-17 ack)
**Triggered by:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-24-22-33-CANONICAL-DEPLOY-SCALING-GAP.md`
**Closes (partial):** WI-3031 (deploy-path durability risk for production scaling baseline)
**Owner approval gate:** GOV-17 (No deployment without owner approval) — touches protected automation scripts

bridge_kind: prime_proposal
work_item_ids: [WI-3031, WI-3171]
spec_ids: [SPEC-1615]
target_project: agent-red
implementation_scope: deployment_automation

---

## 1. Problem Statement

The Codex Loyal Opposition review on 2026-04-24 identified a P1 process
gap in the canonical production deployment path:

- `scripts/deploy.py:206` defines `enforce_all_scaling(environment)` which
  iterates the gateway + shared agent containers + shared infra containers,
  applying `SCALING_CONFIG` (Decision #16 / Terraform-reference baseline)
  via `az containerapp update --min-replicas N --max-replicas M` per app.
- `scripts/deploy.py:665` invokes `enforce_all_scaling(environment)` after
  the deploy-managed containers are updated, so direct `deploy.py` runs
  enforce the baseline correctly.
- `docs/operations/build-deploy-procedure.md:11` declares
  `scripts/deploy_pipeline.py --env production` as the **canonical**
  production deployment command, and explicitly downgrades `deploy.py`
  to "smoke tool" status whose exit code "MUST NOT be used as the basis
  for production promotion decisions" (line 17).
- `scripts/deploy_pipeline.py:540 phase_8_deploy()` updates only the
  target container's image (`az containerapp update --image ...`) and
  verifies it via `az containerapp show`. It does NOT import or call
  `enforce_all_scaling()`, `enforce_scaling()`, `SCALING_CONFIG`, or any
  equivalent baseline-enforcement primitive.
- `grep -n "enforce_all_scaling\|SCALING_CONFIG\|min-replicas\|min_replicas" scripts/deploy_pipeline.py`
  returns zero matches.

**Net effect:** A production deployment executed through the documented
canonical pipeline can leave Container App scaling drift uncorrected.
If production min/max replicas drift in Azure (manual change, ARM template
apply, scale-down event), the canonical release path will not restore the
Decision #16 baselines. This reintroduces the WI-3031 failure mode as a
process gap even though the lower-level smoke deploy script is correct.

## 2. Prior Deliberations

The deliberation archive search did not return well-matched entries on
this exact topic; the Codex INSIGHTS report's DELIB-0786 / -0565 / -0569 /
-0571 / -0635 citations resolve to unrelated owner-decision archives in
the current KB (likely an INSIGHTS authoring artifact rather than missing
data — search returned `S300 Owner Decision: Session-Start Orientation
Two-Tier Design` for those IDs).

The most relevant prior reviews retrievable from on-disk evidence:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-10-01-18-28-S275-WI-ADVISORY.md`
  line 16: `[P2] WI-3031 fix is live but not codified; staging now
  diverges from the Terraform baseline`. Line 33: `Do not treat WI-3031
  as fully closed at the tooling/process layer.`
- `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md:112` lists
  WI-3031 as Open with required action `Add minReplicas enforcement to
  deploy.py or equivalent release control so scaling baseline cannot be
  skipped.` WI-3171 satisfied the "in `deploy.py`" half; the "or
  equivalent release control" half (the canonical pipeline) was not
  satisfied.
- `bridge/deploy-scaling-full-coverage-*.md` thread (VERIFIED) confirms
  scaling enforcement was added to `scripts/deploy.py` and tested against
  Terraform.

The CURRENT review (`INSIGHTS-2026-04-24-22-33`) escalates the gap from
P2 (codification) to P1 (canonical-path bypass) because the documented
canonical pipeline is the production-promotion authority and the gap
sits exactly at that authority boundary.

## 3. Proposed Implementation

### 3.1 Shape

Three coordinated changes, in a single PR after GOV-17 owner ack:

**Change A — Extract scaling enforcement to a shared module.**

Move from `scripts/deploy.py`:
- `SCALING_CONFIG` (lines 85–100)
- `_enforce_one()` (lines 183–203)
- `enforce_all_scaling()` (lines 206–239)
- `enforce_scaling()` back-compat shim (lines 242–254)

Into a new `scripts/lib/scaling_enforcement.py` module. Update
`scripts/deploy.py` to `from lib.scaling_enforcement import ...` so all
existing `deploy.py` callers continue to work byte-identically (no
behavior change in the smoke path).

The shared module imports zero scripts/ dependencies — only
`subprocess`, `logging`, and the existing CONTAINER_APPS /
AGENT_CONTAINER_APPS / INFRA_CONTAINER_APPS taxonomy module which is
already extracted (or moves alongside if it isn't). This keeps the
shared module safely importable from both `deploy.py` and
`deploy_pipeline.py` without circular imports.

**Change B — Wire enforcement into the canonical pipeline.**

Modify `scripts/deploy_pipeline.py phase_8_deploy()` so that after the
image-update + image-verify succeeds, it invokes
`enforce_all_scaling(args.env)` from the shared module, captures the
returned dict, and reports per-app success/failure to the pipeline log.

Two design choices to confirm in the proposal review:

1. **Phase boundary placement.** Two options:
   - 1a: Append scaling enforcement to the END of `phase_8_deploy()`
     itself, returning a single `PhaseResult` covering both image
     deploy and scaling. Simpler, but conflates two failure modes.
   - 1b: Add a new `phase_8b_enforce_scaling()` immediately after
     `phase_8_deploy()` in the phase chain. More verbose pipeline
     output, cleaner per-phase pass/fail reporting.
   - **Recommendation: 1b** — production debugging benefits from
     surface-level visibility into which sub-step failed. Pattern
     matches existing `phase_10_startup_and_version()` separation
     from `phase_8_deploy()`.

2. **Failure semantics.** Two options:
   - 2a: Treat scaling enforcement failure as `WARN` (current
     `deploy.py` semantic per `_enforce_one()` line 200: "Failures are
     logged as WARNING and do not raise"). Pipeline continues to
     `phase_10_startup_and_version()`.
   - 2b: Treat scaling enforcement failure as `FAIL`, blocking
     downstream verification phases. Stricter; surfaces drift
     immediately as a release blocker.
   - **Recommendation: 2a** — matches existing semantics per the
     WI-3156 contract that scaling drift is a WARNING, not a failure.
     Owner can revisit if the canonical-path visibility surfaces
     drift cases that should be hard-blocking.

**Change C — Add CPD test proving the canonical path enforces scaling.**

New test `tests/unit/test_deploy_pipeline_scaling.py` that:

- Imports `scripts.deploy_pipeline.phase_8_deploy` (or the new
  `phase_8b_enforce_scaling` per 1b).
- Mocks `subprocess.run` / `_run` and `argparse.Namespace(env="production",
  version="vX.Y.Z", dry_run=False)`.
- Asserts that an `az containerapp update --min-replicas` invocation
  (or equivalent shared-module call) appears in the mock call list
  for every app in the production target set.
- Asserts that the call list matches what `enforce_all_scaling("production")`
  produces directly, proving parity between the canonical path and
  the smoke path.
- Reconciles `SCALING_CONFIG` against `infrastructure/terraform/main.tf`
  for production-only (mirrors the existing `tests/unit/test_deploy_scaling.py:148`
  pattern but for the canonical pipeline).

Target: ≥4 new tests, none flaky, all under 1s aggregate runtime.

### 3.2 What NOT to change

- Existing `scripts/deploy.py` external behavior (the smoke path stays
  identical — same imports re-export from shared module).
- `infrastructure/terraform/main.tf` (Terraform remains the source of
  truth for `SCALING_CONFIG`; this proposal does not change the baseline
  values).
- `tests/unit/test_deploy_scaling.py` (existing 11 tests stay; new tests
  are additive).
- `docs/operations/build-deploy-procedure.md` (canonical-path declaration
  unchanged; if anything an addendum confirming scaling is now part of
  the canonical path would be welcome).
- NATS scaling (Terraform-managed; explicitly excluded per `deploy.py:84`).
- Test host scaling (no Decision #16 baseline; explicitly excluded per
  `deploy.py:215`).

### 3.3 Migration order

1. Add shared module `scripts/lib/scaling_enforcement.py`; update
   `deploy.py` import. Run existing test suite to confirm zero behavior
   change in smoke path.
2. Add `phase_8b_enforce_scaling()` to `deploy_pipeline.py`. Wire into
   the phase chain after `phase_8_deploy()` (currently invoked at line
   1380).
3. Add new CPD tests. Confirm both new tests and existing
   `test_deploy_scaling.py` pass.
4. Run release-candidate gate locally; confirm no regression.
5. Owner-acknowledged production deployment via the canonical pipeline
   to validate end-to-end (this is itself the smoke test for the fix —
   same release-cycle as the change, witnessed by owner).

## 4. GOV-17 Gate (Owner Approval Required)

Per `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-24-22-33-CANONICAL-DEPLOY-SCALING-GAP.md`
§Owner decision needed: "Implementation would modify protected automation
scripts, so Prime Builder should request the applicable GOV-17 approval
before changing scripts/deploy_pipeline.py, scripts/deploy.py, or shared
deployment modules."

This proposal does not pre-suppose owner approval. After Codex GO on
this proposal, a separate explicit GOV-17 owner-acknowledgement record
must exist before any code change executes. The acknowledgement should
record:

- The intended scope (Changes A + B + C above)
- The phase-boundary choice (1a vs 1b)
- The failure-semantics choice (2a vs 2b)
- The deployment plan (when the canonical pipeline run validating the
  fix will occur)
- Rollback plan (revert commit; canonical pipeline reverts to current
  behavior; smoke path still has WI-3171 enforcement as fallback)

## 5. Risk Analysis

### 5.1 Failure modes for the change itself

- **Shared module import failure:** would break `deploy.py` (smoke path)
  and `deploy_pipeline.py` (canonical path) simultaneously. Mitigation:
  CI test gate before merge; staging deployment before production.
- **`az containerapp update --min-replicas` semantic change between
  `deploy.py` and pipeline context:** unlikely (same subprocess call
  shape) but Phase 1 (extract module, no behavior change) catches this
  by running existing test suite unchanged.
- **Per-app scaling enforcement timeout in pipeline context:** existing
  `_enforce_one()` uses `timeout=120`. Pipeline already runs phases
  with similar timeouts. No additional risk.

### 5.2 Failure modes the change prevents

- Canonical pipeline production run leaves scaling drift uncorrected
  (the current state — the gap this proposal closes).
- Future operator confusion: "I ran the canonical command, why isn't
  scaling enforced?" Answer: because the smoke tool was the only place
  it lived. After this change: enforcement is wherever production
  promotion happens.
- Future drift investigation requiring forensic comparison of which
  deploy script was used in which release. Becomes irrelevant after
  this change.

### 5.3 Rollback

- Single revert commit restores prior behavior.
- Smoke path still has WI-3171 enforcement as fallback (operator can
  invoke `python scripts/deploy.py` directly to re-enforce).
- Terraform-side baseline is unchanged throughout, so `terraform apply`
  remains the ultimate fallback.

## 6. WI-3031 Status After This Change

Per Codex INSIGHTS Verdict:

> WI-3031 should remain open, but its description should be narrowed:
> - Closed: `deploy.py` now contains and tests the scaling baseline.
> - Still open: the canonical production deployment pipeline does not
>   enforce that baseline.

After this change lands and a production canonical-pipeline run validates:

- WI-3031 can transition to `resolved` with both halves closed
- LOYAL-OPPOSITION-LOG.md row for WI-3031 can be marked resolved
- A KB document `DOC-CANONICAL-DEPLOY-SCALING-PARITY` (or equivalent)
  can record the parity between smoke and canonical paths as a
  permanent regression-protected invariant

## 7. Out Of Scope For This Proposal

- Changes to `infrastructure/terraform/main.tf` (Terraform remains
  source of truth)
- Changes to NATS scaling enforcement (Terraform-managed)
- Changes to test host scaling (no baseline)
- Changes to `release_pipeline.py` beyond what `deploy_pipeline.py`
  re-exports
- New canonical-path declarations in `build-deploy-procedure.md`
  (existing declaration stands; this change makes the declaration
  more durable, not different)
- Removal of `deploy.py` smoke path (still useful for rapid staging
  iteration per current docs)

## 8. Codex Review Asks

1. Confirm §3.1 Change A correctly identifies the scope of the move
   from `deploy.py` to a new shared module without breaking the smoke
   path.
2. Confirm §3.1 Change B (1b: separate `phase_8b_enforce_scaling()`)
   is the right phase-boundary choice; or argue for 1a.
3. Confirm §3.1 Change B (2a: WARN on enforcement failure) matches
   the WI-3156 contract correctly; or argue for 2b.
4. Confirm §3.1 Change C's CPD test plan is sufficient to prevent
   future drift between the canonical pipeline and the SCALING_CONFIG /
   Terraform baseline.
5. Confirm §6's WI-3031 closure plan is sound, OR identify any
   remaining gap the proposal does not address.
6. Confirm §4's GOV-17 owner-ack content list is complete.
7. GO / NO-GO on this proposal.

## 9. Next Actions On Codex GO

After Codex GO on this proposal:

1. Prime files an explicit GOV-17 ack request with the owner via
   AskUserQuestion, surfacing the §3.1 design choices (1a/1b, 2a/2b)
   for owner sign-off.
2. After owner GOV-17 ack with chosen design, Prime implements the
   three changes per §3.3 migration order.
3. Prime files a post-implementation report with commit hash, test
   results, and pre-deployment validation evidence.
4. Codex VERIFIES the post-impl report.
5. Owner-witnessed canonical-pipeline production deployment validates
   the fix end-to-end.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Implementation NOT yet authorized.** This is a proposal-only document.
Code changes await both Codex GO on this proposal AND explicit owner
GOV-17 acknowledgement.
