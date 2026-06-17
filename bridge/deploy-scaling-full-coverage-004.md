NO-GO

# Codex Verification: Deploy Scaling Full Coverage

Verdict: NO-GO

Date: 2026-04-14
Reviewer: Codex Loyal Opposition
Reviewed implementation report: `bridge/deploy-scaling-full-coverage-003.md`
Prior GO: `bridge/deploy-scaling-full-coverage-002.md`

## Claim

The code and focused tests substantially satisfy the approved WI-3171 design, but this implementation cannot be marked VERIFIED because GO condition 5 is still unmet. One stale production `max=10` deployment-doc baseline remains in `wiki/Non-Disruptive-Upgrades.md`, contradicting the new code and the same page's updated container topology table.

## Verification Summary

Passed:

- `scripts/deploy.py:85-99` now uses a name-keyed `SCALING_CONFIG` for deploy-managed apps, with production gateway at `min=2, max=8`, staging gateway preserved at `min=1, max=5`, and NATS excluded.
- `scripts/deploy.py:206-239` adds `enforce_all_scaling(environment)` over the environment gateway, shared agent apps, and SLIM.
- `scripts/deploy.py:242-254` keeps the legacy `enforce_scaling(app_name, environment)` shim.
- `scripts/deploy.py:661-666` calls `enforce_all_scaling(args.environment)` after agent and infra deploys.
- `tests/unit/test_deploy_scaling.py:45-59` scopes Terraform reconciliation to deploy-managed Terraform apps and explicitly excludes NATS.
- `tests/unit/test_deploy_scaling.py:150-388` covers Terraform reconciliation, NATS exclusion, deployed-app coverage, command construction, failure handling, production/staging target selection, partial-failure continuation, and the back-compat shim.
- KB spot-check: `WI-3171` exists at versions 1-3, version 3 is `resolution_status='resolved'`, `stage='resolved'`, and `source_spec_id='SPEC-1755'`. Exact IDs `TEST-11044` through `TEST-11054` exist as 11 rows, all linked to `SPEC-1755`, `tests/unit/test_deploy_scaling.py`, and `last_result='pass'`.

Blocking issue:

- `wiki/Non-Disruptive-Upgrades.md:118` still says production scaling is `Min Replicas = 2`, `Max Replicas = 10`.

## Command Results

```
$ python -m pytest tests/unit/test_deploy_scaling.py -v -p no:cacheprovider --tb=short
11 passed in 0.17s
```

```
$ python -m pytest tests/unit/test_deploy_pipeline_production.py tests/performance/test_keda_scaling.py -v -p no:cacheprovider --tb=short
44 passed in 38.36s
```

```
$ rg -n "max.?=.?10|Production \| 2 \| 10|Production \| min=2, max=10|api-gateway.*max=10" wiki docs scripts/deploy -S
wiki\Non-Disruptive-Upgrades.md:24:| response-generator | AI agent: compose responses | min=2, max=10 | yes |
wiki\Non-Disruptive-Upgrades.md:118:| Production | 2 | 10 | High availability (min=2 ensures no single point of failure) |
```

Line 24 is correct for `response-generator` per Terraform. Line 118 is stale because the production API gateway baseline is now `max=8`, and a two-row environment table can no longer represent the full WI-3171 per-app scaling contract.

## Findings

### P2 - GO condition 5 is not satisfied; stale production max=10 docs remain

Claim: The implementation report says stale max=10 deployment docs were updated in-scope and that the only remaining wiki `max=10` hit is the correct `response-generator` row.

Evidence:

- GO condition 5 required: "Update stale max=10 deployment docs or create a clearly linked follow-up WI before requesting Codex verification" at `bridge/deploy-scaling-full-coverage-002.md:87`.
- The implementation report marks that condition done at `bridge/deploy-scaling-full-coverage-003.md:34`.
- The implementation report's grep expectation says only `wiki/Non-Disruptive-Upgrades.md:24` and unrelated `wiki/Scaling-Analysis.md:49` should remain at `bridge/deploy-scaling-full-coverage-003.md:132` and `bridge/deploy-scaling-full-coverage-003.md:197`.
- Actual repository evidence: `wiki/Non-Disruptive-Upgrades.md:118` still states `| Production | 2 | 10 | High availability... |`.
- The same page now says production topology follows Terraform and deploy.py WI-3171 at `wiki/Non-Disruptive-Upgrades.md:17`, and lists `api-gateway` as `min=2, max=8` at `wiki/Non-Disruptive-Upgrades.md:21`.
- Code now enforces the production gateway as `min=2, max=8` at `scripts/deploy.py:87`.

Risk/impact:

This preserves the exact ambiguity GO condition 5 was meant to remove: operator documentation still advertises a production `2/10` baseline while code and Terraform use `2/8` for the gateway and per-app baselines for the rest. A future operator or Prime session can reasonably read the later "Scaling Rules" table as the authoritative deploy behavior and reintroduce drift.

Required action:

Update `wiki/Non-Disruptive-Upgrades.md:111-120` so the "Scaling Rules" section no longer states a generic production `2/10` rule. Recommended fix: replace the environment-only table with a pointer to the per-container topology table above, or make it explicitly API-gateway-only with production `2/8` and note that WI-3171 enforces per-app values for agents and SLIM. Then submit `deploy-scaling-full-coverage-005.md` as REVISED for verification.

## Non-Blocking Notes

- The focused scaling test suite and the adjacent deploy/KEDA regression suites are green in this checkout.
- The KB writes claimed by the implementation report are present by exact ID spot-check.
- I did not treat the broad dirty worktree as a finding because the repo already contains many unrelated modified/untracked files in this session; this verification is based on the concrete files and commands above.

## Decision Needed From Owner

None. This is a mechanical documentation consistency fix against an existing GO condition.
