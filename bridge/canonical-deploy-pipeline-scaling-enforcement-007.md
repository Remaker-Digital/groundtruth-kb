REVISED

# Canonical Deploy Pipeline Scaling Enforcement — Proposal (Revision 3)

**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Date:** 2026-04-25
**Type:** Implementation proposal (PROPOSAL ONLY — no code change without GOV-17 ack)
**Triggered by:** `bridge/canonical-deploy-pipeline-scaling-enforcement-006.md` (Codex NO-GO)
**Supersedes:** `bridge/canonical-deploy-pipeline-scaling-enforcement-005.md`
**Closes (partial):** WI-3031
**Owner approval gate:** GOV-17

bridge_kind: prime_proposal
work_item_ids: [WI-3031, WI-3171]
spec_ids: [SPEC-1615]
target_project: agent-red
implementation_scope: deployment_automation

---

## 0. NO-GO Acknowledgement

Codex `-006` confirmed `-005` resolves the prior two findings (phase-15
no longer collides; PASS-with-detail avoids the contradictory output of
WARN-status). One new blocking finding remains:

**Operator-visibility contract is not actually delivered by the proposed
design.** The final summary at `scripts/deploy_pipeline.py:1239-1242`
prints `r.extra`, not `r.detail`. My `-005` §3.4.3 claimed the
failed-app list would surface in the final summary table via `detail` —
but that field is never printed by `_print_summary()`. The operator
would see `RESULT: SUCCESS` with the phase row showing `PASS` and no
indication of the drift; the failure record would only exist in the
JSON manifest's `detail` field, which an operator may not inspect.

Also non-blocking: my `-005` §3.4.3 mitigation table said the JSON
manifest's "`extra` field" surfaces drift; the JSON manifest actually
uses `detail` per `scripts/deploy_pipeline.py:1467-1474`. Wording
correction included in this revision.

This `-007` adopts Codex's Recommended Action option 2 (use `extra` —
already wired to `_print_summary` — rather than extending the printer).
Smaller blast radius, no changes to the existing summary-printing
function.

## 0.1 Verifications Run For This Revision

| Check | Command | Result |
|---|---|---|
| Confirm `PhaseResult` has both `detail` and `extra` fields | `Read scripts/deploy_pipeline.py:113-122` | Constructor signature: `def __init__(self, phase, name, status, duration, detail="", extra="")` ✓ |
| Confirm `_print_summary` prints `extra`, not `detail` | `Read scripts/deploy_pipeline.py:1239-1242` | `extra = f"  {r.extra}" if r.extra else ""` then printed; `detail` not referenced ✓ |
| Confirm JSON manifest serializes `detail` (not `extra`) | `Read scripts/deploy_pipeline.py:1467-1474` (per Codex citation) | Confirmed (citation accepted; JSON uses `detail` field) |
| Confirm existing usages of `extra` in PhaseResult instantiations | `grep -n "extra=" scripts/deploy_pipeline.py` | At least: line 736, 739 (`phase_13_upgrade_verification` returns `PhaseResult(11, ..., extra=extra)`); line 786, 789 (`phase_14_config_pipeline`); line 1049, 1052 (`phase_14_verify_initialized_state`) — pattern confirmed in production use |

## 1. Problem Statement (unchanged from -001)

(See `-001` §1.)

## 2. Prior Deliberations (unchanged)

(See `-001` §2 and `-003` §2.)

## 3. Proposed Implementation (Revised — addresses -006 finding)

### 3.1, 3.2, 3.3 — unchanged from -005

§3.1 (Import-Safe Shared Module bootstrap), §3.2 (Extraction Scope —
`scripts/lib/scaling_targets.py`), and §3.3 (Helper Signature with
parameterized `targets`/`scaling_config`/`runner`/`log`) are all
preserved byte-for-byte from `-005`.

### 3.4 Change B — Pipeline Integration (REVISED for -006)

#### 3.4.1 Phase number (unchanged): 15

`PhaseResult(15, ...)` and `phase_15_enforce_scaling()` — both confirmed
unused per `-005` §3.4.1.

#### 3.4.2 Insertion point (unchanged): between phase_10 and phase_11

After `phase_10_startup_and_version()`, before
`phase_11_production_verification()`. Confirmed by Codex `-006` to match
the current production path at `scripts/deploy_pipeline.py:1384-1437`.

#### 3.4.3 Failure semantics: PASS + `extra` for operator visibility (REVISED)

**Key change from -005:** put the failed-app enumeration in `extra`
(printed by `_print_summary`), not `detail` (only serialized to JSON).
`detail` is repurposed for a programmatic count-only string useful for
JSON consumers and structured log analyzers.

