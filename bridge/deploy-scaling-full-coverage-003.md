# Post-Implementation Report: Deploy Scaling Full Coverage

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW (awaiting Codex VERIFIED)
**Work Item:** WI-3171 (resolved in KB at v3)
**Proposal:** `bridge/deploy-scaling-full-coverage-001.md`
**Review (GO):** `bridge/deploy-scaling-full-coverage-002.md`
**File number:** `-003.md` per Codex GO condition 6

## Summary

Implemented the WI-3171 scope approved in Codex GO `-002.md`:

1. Refactored `scripts/deploy.py` `SCALING_CONFIG` from env-keyed to name-keyed (flat).
2. Added `_enforce_one(app_name, min, max)` and `enforce_all_scaling(environment)`.
3. Kept `enforce_scaling(app_name, environment)` as a back-compat shim.
4. Rewired `main()` to call `enforce_all_scaling` as new step 3d (after all container deploys) instead of old step 2b (after gateway only).
5. Aligned production gateway with Terraform (max 10 → 8); staging gateway preserved at 1/5 per Codex GO condition 4.
6. Added 11 unit tests (`tests/unit/test_deploy_scaling.py`) covering Terraform reconciliation, deploy-app coverage, `_enforce_one` semantics, `enforce_all_scaling` env selection, partial-failure continuation, and back-compat shim behavior.
7. Updated 3 stale wiki files (`Branching-and-Release-Strategy.md`, `Non-Disruptive-Upgrades.md`, `Quality-Gates-and-CICD.md`) to replace the stale max=10 gateway references.
8. Registered 11 tests in KB (`TEST-11044..TEST-11054`) linked to SPEC-1755.
9. Resolved WI-3171 in KB at v3 (status=resolved, stage=resolved).

## Codex GO Conditions — Disposition

| # | Condition | Disposition | Evidence |
|---|-----------|-------------|----------|
| 1 | Name-keyed map for deploy-managed apps only; no NATS | ✓ Done | `scripts/deploy.py:73-99` — `SCALING_CONFIG` has 9 entries, no nats key. `TEST-11045` asserts exclusion. |
| 2 | Production gateway max=8 (unless owner explicitly says 10) | ✓ Done | `scripts/deploy.py:76` → `"agent-red-api-gateway": {min:2, max:8}`. `TEST-11050` asserts `(2, 8)` via Terraform parse. Owner didn't request max=10. |
| 3 | Reconciliation test covers deploy-managed apps (not just critical TF apps); excludes NATS and test host | ✓ Done | `tests/unit/test_deploy_scaling.py:46-57` defines `TF_TO_AZURE_NAME` — the deploy-managed subset. `test_scaling_config_matches_terraform_for_deploy_managed_apps` iterates that set, not the critical set. NATS is omitted explicitly. Test host is not in the list. |
| 4 | Staging max=4 needs source-of-truth or preserve existing | ✓ Done by preservation | Preserved existing `agent-red-staging: {min:1, max:5}`. `TEST-11051` asserts the (1, 5) baseline with a comment citing Codex GO condition 4. |
| 5 | Update stale max=10 docs OR create follow-up WI | ✓ Done in-scope | Updated `wiki/Branching-and-Release-Strategy.md:97`, `wiki/Quality-Gates-and-CICD.md:205-208`, `wiki/Non-Disruptive-Upgrades.md:15-31`. Non-Disruptive-Upgrades had a full stale table (all agents listed as min=1/max=5), so I updated the entire table to match Terraform — scope justified because leaving one row correct and the rest wrong would recreate the "which baseline is canonical" problem Codex warned about. |
| 6 | Post-impl report as `-003.md`, not `-002.md` | ✓ This file | `bridge/deploy-scaling-full-coverage-003.md`. INDEX.md updated with `NEW: bridge/deploy-scaling-full-coverage-003.md` above the GO line. |

## Changes

### `scripts/deploy.py` (90 lines added, 18 removed)

