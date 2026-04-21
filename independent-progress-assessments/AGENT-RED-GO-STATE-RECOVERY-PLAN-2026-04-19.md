# Agent Red GO-State Recovery Plan - 2026-04-19

## Session Context

- Role requested by owner: Prime Builder, bridge unavailable, working alone.
- Role-governance update: on 2026-04-20 the owner directed Loyal Opposition/Codex to assume the acting Prime Builder role while canonical Prime Builder is unavailable. Archived as `DELIB-0830` v1.
- Role-portability principle: Prime Builder and Loyal Opposition may be assumed by any capable AI harness assigned by the owner; that harness must enable the assigned role's skills, plugins, hooks, directives, and responsibilities to the extent possible. When the bridge is available, its counterpart is always Loyal Opposition.
- GT-KB installation role principle: GT-KB-installed projects must be fully configured for Prime Builder; if multiple capable harnesses are installed, configuration should be prepared for all harnesses so any owner-assigned harness may act as Prime Builder and the other bridge participant assumes Loyal Opposition.
- Current release recommendation: NO-GO.
- Plan objective: drive the Agent Red project to a defensible production GO state.
- File safety constraint: the owner has since provided broad approval to continue and make necessary changes. Preserve unrelated dirty worktree changes and avoid reverting files not touched for this recovery effort.
- Worktree condition at plan creation: dirty with unrelated tracked and untracked changes. Release work must avoid mixing remediation changes with unrelated artifacts.

## GO Definition

Agent Red reaches GO state only when all of the following are true:

1. No production secrets are present in tracked repository files or generated release artifacts.
2. All production startup paths fail closed when required secrets or externally visible URLs are missing.
3. Authentication, admin access, customer token, MFA, and recovery-token signing secrets are strong, explicit, and environment-specific.
4. Commercial launch-scope state is either durable and concurrency-safe or explicitly removed from production launch scope.
5. CI/security gates are green on the exact release candidate commit.
6. `main` and `develop` release provenance is reconciled and documented.
7. A clean Python 3.12 verification run exists for the final candidate.
8. GroundTruth-KB adopter governance is enforceable: adopter config, governance hooks/rules/skills, release-candidate gate, MemBase updates, and Deliberation Archive evidence are present and regression-tested.

## Status Legend

- BLOCKED: cannot proceed without owner approval, credential rotation, or external configuration.
- TODO: not started.
- IN PROGRESS: active in current session.
- DONE: completed and verified.
- DEFERRED: consciously out of launch scope with owner approval.

## Phase 0 - Release Freeze and Secret Containment

| ID | Status | Item | Required action | Evidence / Notes |
| --- | --- | --- | --- | --- |
| P0.1 | BLOCKED | Rotate leaked production credentials | Rotate every secret exposed in `scripts/deploy/production-gateway-generated.yaml` before any production release. | Plaintext values were observed for OpenAI, Cosmos, Stripe, Shopify, Zendesk, SMTP/Azure Communication, Redis, GitHub, and shared-service secrets. Values must not be reused. |
| P0.2 | DONE | Remove tracked secret manifest | Removed `scripts/deploy/production-gateway-generated.yaml` from the working tree and added ignore rules for generated production YAML. | Credential rotation/history handling remains P0.1. |
| P0.3 | DONE | Add full-repo secret scanning | Updated Security Scan Semgrep target from `src/` to repository-wide scanning with generated dependency/build output exclusions. | CI must still be rerun in GitHub. |
| P0.4 | DONE | Add generated artifact policy | `restore-production-gateway.ps1` now writes `_production-gateway-generated.local.yaml`, and `.gitignore` ignores generated production gateway YAML. | Prevents recurrence of committed generated production manifests. |

## Phase 1 - Fail-Closed Production Configuration

| ID | Status | Item | Required action | Evidence / Notes |
| --- | --- | --- | --- | --- |
| P1.1 | DONE | Standalone admin must not fail open | `standalone_auth.py` now denies passwordless admin access in staging/production, and startup config requires `ADMIN_PREVIEW_PASSWORD` and `ADMIN_SESSION_SECRET`. | Targeted auth tests pass. |
| P1.2 | DONE | Token/JWT secrets must be mandatory in production | Added startup guard requiring `MAGIC_LINK_JWT_SECRET`, `MFA_JWT_SECRET`, and `CUSTOMER_TOKEN_SECRET` in staging/production. | Static dev fallbacks remain usable only when deployed startup guard is not active. |
| P1.3 | DONE | Commerce base URL must be mandatory in production | Added startup guard requiring non-localhost `APP_BASE_URL` in staging/production. | Billing modules still default locally for development. |
| P1.4 | DONE | CORS must be explicit in production | Added startup guard requiring `APP_CORS_ORIGINS` in staging/production. | Restore template now includes the setting. |