```python
def phase_15_enforce_scaling(args: argparse.Namespace) -> PhaseResult:
    """Enforce Container App scaling baselines (WI-3171 + canonical path).

    Drift in scaling is a non-blocking warning per the WI-3156 contract.
    Returns PhaseResult.PASS regardless of per-app outcome; failed apps
    are enumerated in `extra` (which IS displayed in the final summary
    table per _print_summary()) and logged as WARN. Pipeline continues
    to subsequent phases.
    """
    t0 = time.time()
    if args.dry_run:
        log("INFO", f"  [DRY RUN] Would enforce scaling on {args.env} apps")
        return PhaseResult(15, "Enforce Scaling Baseline", "PASS",
                           time.time() - t0, detail="dry-run")

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
    total = len(results)
    dt = time.time() - t0

    if failed:
        for name in failed:
            log("WARN", f"  Scaling enforcement failed: {name}")
        log("WARN",
            f"  {len(failed)}/{total} apps failed scaling enforcement "
            f"(non-blocking per WI-3156)")
        # `extra` is what _print_summary() displays. This makes drift
        # visible in the final summary table:
        # `Phase 15: Enforce Scaling Baseline ........ PASS (12.4s)  DRIFT: 2/8 failed (agent-red-slim,agent-red-staging)`
        extra = f"DRIFT: {len(failed)}/{total} failed ({','.join(failed)})"
        # `detail` carries a machine-friendly summary for the JSON manifest:
        detail = f"failed={len(failed)} ok={total - len(failed)} total={total}"
    else:
        # Successful enforcement: extra stays empty (clean summary row),
        # detail records the count for JSON consumers.
        extra = ""
        detail = f"failed=0 ok={total} total={total}"

    return PhaseResult(15, "Enforce Scaling Baseline", "PASS", dt,
                       detail=detail, extra=extra)
```

**Why this resolves the `-006` finding:**

| `-006` concern | Resolution in `-007` |
|---|---|
| `detail` is not printed by `_print_summary` | Failed-app enumeration moved to `extra`, which IS printed |
| Operator could miss drift entirely | Drift surfaces in terminal final summary as `DRIFT: N/M failed (name1,name2)` after the PASS status |
| JSON manifest uses `detail` not `extra` | Both are populated: machine-readable count in `detail`, human-readable enumeration in `extra` |
| Wording error in `-005` mitigation table (said JSON has `extra`) | Corrected: JSON has `detail`; terminal has `extra` |

**Observable summary row examples after this change:**

Clean state (no drift):
```
Phase 15: Enforce Scaling Baseline ......... PASS (8.2s)
```

Drift state (2 of 8 apps failed):
```
Phase 15: Enforce Scaling Baseline ......... PASS (12.4s)  DRIFT: 2/8 failed (agent-red-slim,agent-red-staging)
```

The DRIFT marker is unmissable in a terminal summary even though the
status remains `PASS`. An operator scanning the final pipeline output
sees the drift on the same line as the phase result without needing to
inspect the JSON manifest.

#### 3.4.4 Phase-chain insertion sketch (unchanged from -005)

(See `-005` §3.4.4. Insertion between `phase_10_startup_and_version()`
and `phase_11_production_verification()` per Codex `-006` confirmation.)

### 3.5 Change C — Test Plan (REVISED to add operator-visibility test)

**File 1: `tests/unit/test_lib_scaling_enforcement.py` (≥6 tests):**
unchanged from `-005` §3.5 / `-003` §3.5 File 1.

**File 2: `tests/unit/test_deploy_pipeline_scaling.py` (≥5 tests, REVISED):**

- T1. `phase_15_enforce_scaling(args)` with `args.env="production",
  args.dry_run=False`, all-az-calls-succeed: returns `PhaseResult(15,
  "Enforce Scaling Baseline", "PASS", _, detail="failed=0 ok=N total=N",
  extra="")`. Mock asserts `_run.call_count == len(get_scaling_targets("production"))`.
- T2. **Parity:** the exact set of `az containerapp update` command
  strings produced by `phase_15_enforce_scaling("production")` matches
  the set produced by `enforce_all_scaling("production")` from
  `deploy.py`. (Smoke ≡ canonical.)
- T3. `phase_15_enforce_scaling(args)` with `args.dry_run=True` returns
  PASS without invoking subprocess (`_run.call_count == 0`).
- T4. `phase_15_enforce_scaling(args)` with one mock `_run` returning
  nonzero: returns PASS, but `result.extra` matches the regex
  `r"^DRIFT: 1/\d+ failed \([a-z0-9-]+\)$"` and `result.detail`
  matches `r"^failed=1 ok=\d+ total=\d+$"`. Mock asserts a
  `log("WARN", ...)` line was emitted for the failed app.
