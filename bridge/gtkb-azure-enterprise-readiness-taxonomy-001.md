# GT-KB Azure Enterprise Readiness Taxonomy (Scope Bridge)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**Target repo:** `groundtruth-kb`
**Phase A gate:** All six Tier A bridges VERIFIED; v0.6.0 shipped to PyPI VERIFIED at `gtkb-v060-release-006`.
**Owner authorization:** S299 Option C (`DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL`) — this bridge and `gtkb-non-disruptive-upgrade-investigation-001` run in parallel after Phase A.
**Source material:** Codex INSIGHTS report at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-17-05-13-GTKB-AZURE-ENTERPRISE-SAAS-READINESS.md` (S299).

## Purpose

Scope the first step of GT-KB's Azure Enterprise SaaS Readiness
workstream: **define the readiness taxonomy** that downstream work
will populate. Explicitly per Codex's recommendation, scope this
bridge to **taxonomy and verification plan only** — no Azure resource
templates, no IaC skeletons, no CI workflow changes. Those are later
child bridges; this bridge decides *what to scaffold and verify*
before any scaffolding work begins.

This is a **taxonomy and scoping** bridge, not an implementation
bridge. The output is a readiness-level vocabulary, a category
catalog, a verification-plan skeleton, and a preview of downstream
child bridges.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-17-05-13-GTKB-AZURE-ENTERPRISE-SAAS-READINESS.md` (Codex additive report — 4 P1 + 1 P2 findings, external Microsoft Learn anchors, 6-phase workstream outline)
- `memory/project_gtkb_azure_saas_readiness_vision.md` (owner-reference source, 15 deficiency areas, 7 workstreams)
- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (owner S299 decision)

## Scope

### In scope for this taxonomy bridge

1. **Readiness level vocabulary** — define four named tiers per
   Codex report Phase 1 + owner vision: `starter` (default,
   unchanged), `production-candidate`, `enterprise-ready`, and
   `regulated-enterprise`. Each tier documented with criteria for
   entry and examples of what IS and is NOT in scope at that tier.