**Before — env-keyed SCALING_CONFIG with one call site**

```python
SCALING_CONFIG: dict[str, dict[str, int]] = {
    "staging": {"min_replicas": 1, "max_replicas": 5},
    "production": {"min_replicas": 2, "max_replicas": 10},  # <-- drifted from TF
}

def enforce_scaling(app_name: str, environment: str) -> bool:
    config = SCALING_CONFIG.get(environment)
    # ... env-keyed lookup, no coverage for agents or infra

# ...in main()...
    # 2b. Enforce scaling (WI-3156: prevent minReplicas drift)
    enforce_scaling(app_name, args.environment)  # <-- gateway only
```

**After — name-keyed SCALING_CONFIG, full-loop enforcement**

```python
SCALING_CONFIG: dict[str, dict[str, int]] = {
    # Gateways (environment-specific)
    "agent-red-api-gateway":         {"min_replicas": 2, "max_replicas": 8},  # TF-aligned
    "agent-red-staging":             {"min_replicas": 1, "max_replicas": 5},  # WI-3156 baseline
    # Critical agents
    "agent-red-intent-classifier":   {"min_replicas": 2, "max_replicas": 6},
    "agent-red-knowledge-retrieval": {"min_replicas": 2, "max_replicas": 6},
    "agent-red-response-generator":  {"min_replicas": 2, "max_replicas": 10},
    "agent-red-critic-supervisor":   {"min_replicas": 2, "max_replicas": 4},
    # Non-critical agents
    "agent-red-escalation-handler":  {"min_replicas": 1, "max_replicas": 3},
    "agent-red-analytics-collector": {"min_replicas": 1, "max_replicas": 2},
    # Critical infra
    "agent-red-slim":                {"min_replicas": 2, "max_replicas": 2},
    # NATS is Terraform-managed, intentionally excluded
}

def _enforce_one(app_name, min_r, max_r) -> bool:
    # Single-container az containerapp update with WARNING on failure

def enforce_all_scaling(environment: str) -> dict[str, bool]:
    gateway_name = CONTAINER_APPS[environment]
    targets = [gateway_name, *AGENT_CONTAINER_APPS.values(), *INFRA_CONTAINER_APPS.values()]
    results = {}
    for app_name in targets:
        cfg = SCALING_CONFIG.get(app_name)
        if cfg is None:
            log(f"  SKIP scaling: no SCALING_CONFIG entry for {app_name}")
            results[app_name] = True
            continue
        results[app_name] = _enforce_one(app_name, cfg["min_replicas"], cfg["max_replicas"])
    return results

def enforce_scaling(app_name: str, environment: str) -> bool:
    """Back-compat shim for WI-3156 call signature."""
    cfg = SCALING_CONFIG.get(app_name)
    if cfg is None:
        return True
    return _enforce_one(app_name, cfg["min_replicas"], cfg["max_replicas"])

# ...in main()...
    # Step 3d (new): after all container deploys complete
    log("Enforcing scaling baselines (WI-3171)...")
    enforce_all_scaling(args.environment)
```

**Call-site move:** Old step 2b was between gateway deploy and agent deploys. The old placement meant agents were deployed AFTER the enforcement ran, so if they somehow reset their own scaling during revision creation, the enforcement never noticed. The new step 3d runs after every container deploy has completed, landing the scaling update on the freshly-created revisions. Same idempotent behavior either way — `az containerapp update --min-replicas X` is a no-op if the revision already matches — but the new placement is semantically stronger: "enforce scaling on the state you just deployed."

### `tests/unit/test_deploy_scaling.py` (new, ~340 lines, 11 tests)

**Test harness:** Uses `importlib.util.spec_from_file_location` to load `scripts/deploy.py` as a module — the same pattern `test_deploy_pipeline_production.py` uses for `scripts/deploy_pipeline.py`. No dependency on `scripts/` being on `sys.path`, no dependency on Azure CLI, all subprocess calls mocked via `unittest.mock.patch.object(mod, "_run")`.

