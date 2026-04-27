NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 9

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md`
Scope: Production effects rehearsal lane proposal for `scripts/rehearse/_production_effects.py`

## Claim

Slice 9 is not ready to implement. The proposal claims to enumerate every production-affecting filesystem surface, but the source set omits core deployment surfaces and does not implement the required deploy-safety tags.

## Evidence

- The proposal claims the lane enumerates every production-affecting filesystem surface: `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md:31`.
- The proposal's inventory includes selected env, secret, approval, POR, deploy-bundle, `docker-compose.yml`, dashboard/report, and root governance surfaces, but does not list several live production/deployment surfaces present in this checkout: `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md:44` to `:101`.
- Live omitted root deployment surfaces include `.dockerignore`, `.shopifyignore`, `Dockerfile`, `Dockerfile.ui`, `Dockerfile.test`, and `shopify.app.toml`.
- Live omitted deployment scripts include `scripts/deploy.py`, `scripts/deploy_agent_containers.py`, `scripts/deploy_config.py`, `scripts/deploy_orchestrator.py`, `scripts/deploy_pipeline.py`, `scripts/deploy_ui.py`, plus `scripts/deploy/*.ps1` and deploy YAML/notes.
- Live omitted infrastructure surfaces include `infrastructure/terraform/*.tf`, `*.tfvars`, and Terraform state/lock files.
- The Phase 8 plan requires `production-effects-map.md` to list every code path or config value that assumes the legacy mixed root, specifically including hardcoded paths in deploy scripts, GitHub Actions working directories, Docker build contexts, secrets handling scripts, and scheduled tasks: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:197` to `:201`.
- The Phase 8 plan also requires every production-affecting rewrite to be tagged `deploy-blocking` or `deploy-safe-after-review`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:202` to `:204`. The proposal's disposition vocabulary is `MOVE`, `KEEP`, `DO_NOT_MOVE`, and `OWNER_DECISION_REQUIRED`: `bridge/gtkb-isolation-016-phase8-wave2-slice9-001.md:31` to `:36`.

## Risk / Impact

The proposed map would give a false sense that production-impacting migration paths are covered while missing the actual deployment scripts, image build inputs, Shopify app config, and Terraform infrastructure files that can break or mutate production behavior.

## Required Revision

- Expand the source inventory to include Dockerfiles, Docker ignore rules, Shopify app config, deploy scripts, `scripts/deploy/`, Terraform/infrastructure files, and relevant GitHub Actions working directories.
- Include hardcoded legacy-root assumptions found in deployment code/config, not just top-level artifacts.
- Add `deploy-blocking` / `deploy-safe-after-review` tags as first-class output fields alongside disposition.
- Add tests covering at least one omitted category from each group: Docker, Shopify, deploy scripts, Terraform, and GitHub Actions working directory assumptions.

## Decision Needed From Owner

None. The proposal must first meet the Phase 8 source-set and tagging requirements.
