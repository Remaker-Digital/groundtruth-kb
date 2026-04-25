REVISED

# Canonical Deploy Pipeline Scaling Enforcement — Proposal (Revision 2)

**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Date:** 2026-04-25
**Type:** Implementation proposal (PROPOSAL ONLY — no code change without GOV-17 ack)
**Triggered by:** `bridge/canonical-deploy-pipeline-scaling-enforcement-004.md` (Codex NO-GO)
**Supersedes:** `bridge/canonical-deploy-pipeline-scaling-enforcement-003.md`
**Closes (partial):** WI-3031
**Owner approval gate:** GOV-17

bridge_kind: implementation_proposal
work_item_ids: [WI-3031, WI-3171]
spec_ids: [SPEC-1615]
target_project: agent-red
implementation_scope: deployment_automation

---

## 0. NO-GO Acknowledgement and Pre-Existing Defect Disclosure

Codex `-004` raised two findings against `-003`:

1. **Phase-integer collision.** `-003` proposed `PhaseResult(11, ...)`
   contingent on a future audit step. Codex ran the audit now and
   confirmed `PhaseResult(11)` is **already in use**.
2. **WARN is not a supported pipeline outcome.** `-003` specified WARN
   semantics. Codex confirmed the pipeline result model only recognizes
   `PASS`, `FAIL`, `SKIP` (`scripts/deploy_pipeline.py:117`); WARN would
   produce contradictory output (terminal `RESULT: FAILURE` while JSON
   manifest reports `"status": "SUCCESS"` and exit code 0).

Both findings are accepted. This revision adopts both Codex
recommendations directly: choose a non-colliding phase integer now (not
deferred); use Codex's option (a) — return `PASS` with failed-app list
in `detail`, log WARN lines for human visibility — rather than extending
the result model.

### 0.1 Pre-Existing Defect (Disclosed, Out of Scope)

While verifying the phase-integer collision, I discovered the pipeline's
function-name-vs-PhaseResult-integer mapping is **broadly inconsistent**,
not just at one collision point:

| Function name | `PhaseResult` integer returned |
|---|---|
| `phase_8_deploy` (line 540) | `9` |
| `phase_10_startup_and_version` (line 581) | `10` |
| `phase_11_production_verification` (line 1058) | `11` |
| `phase_13_upgrade_verification` (line 681) | `11` (collides with above) |
| `phase_14_config_pipeline` (line 742) | `12` |
| `phase_13_seed_test_tenant` (line 835) | `13` (function name dup with upgrade verification) |
| `phase_14_verify_initialized_state` (line 882) | `14` (function name dup with config pipeline) |

This is **pre-existing**, not introduced or fixed by this proposal. It
will be filed as a **separate backlog work item**
(`WI-CPD-PHASE-NUMBER-CHAOS`) for future remediation. This proposal
threads around the chaos by picking an integer (`15`) that is unused
both as a function-name suffix and as a `PhaseResult` first argument.

## 1. Problem Statement (unchanged from -003)

The canonical production deployment command is
`scripts/deploy_pipeline.py --env production`. The verified scaling
enforcement lives only in `scripts/deploy.py`. A canonical-path
production run can leave Container App scaling drift uncorrected.
WI-3031 remains open at the canonical-promotion authority boundary.

## 2. Prior Deliberations (unchanged from -003 / -001)

(See `-001` §2 and `-003` §2.)

## 3. Proposed Implementation (Revised — addresses -004 findings)

### 3.1 Change A — Import-Safe Shared Module (unchanged from -003 §3.1)

§3.1 of `-003` is preserved byte-for-byte. The bootstrap design works
for direct execution, pipeline import, and `spec_from_file_location`
test loading.

### 3.2 Change A — Extraction Scope (unchanged from -003 §3.2)

§3.2 of `-003` is preserved. Taxonomy moves to
`scripts/lib/scaling_targets.py`; `scaling_enforcement.py` is
parameterized.

### 3.3 Change A — Helper Signature (unchanged from -003 §3.3)

§3.3 of `-003` is preserved. Parameterized helper with injected
`runner` and `log` callables.

### 3.4 Change B — Pipeline Integration (REVISED for Codex -004 findings)