## Phase 2 - CI and Security Gate Recovery

| ID | Status | Item | Required action | Evidence / Notes |
| --- | --- | --- | --- | --- |
| P2.1 | BLOCKED | Repair SonarCloud gate | External GitHub/Sonar configuration required: set valid `SONAR_TOKEN`, project key, and organization. | Latest `develop` SonarCloud runs fail because token/config is missing or invalid. |
| P2.2 | DONE | Repair Docker Scout security job | Added ACR login to `.github/workflows/security-scan.yml` using the existing repository pattern. | Requires `ACR_USERNAME` and `ACR_PASSWORD` secrets to be valid in GitHub. |
| P2.3 | DONE | Resolve dependency CVEs | Added `pyOpenSSL>=26.0.0` to `requirements.txt`. | `pip-audit -r requirements.txt` now reports no known vulnerabilities locally. |
| P2.4 | DONE | Fix blocking Ruff E/F error | Removed unused `pytest` import from `tests/unit/test_deploy_scaling.py`. | `ruff --select E,F` now passes. |
| P2.5 | DONE | Bandit triage | Fixed hardcoded temp path, marked intentional Container Apps health bind, and configured Bandit to skip low-confidence Cosmos B608 heuristic. | `bandit -r src/ -ll -c pyproject.toml` now passes. |

## Phase 3 - Commercial Durability

| ID | Status | Item | Required action | Evidence / Notes |
| --- | --- | --- | --- | --- |
| P3.1 | BLOCKED | Shopify subscription state durability | Decide whether Shopify billing is launch scope; if yes, replace in-memory tracking. | `shopify_billing.py` labels current tracking development-only. |
| P3.2 | BLOCKED | Stripe usage and pack durability | Decide whether paid usage/packs are launch scope; if yes, persist counters and balances. | `stripe_usage.py` and `stripe_packs.py` use in-memory state. |
| P3.3 | BLOCKED | Stripe webhook idempotency durability | Persist processed webhook IDs or use Stripe/event-store idempotency. | Current set resets on restart. |
| P3.4 | BLOCKED | Action executor audit durability | Persist pending actions and audit trail if production integrations can execute actions. | Current state is in memory. |

## Phase 4 - Release Provenance and Final Gate

| ID | Status | Item | Required action | Evidence / Notes |
| --- | --- | --- | --- | --- |
| P4.1 | TODO | Reconcile `main` and `develop` | Decide canonical release branch and merge/backport missing commits. | Branches are currently diverged. |
| P4.2 | TODO | Clean release worktree | Isolate release remediation branch from unrelated dirty files. | Current worktree contains many unrelated changes. |
| P4.3 | TODO | Python 3.12 verification environment | Run full test suite under target Python 3.12. | Local environment currently exposed Python 3.14, not 3.12. |
| P4.4 | IN PROGRESS | Final release-candidate evidence bundle | Capture commit SHA, workflow URLs, security scan results, deployment artifact provenance, DA/MemBase evidence, and release-gate results. | Local Python/security release-candidate gate passes under Python 3.14; exact-candidate GitHub/Python 3.12 proof still required. |

## Phase 5 - GroundTruth-KB Governance Adoption

