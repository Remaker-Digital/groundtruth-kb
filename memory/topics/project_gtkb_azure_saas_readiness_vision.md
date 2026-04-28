---
name: GT-KB Azure Enterprise SaaS Readiness vision
description: Post-Phase-A strategic product direction from Codex assessment — elevate GT-KB from deployment scaffold to governed Azure production-readiness envelope
type: project
originSessionId: 766f6784-f0b0-408f-8071-867d2866ef86
---
**Source**: Codex Loyal Opposition strategic assessment, S298 (2026-04-17), shared by owner during scanner-safe-writer review window.

**Core thesis**: *GT-KB should not merely help developers start an Azure project. It should produce an Azure production-readiness envelope around the generated service.*

Current state: starter-level Azure support (Docker templates, Terraform provider stubs, CI templates, doctor checks, deployment placeholders). Useful for prototypes; not production-grade Azure SaaS factory.

**Why:** CTO evaluating GT-KB imminently (2026-04-17). Production-grade SaaS generation is the difference between "interesting dev tool" and "platform-scale product". Codex explicitly recommends elevating this to first-class GT-KB pillar: **Enterprise Azure SaaS Readiness**.

**How to apply (S299 Option C revision):** When post-Phase-A (v0.6.0) planning starts, draft BOTH scope bridges near-simultaneously as PARALLEL workstreams:

1. `gtkb-azure-enterprise-readiness-taxonomy-001` — taxonomy/readiness levels + verification plan ONLY; no Azure resource templates in this bridge (per Codex INSIGHTS-2026-04-17-05-13 first-bridge recommendation).
2. `gtkb-non-disruptive-upgrade-investigation-001` — investigation scope per `project_gtkb_non_disruptive_upgrade_priority.md`.

The 7-workstream structure below remains the long-term outline for Azure work, sequenced after taxonomy GO.

Do NOT interrupt current Tier A Phase A work. Tier A lands first (v0.6.0 milestone); then both scopes open concurrently. Recorded as DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL.

**15 deficiency areas identified by Codex:**

1. Azure Landing Zone Maturity (management groups, subscription strategy, policy inheritance, RBAC)
2. Production-Grade Multi-Tenant SaaS Architecture (pooled/siloed/hybrid tenant models)
3. Identity, Access, Enterprise SSO (Entra ID, OIDC/SAML, SCIM, conditional access)
4. Secrets & Credential Governance (Key Vault + managed identity, no static creds in CI)
5. Network & Security Perimeter (private endpoints, WAF, DDoS, egress control)
6. Compute Platform Decisioning (Container Apps vs AKS vs App Service vs Functions)
7. Data Architecture & Durability (tenant partitioning, backup/PITR, geo-replication, retention)
8. Reliability, SLOs & DR (availability targets, RTO/RPO, chaos testing, incident response)
9. Observability & Operations (Azure Monitor, Application Insights, per-tenant views)
10. CI/CD, IaC, Release Governance (OIDC federation, IaC validation, drift detection, rollback)
11. Compliance & Audit Evidence (SOC 2 controls, data boundaries, access reviews)
12. Enterprise Integration Surface (API Management, Event Grid, webhooks, private connectivity)
13. Cost, Capacity, Commercial Operations (unit economics, FinOps, tenant cost attribution)
14. Azure OpenAI / AI Workload Governance (model deployment, content safety, eval gates)
15. **Generate DECISIONS, not just files** — governed decision system, not scaffold

**7 proposed workstream stages (serialize by dependency):**

1. **Azure Readiness Taxonomy** — prototype / production / enterprise / regulated enterprise maturity model
2. **Azure Landing Zone & Environment Model** — subscription/environment/governance assumptions
3. **Azure Production Reference Architectures** — Container Apps, AKS, App Service, event-driven variants
4. **IaC & CI/CD Generation** — Bicep/Terraform modules, GitHub OIDC workflows
5. **Operational Readiness** — observability, SLOs, incident response, backup/restore, DR, runbooks
6. **Enterprise SaaS Tenancy** — isolation, onboarding, metering, support access, data residency, lifecycle
7. **Doctor/Verification Integration** — `gt project doctor` verifies Azure prereqs, config, policies, secrets, deployment health, operational evidence

**Sources cited by Codex:**
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Azure landing zones](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/)
- [Azure SaaS and multitenant architecture](https://learn.microsoft.com/azure/architecture/example-scenario/multi-saas/multitenant-saas)
- [Azure Container Apps managed identities](https://learn.microsoft.com/azure/container-apps/managed-identity)
- [Azure Container Apps Key Vault secret references](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets)

**When to revisit:** After Tier A Phase A (all 6 bridges VERIFIED) ships as GT-KB v0.6.0. Then draft taxonomy scope bridge (`gtkb-azure-enterprise-readiness-taxonomy-001`) in parallel with the non-disruptive upgrade investigation scope bridge. New Codex-supplied additive analysis at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-17-05-13-GTKB-AZURE-ENTERPRISE-SAAS-READINESS.md` provides P1/P2 findings + external Azure landing-zone anchors for the taxonomy bridge's content.