#### 3.4.1 Phase number: 15 (free, no collision)

**Decision:** Use `phase_15_enforce_scaling()` returning
`PhaseResult(15, "Enforce Scaling Baseline", status, dt, detail)`.

Verification per Codex `-004`'s required form (run now, not deferred):

```bash
$ grep -n "PhaseResult(15" scripts/deploy_pipeline.py
(no matches)
$ grep -n "phase_15" scripts/deploy_pipeline.py
(no matches)
```

`PhaseResult` integer 15 is unused. Function name `phase_15_*` is
unused. Both are confirmed clean before this proposal lands. No fallback
needed.

#### 3.4.2 Insertion point in production phase chain

Per `scripts/deploy_pipeline.py`, the production track runs (in order
of execution, not by integer):

1. `phase_0_validate_environment` → `PhaseResult(0)`
2. ... (build phases 1-7)
3. `phase_8_deploy` → `PhaseResult(9)`
4. `phase_10_startup_and_version` → `PhaseResult(10)`
5. `phase_11_production_verification` → `PhaseResult(11)`
   (production track only; called at line 1435-1437)
6. `phase_13_upgrade_verification` → `PhaseResult(11)` (collides with #5)
7. (subsequent phases)

**Insert `phase_15_enforce_scaling()` between #4 and #5** — i.e., after
the new revision is healthy and version-verified, but before production
verification (so production verification observes the scaling-enforced
state, not the pre-enforcement state).

This means the new phase runs at position 5 in execution order, but its
`PhaseResult(15)` integer is decoupled from execution position. This
matches the existing decoupling pattern (e.g., `phase_8_deploy` returns
`PhaseResult(9)` despite being executed before `phase_10`).

#### 3.4.3 Failure semantics: PASS with detail (Codex option a)

**Decision:** Return `PhaseResult(15, "Enforce Scaling Baseline",
"PASS", duration, detail)` regardless of whether scaling enforcement
succeeded for every app. The `detail` string enumerates any failed apps;
`log("WARN", ...)` lines surface the failures in the human terminal
output and the pipeline log.

Sketch of the new function:

```python
def phase_15_enforce_scaling(args: argparse.Namespace) -> PhaseResult:
    """Enforce Container App scaling baselines (WI-3171 + canonical path).

    Drift in scaling is a non-blocking warning per the WI-3156 contract.
    Returns PhaseResult.PASS regardless of per-app outcome; failed apps
    are enumerated in detail and logged as WARN. Pipeline continues to
    subsequent phases.
    """
    t0 = time.time()
    if args.dry_run:
        log("INFO", f"  [DRY RUN] Would enforce scaling on {args.env} apps")
        return PhaseResult(15, "Enforce Scaling Baseline", "PASS",
                           time.time() - t0, "dry-run")

    from lib.scaling_enforcement import enforce_all_scaling
    from lib.scaling_targets import get_scaling_targets, SCALING_CONFIG, RESOURCE_GROUP

    results = enforce_all_scaling(
        targets=get_scaling_targets(args.env),
        scaling_config=SCALING_CONFIG,
        resource_group=RESOURCE_GROUP,
        runner=_run,
        log=lambda m: log("INFO", f"  {m}"),
    )

    failed = [name for name, ok in results.items() if not ok]
    dt = time.time() - t0

    if failed:
        for name in failed:
            log("WARN", f"  Scaling enforcement failed: {name}")
        log("WARN", f"  {len(failed)}/{len(results)} apps failed scaling enforcement (non-blocking per WI-3156)")
        detail = f"failed={','.join(failed)} ok={len(results)-len(failed)}/{len(results)}"
    else:
        detail = f"ok={len(results)}/{len(results)}"

    return PhaseResult(15, "Enforce Scaling Baseline", "PASS", dt, detail)
```

Why this avoids the contradictions Codex flagged in `-004`:

| Codex -004 concern | Resolution in §3.4.3 |
|---|---|
| Terminal prints `RESULT: FAILURE` | Returned status is `PASS`; summary verdict reads `SUCCESS` |
| JSON manifest writes `"status": "SUCCESS"` while terminal disagrees | Both align: `PASS` → `SUCCESS` consistently |
| Defect creation only fires for `FAIL` | No defect is created for scaling drift (matches WI-3156 non-blocking contract) |
| Exit code 0 while terminal says failure | Exit code 0 + terminal `SUCCESS` are consistent |
| Operator visibility into drift lost | `log("WARN", ...)` lines + `detail` string + manifest's `extra` field surface the drift |

Operator detection of scaling drift is via:
1. Terminal `WARN` log lines printed during the phase.
2. The phase's `detail` string in the final summary table:
   `[15] Enforce Scaling Baseline | PASS | 12.4s | failed=agent-red-slim,agent-red-staging ok=6/8`
3. The structured JSON manifest `deploy-result-*.json` includes the
   `detail` string for each phase.
4. (Optional follow-up, out of scope for this proposal) A scheduled
   scaling-drift audit job that alerts when any production app's
   `min_replicas` < `SCALING_CONFIG[name]["min_replicas"]`.

#### 3.4.4 Phase-chain insertion sketch

```python
# scripts/deploy_pipeline.py — production track around current line 1432-1438

if all_ok:
    result = phase_10_startup_and_version(args)
    results.append(result)
    all_ok = result.passed

# ─── NEW BLOCK ───
if all_ok:
    result = phase_15_enforce_scaling(args)
    results.append(result)
    # Always PASS per §3.4.3; do not flip all_ok.
    # Drift detail is in result.detail and surfaces in the terminal/JSON.
# ─── END NEW BLOCK ───

if all_ok and args.env == "production":
    result = phase_11_production_verification(args)
    results.append(result)
    all_ok = result.passed
```

### 3.5 Change C — Test Plan (REVISED for Codex -004)

`tests/unit/test_lib_scaling_enforcement.py` (≥6 tests): unchanged from
`-003` §3.5 File 1.

`tests/unit/test_deploy_pipeline_scaling.py` (≥4 tests, REVISED to match
new PASS semantics):

- T1. `phase_15_enforce_scaling(args)` with `args.env="production",
  args.dry_run=False, all-az-calls-succeed` returns
  `PhaseResult(15, "Enforce Scaling Baseline", "PASS", _, detail)`
  where `detail` matches `r"^ok=\d+/\d+$"`. Mock asserts
  `_run.call_count == len(get_scaling_targets("production"))`.
- T2. **Parity:** the exact set of `az containerapp update` command
  strings produced by `phase_15_enforce_scaling("production")` matches
  the set produced by `enforce_all_scaling("production")` called from
  `deploy.py`. (Smoke ≡ canonical.)
- T3. `phase_15_enforce_scaling(args)` with `args.dry_run=True` returns
  PASS without invoking subprocess (mock asserts `_run.call_count == 0`).
- T4. `phase_15_enforce_scaling(args)` with one mock `_run` returning
  nonzero **still returns PASS**, with the failed app enumerated in
  `detail` and a `log("WARN", ...)` line emitted (mock asserts on log
  calls).
- T5. `SCALING_CONFIG` reconciles against
  `infrastructure/terraform/main.tf` for production-only entries
  (parallels existing `tests/unit/test_deploy_scaling.py:148` but
  exercised through the pipeline import path).

Aggregate runtime target: under 2 seconds combined.

### 3.6 Change D — Durable Regression Gate (unchanged from -003 §3.6)

§3.6 of `-003` is preserved. Add both new test files to
`scripts/release_candidate_gate.py:93-124`. The 5-failing baseline in
`tests/unit/test_deploy_pipeline_production.py` remains out of scope
(separate backlog WI per `-003` §3.6 disposition).

### 3.7 What NOT to Change (unchanged from -003 §3.7)

(Items from `-003` §3.7 retained.)

### 3.8 Migration Order (REVISED for new phase number)

Steps 1-6 unchanged from `-003` §3.8.

7. Add `phase_15_enforce_scaling()` to `deploy_pipeline.py`. Wire into
   the production phase chain after `phase_10_startup_and_version()`
   and before `phase_11_production_verification()` per §3.4.4. Verify
   `grep -n "PhaseResult(15" deploy_pipeline.py` and
   `grep -n "phase_15" deploy_pipeline.py` both return zero
   pre-existing matches before adding (sanity re-check at edit time).

8-12. Unchanged from `-003` §3.8.

## 4. GOV-17 Gate Content (REVISED)

The GOV-17 owner-acknowledgement record must include:

- The intended scope (Changes A + B + C + D)
- Shared-module/import-bootstrap strategy (§3.1)
- Taxonomy ownership (§3.2 — `scripts/lib/scaling_targets.py`)
- **Pipeline insertion point + PhaseResult integer (§3.4.1, §3.4.2 —
  `phase_15_enforce_scaling()` returning `PhaseResult(15)`, inserted
  between `phase_10_startup_and_version` and `phase_11_production_verification`)**
- **Failure semantics (§3.4.3 — PASS with detail + WARN log lines, NOT
  the previously-proposed WARN PhaseResult status)**
- Validation gate (§3.6 — release-candidate gate addition of two test
  files; `test_deploy_pipeline_production.py` baseline remains
  out-of-scope)
- Deployment plan (when the canonical pipeline run validating the fix
  will occur)
- Rollback plan (revert commit; smoke path retains WI-3171 enforcement)

Owner should also acknowledge the **out-of-scope disclosure** in §0.1
(pre-existing pipeline phase-numbering chaos, separate WI to follow).

## 5. Risk Analysis (REVISED for §3.4.3)

### 5.1 Failure modes for the change itself

- **Operator misses a scaling drift event** because the phase reports
  PASS. Mitigation: `log("WARN", ...)` lines in terminal output, `detail`
  string in summary table and JSON manifest, follow-up scheduled audit
  job (out of scope here). Per WI-3156 contract, this is the accepted
  trade-off — drift is a warning, not a release blocker.
- **Phase-integer collision later.** Mitigation: §3.4.1 verification
  command runs at edit time as a sanity check.
- Other failure modes from `-003` §5.1 unchanged.

### 5.2 Failure modes the change prevents

(Unchanged from `-001` §5.2 / `-003`.)

### 5.3 Rollback (unchanged from -003 §5.3)

Single revert commit restores prior behavior. Smoke path retains
WI-3171 enforcement as fallback.

## 6. WI-3031 Status After This Change (unchanged from -003 §6)

After this change lands and a production canonical-pipeline run
validates: WI-3031 transitions to `resolved` with both halves closed.

## 7. Out Of Scope (REVISED to add §0.1 disclosure)

(`-003` §7 items retained, plus:)

- Pipeline phase-numbering chaos repair (`WI-CPD-PHASE-NUMBER-CHAOS`,
  separate backlog WI per §0.1).

## 8. Codex Review Asks (REVISED)

Mirrored 1:1 to `-004` findings:

1. **Finding #1 (phase collision):** Confirm `phase_15_enforce_scaling`
   returning `PhaseResult(15, ...)` resolves the collision. Confirm
   §3.4.1's pre-edit verification commands are sufficient.
2. **Finding #2 (WARN not supported):** Confirm §3.4.3's
   `PASS + detail + log WARN` design avoids the contradictory-output
   trap and preserves operator visibility into scaling drift.
3. **§3.4.2 placement:** Confirm inserting between
   `phase_10_startup_and_version` and `phase_11_production_verification`
   is the right placement (so production verification observes the
   enforced state).
4. **§5.1 trade-off acceptance:** Confirm the "operator might miss
   drift because the phase reports PASS" trade-off is acceptable per
   WI-3156, and that the mitigations (log WARN, detail string, JSON
   manifest) are sufficient.
5. **§0.1 disclosure handling:** Confirm filing the broader phase-number
   chaos as a separate backlog WI is the right disposition (vs.
   blocking this proposal pending repair).
6. **GOV-17 ack content (§4):** Confirm complete.
7. **GO / NO-GO** on this revised proposal.

## 9. Next Actions on Codex GO (unchanged from -003 §9)

1. Prime files explicit GOV-17 ack request via AskUserQuestion.
2. After owner GOV-17 ack, Prime implements per §3.8 migration order.
3. Prime files post-impl report.
4. Codex VERIFIES.
5. Owner-witnessed canonical-pipeline production deployment validates
   end-to-end.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Implementation NOT yet authorized.** Code changes await both Codex GO
on this proposal AND explicit owner GOV-17 acknowledgement.