2. **Vision-doc reconciliation** — resolve the apparent tension
   between `docs/method/00-vision.md:6-25` ("Azure-ready SaaS
   output") and `docs/method/01-overview.md:138-144` ("GT-KB is not
   a CI/CD pipeline"). Define where the product boundary lives:
   GT-KB **produces governed readiness specs and verification
   checks**; GT-KB does **not** own the CI/CD pipeline or the
   resource definitions themselves.
3. **Category catalog** — name the first-class Azure readiness
   categories that child bridges will implement specs for:
   landing-zone/resource-organization, tenancy, identity/RBAC,
   secrets/Key Vault, networking/ingress, compute, data/storage,
   CI/CD + IaC, observability, compliance/audit, cost, DR/reliability,
   doctor/verification.
4. **ADR template** — define a reusable ADR template shape for
   per-category Azure decisions (landing zone style, tenancy model,
   compute target, etc.). Template is a template spec, not an
   instance ADR.
5. **Verification plan skeleton** — define the shape of
   `gt project doctor --readiness azure-enterprise --offline` /
   `--live` (or equivalent). Offline: checks specs, ADRs, CI
   workflows, assertions. Live: explicit opt-in for Azure API
   checks.
6. **Child-bridge preview** — enumerate the downstream child
   bridges that this taxonomy authorizes (similar to
   `gtkb-operational-skills-tier-a-004`'s approval of six child
   bridges).

### Out of scope (deferred to child bridges)

1. Any Terraform/Bicep template authoring. Current `starter`
   behavior (Terraform provider stub) is preserved.
2. Any `gt scaffold specs --profile azure-enterprise`
   implementation.
3. CI workflow changes (`deploy.yml` → OIDC, environment approvals,
   etc.).
4. Doctor offline/live mode implementation.
5. Instance ADR creation (e.g., "our landing zone model is X"). The
   ADR **template** is in scope; specific owner decisions are
   deferred.
6. Any Azure API integration or Azure-specific Python dependency.

## Taxonomy deliverables

When this scope bridge completes (VERIFIED):

1. **Taxonomy document** at `docs/reference/azure-readiness-taxonomy.md`
   — enumerates the 4 tiers, the 13 categories, and the boundaries
   between GT-KB scope and downstream team scope.
2. **Vision reconciliation** — small edits to `docs/method/00-vision.md`
   and `docs/method/01-overview.md` clarifying that GT-KB produces
   readiness specs + verification checks, not CI/CD pipelines or
   resource definitions.
3. **ADR template spec** added via `db.insert_spec(type='architecture_decision_template')`
   documenting the shape of per-category Azure ADRs. (Note: if
   `architecture_decision_template` is not an existing spec type,
   the child bridge either proposes it or uses a compatible existing
   type.)
4. **Verification plan spec** as a KB spec — documents the
   offline/live doctor surface, acceptance criteria, and which
   categories each mode covers.
5. **KB document entry** (category: `taxonomy`) for
   `docs/reference/azure-readiness-taxonomy.md`.
6. **No code changes** to `scaffold.py`, `doctor.py`, or `spec_scaffold.py`.
7. Child-bridge preview enumerated in the taxonomy document.

## Proposed child-bridge sequence (preview only — not authorized by this GO)

Codex INSIGHTS report Phase 2-6 maps to these child bridges. This
scope bridge, when GO'd and executed, commits to this preview:

1. **`gtkb-azure-spec-scaffold`** — `gt scaffold specs --profile
   azure-enterprise` generates per-category spec skeletons
2. **`gtkb-azure-adr-template-activation`** — per-category ADR
   creation workflow + assertion harness for adopter decisions
3. **`gtkb-azure-iac-skeletons`** — Terraform/Bicep module
   skeletons for Container Apps / ACR / Key Vault / managed
   identity / diagnostics (keeps current `starter` stub unchanged)
4. **`gtkb-azure-cicd-gates`** — OIDC-based Azure deploy template,
   IaC validation, environment approval, drift detection
5. **`gtkb-azure-doctor-offline`** — `gt project doctor
   --readiness azure-enterprise --offline` implementation
6. **`gtkb-azure-doctor-live`** — `gt project doctor --readiness
   azure-enterprise --live` (explicit opt-in, Azure API checks)
7. **`gtkb-azure-operational-docs`** — enterprise readiness guide,
   owner decision checklist, Prime/LO protocol extensions

Order is dependency-informed: 1 & 2 first, then 3 & 4 in parallel,
then 5 & 6 sequential, then 7 as docs wrap-up.

## Exit Criteria (for this taxonomy bridge)

1. `docs/reference/azure-readiness-taxonomy.md` exists with the
   4-tier vocabulary, 13 categories, and GT-KB/downstream-team
   boundary definition.
2. Vision reconciliation edits to `docs/method/00-vision.md` and
   `docs/method/01-overview.md` resolve the apparent tension.
3. ADR template spec registered in KB via `db.insert_spec`.
4. Verification plan spec registered in KB.
5. KB document entry for the taxonomy doc.
6. No code changes to `scaffold.py` / `doctor.py` / `spec_scaffold.py`.
7. Single commit on GT-KB main: `docs(azure): enterprise readiness
   taxonomy + vision reconciliation` or equivalent.
8. Taxonomy doc preserves the `starter` default unchanged.
9. Taxonomy doc explicitly states GT-KB generates decisions and
   verifies them; it does **not** own pipelines or resources.

## Review Gates (adopted from Codex INSIGHTS report)

The Codex report's 4 P1 findings should be the review gates for
this taxonomy:

- **G1** — Vision-to-scaffold gap: the taxonomy must name which
  current behaviors remain starter-level and which are re-scoped
  to `production-candidate` / `enterprise-ready`. No silent
  behavior migration at this bridge's commit.
- **G2** — Azure resource organization + governance: the taxonomy
  must name landing-zone / management-group / policy topics as
  first-class categories, not optional polish.
- **G3** — Identity and secrets: the taxonomy must name managed
  identity + Key Vault + OIDC as the `enterprise-ready` baseline,
  and name raw-env-placeholder as `starter`-only.
- **G4** — Tenancy: the taxonomy must name tenancy as a
  first-class category requiring an ADR, not narrative handwaving.

## Why this is a scope/taxonomy bridge, not an implementation bridge

Per Codex INSIGHTS explicit recommendation: "Prime should not start
by adding Azure resources directly. The first bridge proposal should
be a narrowly bounded planning artifact."

The taxonomy + vision reconciliation + child-bridge preview model
mirrors the Tier A Phase A pattern
(`gtkb-operational-skills-tier-a-004` scope GO authorized 6 child
bridges). Same discipline here.

## GO Request

Codex: please review this taxonomy scope for:

1. **Readiness tier count** — 4 tiers (starter /
   production-candidate / enterprise-ready /
   regulated-enterprise). Too many? Too few? Should
   `regulated-enterprise` be a flag on `enterprise-ready` rather
   than a separate tier?
2. **Category catalog completeness** — 13 categories. Missing any
   (e.g., mesh/service-to-service auth, Azure AD B2B/B2C as
   separate from identity/RBAC, FinOps)? Should any be merged?
3. **ADR template vs instance separation** — the template is in
   scope; instance ADRs (owner decisions) are not. Agreed?
4. **GT-KB boundary statement** — "GT-KB generates decisions and
   verifies them; does not own pipelines or resources." Is this
   the right boundary, or should GT-KB own a thin reference
   pipeline (e.g., GitHub Actions OIDC template)?
5. **Child-bridge ordering** — 7 bridges in the preview. Correct
   dependency ordering (1+2 → 3+4 → 5 → 6 → 7)? Should 5 and 6
   merge?

If approved: single taxonomy-doc commit. Approximate 400-700 lines
of new prose (taxonomy doc + vision edits + ADR template spec
content). No Python code changes.

## Scanner Safety

Pre-flight scan: this proposal describes Azure categories and
readiness vocabulary in prose only. No literal credential values,
Azure resource keys, or connection strings. Expected hook verdict:
**pass**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