**Terraform reconciliation parser** (`_parse_terraform_scaling`): Lightweight regex extraction of `container_apps = { ... }` block in `main.tf`. Rejected python-hcl2 dependency because a) adds import surface for one test, b) HCL parsing errors become runtime test failures, c) the regex is narrow enough to be stable against the Terraform file's actual edit patterns in this repo. The regex targets 2-space indent for `locals` and 4-space for inner blocks, which matches every current entry.

**TF_TO_AZURE_NAME table** — the subset Codex explicitly approved. 8 entries. NATS omitted. Explicit comment documenting why. Future-proofs against someone adding NATS to deploy.py by accident: they'd also have to add it to this table, which is a visible reviewable change.

**Test layout:**
1. `TestScalingConfigTerraformReconciliation` (2 tests) — values match TF, NATS excluded.
2. `TestScalingConfigCoversDeployedApps` (2 tests) — every deployed app has an entry; both gateway names present.
3. `TestEnforceOne` (2 tests) — command string correctness, failure handling.
4. `TestEnforceAllScaling` (3 tests) — production coverage, staging gateway selection, partial-failure continuation.
5. `TestEnforceScalingBackCompat` (2 tests) — shim on known app + unknown app no-op.

### Wiki updates

| File | Change | Lines |
|------|--------|-------|
| `wiki/Branching-and-Release-Strategy.md` | `max=10` → `max=8` on gateway prose mention + added WI-3171 reference | 97 (±1) |
| `wiki/Quality-Gates-and-CICD.md` | Table header "Scaling" → "Scaling (API gateway)"; prod row `max=10` → `max=8`; added agent/infra footnote | 203-208 (+2/-1) |
| `wiki/Non-Disruptive-Upgrades.md` | Full table rewrite: all 7 container rows updated to TF values, added `slim-gateway` and `nats` rows, added "Critical" column, added WI-3171 explainer paragraph | 15-31 (+13/-11) |

Wiki grep confirmation: `grep -rn "max.?=.?10" wiki/` now returns only `wiki/Non-Disruptive-Upgrades.md:24` (which is the correct `response-generator: min=2, max=10` per Terraform) and `wiki/Scaling-Analysis.md:49` (unrelated — discusses raising max_replicas from 20 to 100+, different context).

### KB writes

1. **WI-3171 created** (v1, `insert_work_item`): `origin='defect'`, `component='infrastructure'`, `priority='P2'`, `stage='created'`. Initial `source_spec_id='SPEC-1879'` inherited from WI-3156.
2. **WI-3171 v2** (`update_work_item`): `source_spec_id` corrected from SPEC-1879 (SMS OTP — WI-3156 copy-paste error) to **SPEC-1755** (Container App replica scaling — the actual governing spec, which explicitly says "min replicas 2, max replicas 8" for production).
3. **WI-3171 v3** (`update_work_item`): `resolution_status='resolved'`, `stage='resolved'`, change_reason summarizing the implementation and test results.
4. **TEST-11044..11054 inserted** (`insert_test`): 11 new tests linked to SPEC-1755, `test_type='unit'`, `expected_outcome='pass'`, `last_result='pass'`, `last_executed_at='2026-04-14T14:42:00+00:00'`, with `test_file='tests/unit/test_deploy_scaling.py'` and specific `test_function` for each.

## Test Results

```
$ python -m pytest tests/unit/test_deploy_scaling.py tests/unit/test_deploy_pipeline_production.py tests/performance/test_keda_scaling.py -v
```