| ID | Status | Item | Required action | Evidence / Notes |
| --- | --- | --- | --- | --- |
| P5.1 | DONE | Inventory GT-KB adopter assets | Confirm root adopter config, KnowledgeDB gate config, `.claude` hooks/rules/skills, and release-gate wiring. | `groundtruth.toml`, `tools/knowledge-db/groundtruth.toml`, `.claude/hooks`, `.claude/rules`, and `.claude/skills` inspected. |
| P5.2 | DONE | Add candidate work items to top of queue | Promote unimplemented candidate skill/plugin/doctor work above existing items. | Added `GTKB-GOV-001`, `GTKB-GOV-002`, and `GTKB-GOV-003` at the top of `memory/work_list.md`. |
| P5.3 | DONE | Make governance artifacts observable | Add regression test for adopter profile, gate plugin config, hook/rule/skill presence, gitignore visibility, release workflow lanes, and work-queue ordering. | Added `tests/scripts/test_groundtruth_governance_adoption.py`; focused run passed. |
| P5.4 | DONE | Add release-candidate skill | Add local operator skill for the non-deploying release gate and evidence requirements. | Added `.claude/skills/release-candidate-gate/SKILL.md`. |
| P5.5 | DONE | Wire adoption guard into production release gate | Ensure `scripts/release_candidate_gate.py` runs the governance adoption test. | `python scripts\release_candidate_gate.py --skip-frontend` passed locally with 147 targeted tests. |
| P5.6 | DONE | Enable upstream GT-KB managed skills | Install `gtkb-decision-capture`, `gtkb-bridge-propose`, and `gtkb-spec-intake` plus helpers. | Added missing `.claude/skills/*` managed skill files and updated governance adoption test. |
| P5.7 | DONE | Clarify acting Prime Builder skill label mapping | Make it explicit that `Prime Builder` / `prime-builder/...` in enabled skills maps to Codex while `DELIB-0830` is active. | Added `.claude/rules/acting-prime-builder.md` and regression coverage. |

## Current Session Work Log

| Time | Item | Result |
| --- | --- | --- |
| 2026-04-19 20:35 PDT | Created durable GO-state recovery plan | DONE. This file is the cross-session source of truth until superseded. |
| 2026-04-19 20:45 PDT | Created patch queue | DONE. See `independent-progress-assessments/AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md` for patch-ready remediation tracks and file-specific approval requirements. |
| 2026-04-19 20:49 PDT | Re-ran focused local gates | DONE. `ruff --select E,F` still fails on unused `pytest` in `tests/unit/test_deploy_scaling.py`; `pip-audit -r requirements.txt` still fails on `pyOpenSSL 25.3.0` CVE-2026-27448 and CVE-2026-27459. |
| 2026-04-19 20:50 PDT | Checked durability/tracking status | DONE. Plan files exist locally, but `independent-progress-assessments/*` is ignored by `.gitignore`; they are durable across local sessions but not git-tracked unless ignore policy is changed with approval. |
| 2026-04-19 20:56 PDT | Applied approved CI/security and fail-closed patch sets | DONE. Security Scan expanded, ACR login added, secret manifest removed, production config guard added, dependency CVEs resolved, Bandit configured, and targeted tests pass. |
| 2026-04-19 20:58 PDT | Made GO-state plan files trackable | DONE. `.gitignore` now re-includes `independent-progress-assessments/AGENT-RED-GO-STATE-*.md`; files are visible as untracked git changes. |
| 2026-04-19 21:28 PDT | Adopted enforceable GT-KB release governance layer | DONE. Added release-candidate skill, unignored governance hooks/rules/skills for source-control visibility, inserted top-priority GTKB-GOV work items, and added governance adoption regression tests. |
| 2026-04-19 21:36 PDT | Re-ran Python/security release candidate gate | DONE. `python scripts\release_candidate_gate.py --skip-frontend` passed: Ruff E/F, import cycles, Bandit, pip-audit, and 146 targeted tests. |
| 2026-04-19 21:42 PDT | Updated MemBase, KnowledgeDB, and Deliberation Archive | DONE. Updated `DOC-release-readiness-recovery` to v2, created `DOC-groundtruth-governance-adoption-2026-04-19` v1, and archived `DELIB-0829` v1. |
| 2026-04-19 21:50 PDT | Enabled missing GT-KB managed skills and clarified acting-Prime mapping | DONE. Installed three upstream managed skills, added acting-Prime local rule, and updated governance adoption regression coverage. Release gate passed with 147 targeted tests. |

## Approval Status

Owner has approved continuing the recovery work and making necessary changes. Continue to avoid unrelated edits and preserve pre-existing dirty worktree changes.

## Next Safe Actions

1. Rotate every exposed credential from the deleted generated production manifest and decide whether repository history needs secret purge.
2. Re-run GitHub Actions Security Scan and SonarCloud after secrets/config are repaired.
3. Reconcile `main` and `develop`, then create a clean release branch or candidate commit.
4. Run full Python 3.12 verification on the candidate commit.
5. Decide commercial durability launch scope for Shopify/Stripe/action-executor in-memory paths.
6. Complete or supersede the pending GT-KB Tier A apply thread and upstream the release-candidate/doctor candidates recorded as `GTKB-GOV-002` and `GTKB-GOV-003`.