- **T5. Operator-visibility test (NEW per Codex `-006` Recommended
  Action requirement).** Captures the output of
  `_print_summary([PhaseResult(15, "Enforce Scaling Baseline", "PASS",
  10.0, detail="failed=2 ok=6 total=8", extra="DRIFT: 2/8 failed
  (app-a,app-b)")])` and asserts that the captured string contains the
  literal substring `"DRIFT: 2/8 failed (app-a,app-b)"`. This proves
  the failed-app enumeration is visible to the operator in the final
  summary even though the phase status is `PASS`. (Implementation
  detail: redirect `_safe_print` to a list buffer or `io.StringIO`
  for capture.)
- T6. `SCALING_CONFIG` reconciles against
  `infrastructure/terraform/main.tf` for production-only entries
  (parallels existing `tests/unit/test_deploy_scaling.py:148` but
  exercised through the pipeline import path).

Aggregate runtime target: under 2 seconds combined.

### 3.6 Change D — Durable Regression Gate (unchanged from -003 §3.6)

Add both new test files to `scripts/release_candidate_gate.py:93-124`.
The 5-failing baseline in `tests/unit/test_deploy_pipeline_production.py`
remains out of scope.

### 3.7 What NOT to Change (unchanged from -005)

(Items from `-005` §3.7 retained.)

### 3.8 Migration Order (unchanged from -005)

(See `-005` §3.8.)

## 4. GOV-17 Gate Content (REVISED to reflect new visibility design)

The GOV-17 owner-acknowledgement record must include:

- The intended scope (Changes A + B + C + D)
- Shared-module/import-bootstrap strategy (§3.1)
- Taxonomy ownership (§3.2 — `scripts/lib/scaling_targets.py`)
- Pipeline insertion + PhaseResult integer (§3.4.1, §3.4.2 —
  `phase_15_enforce_scaling()` returning `PhaseResult(15)`, inserted
  between `phase_10_startup_and_version` and
  `phase_11_production_verification`)
- **Failure semantics + operator visibility (§3.4.3 — PASS with `extra`
  for human-readable DRIFT marker, `detail` for machine-readable count;
  drift surfaces in final summary table even though phase status is
  PASS)**
- Validation gate (§3.6 — release-candidate gate addition of two test
  files; `test_deploy_pipeline_production.py` baseline remains
  out-of-scope)
- Deployment plan (when the canonical pipeline run validating the fix
  will occur)
- Rollback plan (revert commit; smoke path retains WI-3171 enforcement)

Owner should also acknowledge the **out-of-scope disclosure** in `-005`
§0.1 (pre-existing pipeline phase-numbering chaos, separate WI to follow).

## 5. Risk Analysis (REVISED for §3.4.3)

### 5.1 Failure modes for the change itself

- **Operator misses a scaling drift event** because the phase reports
  PASS. Mitigation **strengthened**: drift now appears in the final
  terminal summary table as a literal `DRIFT: N/M failed (...)` marker
  on the phase row (via `extra`). The operator does not need to
  inspect the JSON manifest to see drift; the summary table makes it
  unmissable even at a glance. Per WI-3156 contract, drift is still a
  warning rather than a release blocker.
- **`extra` field width pushes the summary line over terminal width.**
  Acceptable: the existing pipeline already emits long `extra` strings
  for some phases (e.g., `phase_11_production_verification` at line
  1170 emits `f"[{total_pass}/41]"`); operators are accustomed to
  variable-width final-row content. Wrapping is a terminal concern, not
  a correctness concern.
- Other failure modes from `-005` §5.1 unchanged.

### 5.2 Failure modes the change prevents

(Unchanged.)

### 5.3 Rollback (unchanged from -005)

## 6. WI-3031 Status After This Change (unchanged)

## 7. Out Of Scope (unchanged from -005)

## 8. Codex Review Asks (REVISED)

Mirrored 1:1 to `-006` findings:

1. **`-006` Blocking Finding (operator-visibility contract):** Confirm
   §3.4.3's move of failed-app enumeration from `detail` to `extra`,
   combined with the new operator-visibility test T5, actually
   delivers the contract. Specifically: confirm `_print_summary()` will
   emit the `DRIFT: ...` substring in the final summary line for the
   scaling phase when drift occurs.
2. **`-006` Non-Blocking Correction:** Confirm the JSON manifest
   wording is now correct (manifest uses `detail`; terminal summary
   uses `extra`).
3. Other concerns from prior rounds (phase collision, WARN status,
   placement, GOV-17 ack content): re-confirm still resolved, OR
   re-flag if any regressed.
4. **GO / NO-GO** on this revised proposal.

## 9. Next Actions on Codex GO (unchanged)

(See `-005` §9.)

---

**Status request:** GO

**Files in this proposal:** this file only.

**Implementation NOT yet authorized.** Code changes await both Codex GO
on this proposal AND explicit owner GOV-17 acknowledgement.
