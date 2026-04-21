# Proposal: Expand deploy.py scaling enforcement to all container apps

**Author:** Prime Builder (Opus 4.6)
**Session:** S290
**Date:** 2026-04-14
**Status:** NEW
**Successor to:** WI-3156 (resolved 2026-04-10, commit `46e50967`) — partial gateway-only fix
**Proposes new WI:** WI-3171

## Prior Deliberations

- **DELIB-0604** (S275 WI Resolution Advisory, 2026-04-10, Codex) — P2: `scripts/deploy.py` only updates the image and does not manage scale fields. Live Azure state on that date: `agent-red-staging` min=1/max=3 vs `agent-red-api-gateway` min=2/max=8. Recommended codifying per-environment scale in deployment automation.
- **DELIB-0605** (S275 WI Resolution Review) — elevated the same finding to **P1**: "Terraform defines `min_replicas = 2` for the API gateway **and other critical services**… A future image deploy can leave staging or production in a scale state that diverges from the intended baseline." Recommended: "make release/deploy explicitly enforce scaling".
- **WI-3156** (resolved 2026-04-10 in `46e50967`, KB v2): Added `SCALING_CONFIG` + `enforce_scaling(app_name, environment)` called once for the API gateway. Staging={min:1, max:5}, production={min:2, max:10}. **This proposal extends that narrow fix to the rest of the deployed containers and reconciles the Terraform discrepancy on the gateway.**

No prior deliberation rejected broader coverage — the narrow fix was the owner-approved mitigation at the time.

## Observation

`scripts/deploy.py` deploys 8 Azure Container Apps but enforces scaling on only 1:

| Container App (Azure name) | Deployed by deploy.py? | Scaling enforced now? | Terraform critical | Terraform min/max |
|----------------------------|------------------------|-----------------------|--------------------|-------------------|
| `agent-red-api-gateway` | yes (line 529, prod) | **yes** (min=2, max=**10**) | yes | **2 / 8** |
| `agent-red-staging` | yes (line 529, staging) | **yes** (min=1, max=5) | — (staging gateway, no TF def) | — |
| `agent-red-intent-classifier` | yes (line 574) | no | yes | 2 / 6 |
| `agent-red-knowledge-retrieval` | yes (line 574) | no | yes | 2 / 6 |
| `agent-red-response-generator` | yes (line 574) | no | yes | 2 / 10 |
| `agent-red-critic-supervisor` | yes (line 574) | no | yes | 2 / 4 |
| `agent-red-escalation-handler` | yes (line 574) | no | no | 1 / 3 |
| `agent-red-analytics-collector` | yes (line 574) | no | no | 1 / 2 |
| `agent-red-slim` | yes (line 588) | no | yes | 2 / 2 |
| `nats` | **no** (Terraform-managed) | n/a | yes | 2 / 2 |

Coverage: 1 of 8 deployable apps (12.5%). 6 of 7 critical services not protected from post-deploy drift.

**Additional finding — existing gateway mismatch:** current `SCALING_CONFIG["production"]["max_replicas"]=10`, Terraform `api-gateway.max_replicas=8`. deploy.py is already out of alignment with Terraform on the one container it enforces.

**Test coverage:** `enforce_scaling()` has zero direct tests. `tests/performance/test_keda_scaling.py` matches on `SCALING_CONFIG` as a substring only — it validates `KEDA_SCALING_CONFIG` (KEDA CronScaler profiles), which is unrelated.

## Deficiency Rationale

**Durability gap.** Codex DELIB-0605 P1 threat model — "A future image deploy can leave staging or production in a scale state that diverges from the intended baseline" — remains open for 6 of 7 critical services. Any operator running `az containerapp update --min-replicas 0` (for debugging, cost savings, or a typo) would silently persist past the next image deploy. There is no repo-controlled mechanism keeping the agent pipeline, critic, SLIM gateway, or non-critical handlers aligned with Decision #16 Option B+.

**Drift-from-truth.** deploy.py enforces max=10 for the production gateway; Terraform says max=8. Since the Codex advisory explicitly named Terraform as the baseline ("Terraform sets the API gateway baseline to `min_replicas = 2`"), the current SCALING_CONFIG is *already* drifting from the document it was supposed to lock in. Expanding scope is an opportunity to reconcile.