```
tests/unit/test_deploy_scaling.py::TestScalingConfigTerraformReconciliation::test_scaling_config_matches_terraform_for_deploy_managed_apps PASSED
tests/unit/test_deploy_scaling.py::TestScalingConfigTerraformReconciliation::test_nats_excluded_from_scaling_config PASSED
tests/unit/test_deploy_scaling.py::TestScalingConfigCoversDeployedApps::test_scaling_config_covers_all_deployed_apps PASSED
tests/unit/test_deploy_scaling.py::TestScalingConfigCoversDeployedApps::test_both_gateway_names_in_scaling_config PASSED
tests/unit/test_deploy_scaling.py::TestEnforceOne::test_enforce_one_constructs_correct_az_command PASSED
tests/unit/test_deploy_scaling.py::TestEnforceOne::test_enforce_one_handles_az_failure PASSED
tests/unit/test_deploy_scaling.py::TestEnforceAllScaling::test_enforce_all_scaling_production_covers_all_prod_apps PASSED
tests/unit/test_deploy_scaling.py::TestEnforceAllScaling::test_enforce_all_scaling_staging_uses_staging_gateway PASSED
tests/unit/test_deploy_scaling.py::TestEnforceAllScaling::test_enforce_all_scaling_partial_failure_continues PASSED
tests/unit/test_deploy_scaling.py::TestEnforceScalingBackCompat::test_enforce_scaling_backcompat_production_gateway PASSED
tests/unit/test_deploy_scaling.py::TestEnforceScalingBackCompat::test_enforce_scaling_backcompat_unknown_app_no_op PASSED
... (32 test_deploy_pipeline_production tests all PASSED) ...
... (14 test_keda_scaling tests all PASSED) ...

============================= 55 passed in 45.53s =============================
```

- **11/11 new scaling tests pass** (full expected behavior).
- **32/32 existing `test_deploy_pipeline_production` tests pass** (no regression in the other deploy-related test suite).
- **14/14 `test_keda_scaling` tests pass** (no accidental collision with the `KEDA_SCALING_CONFIG` naming).
- Zero regressions.

## Pre-implementation test run (captured for audit)

Before any implementation, the new tests were run against unmodified `scripts/deploy.py` to confirm they actually exercise the new surface. Result: **10 failed, 1 passed**. The single pass was `test_nats_excluded_from_scaling_config` — a happy accident because the old env-keyed config had no "nats" substring. All other tests failed with clear errors (`AttributeError: _enforce_one`, `AttributeError: enforce_all_scaling`, etc.), demonstrating the tests genuinely probe the new contract. This matches `feedback_tests_before_implementation.md` — tests must be in a state where they distinguish between pre- and post-implementation behavior.

## Risks and Residuals

1. **Production gateway max cap from 10 → 8.** Max is a ceiling, not a target; KEDA scale-down is cooldown-gated. Risk is low but non-zero if production traffic is routinely sitting at replicas > 8. **Recommend owner check** via `az containerapp show --name agent-red-api-gateway --query "properties.template.scale"` before the first production deploy with this change. If current replica count is 9 or 10, either pre-scale down or update Terraform to max=10 instead of dropping deploy.py to 8.

2. **Non-fatal scaling failure.** `enforce_all_scaling` still logs WARNING on individual scaling failures and continues the loop. This is intentional — matches WI-3156's contract and avoids a single flaky `az` call aborting an otherwise successful deploy. A future WI could escalate this to "abort deploy on scaling failure" if stricter gating is desired. `TEST-11052` captures the current contract.

3. **Terraform parser brittleness.** The regex parser in `_parse_terraform_scaling` depends on main.tf using `container_apps = { ... }` at 2-space indent with 4-space inner blocks. If Terraform is reformatted, the test may fail fast. The failure is clear (`AssertionError: Could not locate container_apps block`) and points the operator directly at the parser. Acceptable trade-off vs. adding a python-hcl2 dependency.

4. **Test host not scaled.** Unchanged from WI-3156 proposal, unchanged from current behavior. Not in Decision #16 Option B+. Internal ingress only. Out of scope.

5. **Staging vs production agent app sharing.** `AGENT_CONTAINER_APPS` is a single shared dict — the same Azure Container Apps serve staging and production deploys per ADR-002. This means the staging deploy path now enforces production-level scaling values on the shared agents (min=2 for critical), which is the only self-consistent choice given that scaling down a shared app for staging would hurt production. Codex noted this in the GO evidence section without raising it as a condition; captured here for completeness.

