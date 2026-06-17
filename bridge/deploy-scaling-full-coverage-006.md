VERIFIED

# Codex Verification: Deploy Scaling Full Coverage

Verdict: VERIFIED

Date: 2026-04-14
Reviewer: Codex Loyal Opposition
Reviewed revision: `bridge/deploy-scaling-full-coverage-005.md`
Prior NO-GO: `bridge/deploy-scaling-full-coverage-004.md`

## Claim

The revised implementation satisfies the prior GO conditions and resolves the single blocking NO-GO from `-004.md`. The remaining `max=10` hit in the deployment-doc grep is the expected `response-generator` baseline, not a stale production API gateway reference.

## Evidence Reviewed

- Full bridge entry and version chain: `bridge/deploy-scaling-full-coverage-001.md` through `bridge/deploy-scaling-full-coverage-005.md`.
- `scripts/deploy.py:85-99` uses a name-keyed `SCALING_CONFIG`, sets production API gateway to `min=2, max=8`, preserves staging gateway at `min=1, max=5`, covers deployed agents and SLIM, and excludes NATS.
- `scripts/deploy.py:206-239` implements `enforce_all_scaling(environment)` over the environment gateway, all shared agent apps, and SLIM.
- `scripts/deploy.py:242-254` preserves the legacy `enforce_scaling(app_name, environment)` shim.
- `scripts/deploy.py:661-666` runs scaling enforcement after all deploy-managed containers are updated.
- `tests/unit/test_deploy_scaling.py:45-59` scopes Terraform reconciliation to deploy-managed Terraform apps and explicitly omits NATS.
- `tests/unit/test_deploy_scaling.py:150-388` covers Terraform reconciliation, deployed-app coverage, command construction, failure handling, production/staging target selection, partial-failure continuation, and back-compat behavior.
- `wiki/Non-Disruptive-Upgrades.md:17-30` documents the per-container production topology with API gateway `min=2, max=8` and the correct `response-generator` `min=2, max=10`.
- `wiki/Non-Disruptive-Upgrades.md:111-120` now scopes the environment table to API gateway only and changes production from `2/10` to `2/8`.
- `wiki/Branching-and-Release-Strategy.md:97` states production API gateway scaling is `min=2, max=8` and WI-3171 enforces the full Decision #16 baseline.
- `wiki/Quality-Gates-and-CICD.md:203-208` scopes the table to API gateway scaling and uses production `min=2, max=8`.
- `infrastructure/terraform/main.tf:137-145` defines API gateway `min_replicas = 2`, `max_replicas = 8`.
- `infrastructure/terraform/main.tf:184-191` defines `response-generator` `min_replicas = 2`, `max_replicas = 10`, confirming the remaining grep hit is legitimate.

## Command Results

```
$ python -m pytest tests/unit/test_deploy_scaling.py -v -p no:cacheprovider --tb=short
11 passed in 0.20s
```

```
$ python -m pytest tests/unit/test_deploy_pipeline_production.py tests/performance/test_keda_scaling.py -v -p no:cacheprovider --tb=short
44 passed in 44.79s
```

```
$ rg -n "max.?=.?10|Production \| 2 \| 10|Production \| min=2, max=10|api-gateway.*max=10" wiki docs scripts/deploy -S
wiki\Non-Disruptive-Upgrades.md:24:| response-generator | AI agent: compose responses | min=2, max=10 | yes |
```

The only stale-deployment-doc pattern hit is not stale: it is the Terraform-backed `response-generator` max of 10.

## Findings

No blocking findings.

### Verified - Prior GO condition 5 is now satisfied

Claim: The stale production API gateway `2/10` documentation reference identified in `-004.md` has been corrected without creating a new ambiguity.

Evidence:

- `wiki/Non-Disruptive-Upgrades.md:111-120` now labels the table as API-gateway-only and lists production as `2 | 8`.
- `wiki/Non-Disruptive-Upgrades.md:113` points operators to the per-container topology table for the agent and infrastructure baselines enforced by WI-3171.
- The targeted stale-reference grep now finds only `wiki/Non-Disruptive-Upgrades.md:24`, the correct `response-generator` `min=2, max=10` row.
- `infrastructure/terraform/main.tf:189-190` confirms `response-generator` remains `min_replicas = 2`, `max_replicas = 10`.

Risk/impact: The deployment-doc ambiguity that blocked verification is closed. Operators now see API gateway `2/8` in all three deployment docs that were in GO condition 5 scope, while the per-app topology preserves the legitimate `response-generator` `2/10` baseline.

Required action: None.

## Non-Blocking Notes

- A broad wiki hygiene grep still reports `wiki/Scaling-Analysis.md:121` with `Knowledge retrieval max replicas | 10 | KEDA ScaledObject`. This is outside the deployment-doc scope of WI-3171 and was already flagged in `-005.md`; it may deserve a separate documentation-hygiene WI because Terraform now uses knowledge-retrieval max 6.
- Scaling failures remain warning-only by design. The tests capture that contract, but a future owner decision could tighten deploy behavior if scaling drift must become a blocking release gate.

## Decision Needed From Owner

None.

## Required Action Items

None. WI-3171 is verified from the bridge perspective.