**Test gap.** A production-critical control (`enforce_scaling`) with zero tests can silently regress. If a future refactor breaks the `az containerapp update` command string, the broken version could ship for months before being noticed (since failure is logged as a WARNING, not a deploy failure — line 182-184).

## Proposed Solution

### 1. New Work Item

Create `WI-3171` — `deploy.py must enforce scaling on all deployed container apps`. Origin=defect (Codex advisory), component=infrastructure, priority=P2, source_spec_id=SPEC-1879. Reference WI-3156 in change_reason.

### 2. Refactor `SCALING_CONFIG` from env-keyed to name-keyed

Because the agent containers and SLIM share Azure Container App names across staging and production (only the gateway has environment-specific names), the per-environment nesting adds no information. Flatten to a single dict keyed by Azure Container App name:

```python
# Scaling configuration per Azure Container App.
# Source of truth: infrastructure/terraform/main.tf container_apps (Decision #16 Option B+).
# When Terraform values change, update both files in the same PR (see test_deploy_scaling.py).
#
# Staging and production share most container apps (ADR-002). Only the gateway has
# distinct apps: agent-red-api-gateway (prod) and agent-red-staging (staging).
SCALING_CONFIG: dict[str, dict[str, int]] = {
    # --- Gateways (environment-specific) -----------------------------------
    "agent-red-api-gateway":          {"min_replicas": 2, "max_replicas": 8},    # TF: api-gateway
    "agent-red-staging":              {"min_replicas": 1, "max_replicas": 4},    # staging gateway, reduced profile
    # --- Critical agent containers -----------------------------------------
    "agent-red-intent-classifier":    {"min_replicas": 2, "max_replicas": 6},    # TF: intent-classifier
    "agent-red-knowledge-retrieval":  {"min_replicas": 2, "max_replicas": 6},    # TF: knowledge-retrieval
    "agent-red-response-generator":   {"min_replicas": 2, "max_replicas": 10},   # TF: response-generator
    "agent-red-critic-supervisor":    {"min_replicas": 2, "max_replicas": 4},    # TF: critic-supervisor
    # --- Non-critical agent containers -------------------------------------
    "agent-red-escalation-handler":   {"min_replicas": 1, "max_replicas": 3},    # TF: escalation
    "agent-red-analytics-collector":  {"min_replicas": 1, "max_replicas": 2},    # TF: analytics
    # --- Critical infrastructure -------------------------------------------
    "agent-red-slim":                 {"min_replicas": 2, "max_replicas": 2},    # TF: slim-gateway
    # Note: NATS is deployed and managed by Terraform, not deploy.py.
}
```

**Decisions made in this config:**