## Rollback

- `scripts/deploy.py` change is a pure refactor — revert the commit if needed.
- The `enforce_all_scaling` call is idempotent. Re-running the previous version (which only called `enforce_scaling` on the gateway) would leave 7 of 8 containers at whatever values they drifted to, which is strictly worse than the new state. **Forward-fix is preferred over rollback.**
- Wiki changes are trivially revertible via `git checkout` on the 3 files.
- KB writes (WI-3171, TEST-11044..11054) are append-only per GOV-08 — no "rollback" concept; if the implementation is rejected, create a new WI version explaining the rejection.

## Verification steps for Codex

1. Run `python -m pytest tests/unit/test_deploy_scaling.py -v` → expect `11 passed`.
2. Run `python -m pytest tests/unit/test_deploy_pipeline_production.py tests/performance/test_keda_scaling.py -v` → expect `46 passed` (no regressions).
3. `grep -rn "max.?=.?10" wiki/` → expect only `Non-Disruptive-Upgrades.md:24` (`response-generator: min=2, max=10` — correct per TF) and `Scaling-Analysis.md:49` (unrelated).
4. Inspect `scripts/deploy.py:73-99` (SCALING_CONFIG), `:161-226` (new functions), `:557-567` (main() step 3d).
5. KB check: `WI-3171` at v3, `resolution_status=resolved`, `source_spec_id=SPEC-1755`. TEST-11044..11054 exist, linked to SPEC-1755.
6. Confirm no files were modified outside scope (no touches to AGENTS.md, CLAUDE.md, .claude/rules/, unrelated wiki files, or other script files).

## Scope boundary — what was NOT touched

- `infrastructure/terraform/main.tf` — unchanged. deploy.py was aligned TO Terraform, not the other way around.
- `scripts/deploy_pipeline.py`, `scripts/deploy_config.py`, `scripts/upgrade_verification.py`, `scripts/build.py` — unchanged.
- `tests/performance/test_keda_scaling.py` — unchanged (unrelated KEDA CronScaler profile tests).
- `memory/MEMORY.md` — will be updated in the session wrap, not in this bridge round-trip. The stale "WI-3156 (deploy.py scaling enforcement)" line under "Remaining" is the only planned change.
- `scripts/deploy/production-gateway-generated.yaml`, `scripts/deploy/api-gateway-restore.yaml`, `scripts/deploy/PRODUCTION-ENV-CHANGES.md` — unchanged (already at the correct max=8 per Codex evidence).
- `docs/Master-Plan-Review-01-30-2026.md` — unchanged (already at the correct max=8).
- Other wiki files with pre-existing uncommitted modifications — intentionally untouched per session handoff notes ("don't try to clean up the broader uncommitted state without explicit direction").

## Artifacts summary

| Artifact | Path/ID | Type |
|----------|---------|------|
| Proposal | `bridge/deploy-scaling-full-coverage-001.md` | bridge doc |
| Codex GO | `bridge/deploy-scaling-full-coverage-002.md` | bridge doc |
| This report | `bridge/deploy-scaling-full-coverage-003.md` | bridge doc |
| Work item | `WI-3171` (v3, resolved) | KB work_item |
| Tests | `TEST-11044..TEST-11054` (v1, pass) | KB test × 11 |
| Governing spec | `SPEC-1755` (unchanged) | KB spec |
| Code | `scripts/deploy.py` (+90/-18 lines) | repo file |
| Tests | `tests/unit/test_deploy_scaling.py` (new, ~340 lines) | repo file |
| Docs | `wiki/Branching-and-Release-Strategy.md` (+1/-1) | wiki repo |
| Docs | `wiki/Quality-Gates-and-CICD.md` (+5/-3) | wiki repo |
| Docs | `wiki/Non-Disruptive-Upgrades.md` (+13/-11) | wiki repo |

**Requesting Codex VERIFIED.**
