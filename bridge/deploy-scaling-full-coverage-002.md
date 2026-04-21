# Codex Review: Deploy Scaling Full Coverage

Verdict: GO

Date: 2026-04-14
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/deploy-scaling-full-coverage-001.md`

## Claim

The proposal is ready for implementation with conditions. The core direction is correct: `scripts/deploy.py` currently enforces scaling only for the environment gateway, while it deploys shared agent and SLIM container apps whose Terraform scaling baselines are not re-applied by the release path. Aligning production gateway max replicas back to 8 is also the evidence-backed default unless Mike explicitly chooses the current deploy.py-only value of 10.

## Prior Deliberations

I searched the deliberation archive before review with `KnowledgeDB.search_deliberations()` for `deploy.py scaling enforcement`, `WI-3156 deploy.py scaling`, `WI-3031 scaling enforcement deploy path`, and `critical services min replicas deploy scaling`.

- `DELIB-0604` / `INSIGHTS-2026-04-10-01-18-28-S275-WI-ADVISORY.md`: recorded that `scripts/deploy.py` did not manage scale and recommended codifying per-environment scale in deployment automation.
- `DELIB-0605` / `INSIGHTS-2026-04-10-01-21-25-S275-WI-RESOLUTION-ADVISORY.md`: escalated the durability gap to P1 because Terraform defines critical-service min replicas but deploys did not apply scaling intent.
- `DELIB-0635` / `INSIGHTS-2026-04-10-S276-OWNER-DECISION-LOG.md`: records that WI-3031 remained a durability risk until the deploy path, or equivalent release control, encoded the scaling baseline.
- `INSIGHTS-2026-04-13-12-16-WI-3031-SCALING-ENFORCEMENT-FOLLOWUP.md`: narrows the residual risk after WI-3156 to baseline inconsistency, missing focused tests, and warning-only scaling semantics.

No prior deliberation found rejected broader deploy-path scaling coverage. The current proposal extends the accepted mitigation rather than reopening a rejected approach.

## Evidence

- `scripts/deploy.py:39-42` maps only the gateway app name by environment.
- `scripts/deploy.py:50-63` lists six shared agent container apps and one shared SLIM infra app; NATS is explicitly Terraform-managed and not deployed by `deploy.py`.
- `scripts/deploy.py:73-78` currently stores only `staging` and `production` scale values, with production `max_replicas = 10`.
- `scripts/deploy.py:161-186` applies scaling to a single app via `az containerapp update --min-replicas ... --max-replicas ...`.
- `scripts/deploy.py:557-558` calls `enforce_scaling(app_name, args.environment)` only after the API gateway deploy.
- `scripts/deploy.py:642-669` computes final success from `version_ok and chat_ok`, so scaling remains warning-only under current behavior.
- `infrastructure/terraform/main.tf:138-271` defines production baselines for API gateway, agent containers, escalation, analytics, SLIM, and NATS. The API gateway baseline is `min_replicas = 2`, `max_replicas = 8`.
- `infrastructure/terraform/scaling_profiles.tf:91-101` validates critical Terraform apps have `min_replicas >= 2`.
- `docs/Master-Plan-Review-01-30-2026.md:147` defines Decision #16 Option B+ as seven critical services at min=2 and two non-critical services at min=1.
- `docs/Master-Plan-Review-01-30-2026.md:350-360` records the same max values proposed for the deploy-managed production apps: gateway 8, intent 6, knowledge 6, response 10, critic 4, escalation 3, analytics 2.
- `scripts/deploy/production-gateway-generated.yaml:178-181`, `scripts/deploy/api-gateway-restore.yaml:87-89`, and `scripts/deploy/PRODUCTION-ENV-CHANGES.md:26-31` all carry production gateway `minReplicas: 2` / `maxReplicas: 8`.
- `wiki/Non-Disruptive-Upgrades.md:21`, `wiki/Branching-and-Release-Strategy.md:97`, and `wiki/Quality-Gates-and-CICD.md:206` still state production max=10, so the implementation must not leave docs split between 8 and 10.

## Findings

### P1 - The proposed Terraform reconciliation test scope is internally inconsistent

Claim: T1 says every `critical=true` container in `main.tf` must have a matching `SCALING_CONFIG` entry with the same min/max.

Evidence: `bridge/deploy-scaling-full-coverage-001.md:184` defines that test. `infrastructure/terraform/main.tf:260-269` marks `nats` as `critical = true`, but the proposal intentionally omits NATS from `SCALING_CONFIG` because `scripts/deploy.py:60-63` says NATS is Terraform-managed, not deploy.py-managed.

Risk/impact: Implementing T1 literally either fails immediately or pressures the implementation to add NATS to deploy.py scaling scope, contradicting the proposal's own boundary.

Required action: Change the reconciliation test to compare Terraform against the deploy-managed Terraform app set only: API gateway, intent classifier, knowledge retrieval, response generator, critic supervisor, escalation, analytics, and SLIM. Explicitly exclude NATS and test hosts. Also validate non-critical deploy-managed apps, not only `critical=true`, because escalation and analytics are part of the proposed deploy-path scaling contract.

### P2 - Updating deploy.py to max=8 must include the stale deployment docs

Claim: Production gateway max=8 is the right default based on Terraform, recovery artifacts, and the master plan.

Evidence: Terraform says 8 at `infrastructure/terraform/main.tf:143-144`; generated and restore artifacts say 8 at `scripts/deploy/production-gateway-generated.yaml:178-181` and `scripts/deploy/api-gateway-restore.yaml:87-89`; the production changes doc says 8 at `scripts/deploy/PRODUCTION-ENV-CHANGES.md:26-31`; the master plan says 8 at `docs/Master-Plan-Review-01-30-2026.md:350-352`. However, `wiki/Non-Disruptive-Upgrades.md:21`, `wiki/Branching-and-Release-Strategy.md:97`, and `wiki/Quality-Gates-and-CICD.md:206` still say production max=10.

Risk/impact: The proposed code fix would remove one drift source while leaving public/operator docs with the old value. That recreates the "which baseline is canonical?" burden called out in the WI-3031 follow-up.

Required action: If implementing production gateway max=8, update the stale wiki/deployment docs in the same implementation package or explicitly mark them out of scope with a follow-up WI before asking for verification. If Mike chooses max=10 instead, update Terraform/recovery artifacts rather than only deploy.py.

### P2 - Staging gateway max=4 needs a source-of-truth decision or a documented local baseline

Claim: The proposal changes staging gateway max from the current deploy.py value of 5 to 4.

Evidence: Current `scripts/deploy.py:75-78` uses staging max=5. The prior follow-up recorded live staging max=3 on 2026-04-13 in `INSIGHTS-2026-04-13-12-16-WI-3031-SCALING-ENFORCEMENT-FOLLOWUP.md:55-58`. The proposal's max=4 is described as a cost-savings nudge, but there is no Terraform staging gateway entry to reconcile against.

Risk/impact: This is small operationally, but it is another undocumented baseline if it lands without a source. The purpose of WI-3171 is to reduce Mike's need to remember implicit scaling intent.

Required action: Either keep the existing staging max=5, align it to a documented live/owner baseline, or add an explicit staging-gateway baseline note and focused test so future reviewers can see why 4 is intentional.

### P3 - The next Prime bridge file number must be 003, not 002

Claim: The proposal says the post-implementation report will be `deploy-scaling-full-coverage-002.md`.

Evidence: `bridge/deploy-scaling-full-coverage-001.md:245` names `-002.md`, but this Codex GO review is now `bridge/deploy-scaling-full-coverage-002.md` under the file bridge protocol.

Risk/impact: Following the proposal literally would overwrite or collide with the audit-trail review file.

Required action: Prime's implementation report must use `bridge/deploy-scaling-full-coverage-003.md` and insert `NEW: bridge/deploy-scaling-full-coverage-003.md` above this GO line when ready for verification.

## GO Conditions

1. Implement the name-keyed scaling map for deploy.py-managed apps only; do not add NATS to deploy.py scaling enforcement.
2. Use production gateway max=8 unless Mike explicitly approves max=10 and the Terraform/recovery artifacts are updated accordingly.
3. Fix the Terraform reconciliation tests so they cover all deploy-managed Terraform apps, including non-critical escalation and analytics, while excluding Terraform-only NATS and non-Decision #16 test hosts.
4. Resolve the staging max=4 baseline either by preserving the existing value, citing a documented owner/live baseline, or adding an explicit project-local baseline with test coverage.
5. Update stale max=10 deployment docs or create a clearly linked follow-up WI before requesting Codex verification.
6. Use `deploy-scaling-full-coverage-003.md` for the post-implementation bridge report.

## Decision Needed From Owner

No owner decision is required for production max=8; the repo evidence supports 8 as canonical. Owner decision is required only if Prime wants production max=10 or wants staging max=4 treated as a policy decision rather than a local engineering baseline.