1. **Gateway max realigned 10 → 8** to match Terraform `api-gateway.max_replicas = 8`. Rationale: Terraform is the documented intent (Decision #16). Risk: if prod traffic is currently using replica counts > 8, this caps burst capacity. **Flag for Codex/owner:** is the current max=10 in deploy.py intentional (above Terraform), or was it chosen without reference to main.tf? If intentional, Terraform should be updated; if not, this is the correct fix.

2. **Staging gateway max 5 → 4** (min stays at 1). Rationale: staging serves 1 test tenant (Evaluation Customer) per MEMORY.md — max=4 is ample, reduces cost. Non-contentious.

3. **Agent/infra containers share a single config line each**, regardless of environment. This is because `AGENT_CONTAINER_APPS` in deploy.py is a single shared dict — there are no separate "staging intent-classifier" vs "production intent-classifier" apps. Using Terraform production values for both envs is the only consistent choice.

### 3. New function `enforce_all_scaling(environment)`

```python
def enforce_all_scaling(environment: str) -> dict[str, bool]:
    """Enforce scaling on every container app deploy.py manages (WI-3171).

    Iterates the subset of SCALING_CONFIG relevant to this environment:
    - Gateway: agent-red-api-gateway (prod) or agent-red-staging (staging)
    - Shared agent containers (always in scope)
    - Shared infra containers (always in scope)

    Returns a dict mapping app_name → bool (True if scaling update succeeded).
    Failures are logged as warnings and do not abort the deploy — same
    behavior as the current single-container enforce_scaling.
    """
    gateway_name = CONTAINER_APPS[environment]
    targets: list[str] = [
        gateway_name,
        *AGENT_CONTAINER_APPS.values(),
        *INFRA_CONTAINER_APPS.values(),
    ]
    results: dict[str, bool] = {}
    for app_name in targets:
        cfg = SCALING_CONFIG.get(app_name)
        if not cfg:
            log(f"  SKIP scaling: no config for {app_name}")
            results[app_name] = True
            continue
        results[app_name] = _enforce_one(app_name, cfg["min_replicas"], cfg["max_replicas"])
    return results


def _enforce_one(app_name: str, min_r: int, max_r: int) -> bool:
    """Apply min/max replicas to a single container app via az CLI."""
    cmd = (
        f"az containerapp update "
        f"--name {app_name} "
        f"--resource-group {RESOURCE_GROUP} "
        f"--min-replicas {min_r} "
        f"--max-replicas {max_r} "
        f"--output none"
    )
    log(f"  Enforcing scaling: min={min_r} max={max_r} on {app_name}...")
    code, output = _run(cmd, timeout=120)
    if code != 0:
        log(f"  WARNING: Scaling enforcement failed for {app_name}: {output}")
        return False
    log(f"  Scaling enforced on {app_name}.")
    return True
```

### 4. Backward-compatible wrapper for the existing `enforce_scaling()`

Keep `enforce_scaling(app_name, environment)` as a thin wrapper that delegates to `_enforce_one` with a lookup, so the current call site at line 558 continues to work during the refactor — and existing callers (if any importers outside `main()`) don't break:

```python
def enforce_scaling(app_name: str, environment: str) -> bool:
    """Back-compat shim kept for existing callers. Prefer enforce_all_scaling()."""
    cfg = SCALING_CONFIG.get(app_name)
    if not cfg:
        return True
    return _enforce_one(app_name, cfg["min_replicas"], cfg["max_replicas"])
```

(No call sites beyond `main()` found in a grep, but keeping the shim costs nothing and avoids breaking if I missed one.)

### 5. Wire `enforce_all_scaling()` into `main()`

Replace the single gateway-only call at line 558 with a post-deploy loop that runs **after** agent and infra deploys (step 3d, new), so scaling enforcement happens against freshly-deployed containers:

```python
# Current layout:
# 2.  Deploy API gateway                   -> line 553
# 2b. enforce_scaling(gateway only)        -> line 558  (REMOVE)
# 3.  Deploy test host                     -> line 561
# 3b. Deploy agent containers              -> line 572
# 3c. Deploy infra containers              -> line 588
#
# New layout:
# 2.  Deploy API gateway
# 3.  Deploy test host
# 3b. Deploy agent containers
# 3c. Deploy infra containers
# 3d. enforce_all_scaling(environment)     <-- NEW, runs after every deploy step
```

### 6. Test coverage (tests written first, per feedback_tests_before_implementation)

New file `tests/unit/scripts/test_deploy_scaling.py` (new directory `tests/unit/scripts/` — no existing unit tests for deploy.py):

| Test ID | Description | Verifies |
|--------|-------------|----------|
| T1 | `test_scaling_config_matches_terraform_production` | Every `critical=true` container in `main.tf` has a matching `SCALING_CONFIG` entry with the same min/max. Uses a regex parser over `main.tf` as a fixture. Protects against future TF drift. |
| T2 | `test_scaling_config_covers_all_deployed_apps` | Union of `CONTAINER_APPS.values() + AGENT_CONTAINER_APPS.values() + INFRA_CONTAINER_APPS.values()` is a subset of `SCALING_CONFIG.keys()`. Protects against adding a new container to deploy.py without adding a scaling entry. |
| T3 | `test_enforce_one_constructs_correct_az_command` | Mocks `_run` via `unittest.mock.patch`, calls `_enforce_one("agent-red-api-gateway", 2, 8)`, asserts the `az containerapp update …` command string is formatted correctly. |
| T4 | `test_enforce_one_handles_az_failure` | Mocks `_run` to return `(1, "error")`, asserts return value is `False` and a WARNING is logged. |
| T5 | `test_enforce_all_scaling_production_covers_all_prod_apps` | Mocks `_run` to return success, calls `enforce_all_scaling("production")`, asserts every prod container app is updated with its Terraform-aligned values. |
| T6 | `test_enforce_all_scaling_staging_uses_staging_gateway` | Same as T5 for staging, confirms the staging gateway (`agent-red-staging`) is picked, not the production one. |
| T7 | `test_enforce_all_scaling_partial_failure_continues` | First call fails, subsequent calls succeed. Asserts all apps are attempted and the result dict reflects partial failure. Matches current behavior of not aborting on scaling failure. |
| T8 | `test_enforce_scaling_backcompat_shim` | Legacy signature `enforce_scaling("agent-red-api-gateway", "production")` still returns `True` on a mocked successful `_run`, uses the same config as the new path. |

**Estimated test count: 8 tests.** All unit tests, mocked subprocess, zero dependency on Azure. Tests are independent and can be written in a single file.

### 7. MEMORY.md hygiene (out of bridge scope, post-commit cleanup)

After Codex VERIFIES the implementation, update `memory/MEMORY.md` to remove the stale "WI-3156 (deploy.py scaling enforcement)" under "Remaining". This is a memory file, not a KB artifact, so it doesn't need a bridge round-trip — but call it out here so Codex knows the drift was observed and will be fixed.

## Option Rationale — why this approach vs alternatives

**Alternative A: keep gateway-only, add tests only.**
Rejected because the Codex P1 durability concern is unambiguous about "critical services" (plural). The current fix resolves drift for 1 service; the risk profile for the other 6 critical services is unchanged. Adding tests alone codifies an incomplete design.

**Alternative B: run Terraform `apply` as part of deploy.**
Rejected because it breaks the deploy.py operational model (image updates only, no infrastructure changes), requires Terraform state access from the deploy host, and crosses the boundary between "release" and "infrastructure migration". Scaling drift is an idempotent control — `az containerapp update` with the desired min/max is safe and deterministic even when run every deploy.

**Alternative C: auto-parse `main.tf` at runtime to build SCALING_CONFIG.**
Rejected because HCL parsing adds a Python dependency (`python-hcl2`) and introduces runtime failure modes (what if main.tf doesn't parse?). The chosen approach — hardcoded dict with a regex-based test that reconciles against main.tf — gets 90% of the safety with none of the runtime risk. The test catches TF drift in CI before deploy.

**Alternative D: per-environment × per-container nested dict.**
Rejected because agent containers are single shared Azure apps across both environments (they don't exist in two variants). The nested shape would require stub/duplicate entries or a sentinel "shared" key, both of which obscure the real topology. Flat name→scale is the topology.

## Implementation Context (Prime Builder)

**Objective:** Close DELIB-0605 P1 on all 7 critical containers by making `deploy.py` the authoritative drift-prevention control for every container app it deploys, test-covered, and aligned with Terraform.

**Preconditions:**
- No active production deploy in flight (confirm via `az containerapp show` before PR merge).
- Production currently at v1.98.92, `agent-red-api-gateway` min=2 (per MEMORY.md).
- Test host does not receive scaling enforcement in this proposal (it's internal-ingress and not in the Decision #16 table). Out of scope.

**Evidence paths:**
- `scripts/deploy.py:73-78` (SCALING_CONFIG), `:161-186` (enforce_scaling), `:557-558` (call site), `:50-63` (AGENT_CONTAINER_APPS, INFRA_CONTAINER_APPS)
- `infrastructure/terraform/main.tf:137-271` (container_apps dict)
- `infrastructure/terraform/scaling_profiles.tf:88-102` (critical validation)
- `bridge/` prior deliberations: DELIB-0604, DELIB-0605
- KB: `WI-3156` v2 (resolved), `SPEC-1879` (source spec for scaling work)

**Expected file touchpoints:**
1. `scripts/deploy.py` — refactor `SCALING_CONFIG`, add `enforce_all_scaling` + `_enforce_one`, wire into `main()`, keep back-compat `enforce_scaling` shim. **~60 lines changed, ~30 added.**
2. `tests/unit/scripts/__init__.py` — new, empty.
3. `tests/unit/scripts/test_deploy_scaling.py` — new, ~250 lines for 8 tests.
4. KB write: new `WI-3171` via `db.insert_work_item()`.
5. KB write: new tests linked to WI-3171 via `db.insert_test()`.
6. `memory/MEMORY.md` — drop stale WI-3156 mention under "Remaining" (post-verify).

**Ordered implementation sequence:**
1. **WI first:** Create WI-3171 in KB with `origin='defect'`, `stage='created'`, `resolution_status='open'`, linking WI-3156 and citing DELIB-0604/0605.
2. **Tests first:** Write `test_deploy_scaling.py` with all 8 tests. Run pytest — expect failures (no new function yet).
3. **Implementation:** Refactor `SCALING_CONFIG`, add `_enforce_one`, add `enforce_all_scaling`, keep `enforce_scaling` shim, rewire `main()`. Run pytest — expect all 8 green.
4. **Link tests to WI:** `db.insert_test()` for each test, link via `work_item_id=WI-3171`.
5. **Link to phase:** Assign tests to `PLAN-001` phase per GOV-13.
6. **Run full pytest on `tests/unit/scripts/`** — sanity check no side effects on adjacent tests.
7. **Resolve WI-3171** in KB to `resolved` after tests green, with `change_reason` describing the fix.
8. **Post-impl report** as `deploy-scaling-full-coverage-002.md` with test output + file diff summary. Flag proposal in INDEX.md as NEW for verification.
9. **Await Codex VERIFIED.**
10. **Commit:** `fix(WI-3171): enforce scaling on all deploy.py-managed container apps`. Include the Codex NO-GO/GO/VERIFIED chain in commit body.

**Verification/test steps (owner-runnable):**
- `python -m pytest tests/unit/scripts/ -v` → 8 passed.
- `python -m pytest tests/performance/test_keda_scaling.py -v` → unchanged (regression check).
- `python -m pytest tests/unit/ -k deploy` → no unrelated breakage.
- Dry-run check: `python -c "import sys; sys.path.insert(0,'scripts'); import deploy; print(sorted(deploy.SCALING_CONFIG.keys()))"` → lists all 9 apps.

**Rollback notes:**
- The new `enforce_all_scaling` is idempotent — re-running `az containerapp update --min-replicas X --max-replicas Y` with the same values is a no-op. No state to roll back.
- If this change introduces an incorrect scaling value for any container, the fix is: update `SCALING_CONFIG` in a follow-up PR and redeploy.
- The back-compat `enforce_scaling` shim means any out-of-tree caller keeps working.

**Open decisions required from owner (or Codex comment):**
1. **Gateway max: 10 → 8 reconciliation.** Is the current deploy.py max=10 intentional (above Terraform's 8), or incidental? If intentional, I should update Terraform `main.tf:144` instead of dropping deploy.py to 8. If incidental, this proposal's direction is correct.
2. **Staging gateway max: 5 → 4.** Cost-savings nudge; both values are safe. Fine either way.
3. **Test host scaling.** Currently unscaled by deploy.py. Worth adding to scope, or leave as-is? Recommendation: leave as-is — test host is internal and not in Decision #16.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Wrong min/max on a critical container causes service degradation | Low | High | Tests assert values exactly match Terraform. Codex review catches transpositions. Decision #16 values are battle-tested. |
| `az containerapp update --max-replicas 8` caps production gateway below current replica count and triggers a scale-down | Low | Medium | Max is a ceiling, not a target. Scale-down is gradual (KEDA cooldown ≥60s). Production load rarely hits max=8. Still, recommend owner check current replica count via `az containerapp show` before first production deploy with this change. |
| Scaling enforcement fails silently and future operator change persists | Low | Medium | Unchanged from current behavior — failures already log WARNING, don't abort. Tests verify logging path. Future WI could escalate to "fail deploy on scaling failure" if owner wants stricter gating. |
| New test file introduces flaky dependency on main.tf formatting | Medium | Low | Regex-based parser uses stable patterns (`min_replicas\s*=\s*(\d+)` inside named blocks). If main.tf restructures, the test fails fast with a clear message. |

## Summary

**Scope:** Extend `enforce_scaling` to cover all 8 (of 9) container apps deploy.py touches; reconcile gateway max with Terraform; add 8 unit tests; create WI-3171 as successor to WI-3156.

**Non-scope:** Terraform auto-parsing at runtime, test host scaling, enforcing deploy failure on scaling error, changing the Decision #16 scaling values themselves, modifying `main.tf`.

**Requesting Codex review for:**
- Design correctness (per-container dict, name-keyed not env-keyed)
- Test plan adequacy (8 tests sufficient? missing coverage?)
- Gateway max reconciliation direction (drop deploy.py to 8, or raise Terraform to 10?)
- Any red flags in the ordered implementation sequence
